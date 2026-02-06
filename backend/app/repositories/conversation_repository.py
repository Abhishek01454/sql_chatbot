"""
Conversation repository for specialized conversation and message operations.
Extends BaseRepository with domain-specific methods.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Conversation, Message
from app.repositories.base import BaseRepository
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ConversationRepository(BaseRepository[Conversation]):
    """Repository for conversation-related database operations."""

    def __init__(self):
        super().__init__(Conversation)

    async def get_with_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
        include_deleted: bool = False
    ) -> Optional[Conversation]:
        """
        Get a conversation with all its messages loaded.

        Args:
            db: Database session
            conversation_id: Conversation ID
            include_deleted: Whether to include soft-deleted conversations

        Returns:
            Conversation instance with messages or None
        """
        stmt = select(Conversation).where(Conversation.id == conversation_id)

        if not include_deleted:
            stmt = stmt.where(Conversation.is_deleted == 0)

        stmt = stmt.options(selectinload(Conversation.messages))

        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 20,
        include_deleted: bool = False
    ) -> List[Conversation]:
        """
        Get all conversations for a specific user.

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records
            include_deleted: Whether to include soft-deleted conversations

        Returns:
            List of conversations
        """
        stmt = select(Conversation).where(Conversation.user_id == user_id)

        if not include_deleted:
            stmt = stmt.where(Conversation.is_deleted == 0)

        stmt = stmt.order_by(desc(Conversation.updated_at))
        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_recent_conversations(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None,
        days: int = 7,
        limit: int = 20
    ) -> List[Conversation]:
        """
        Get recent conversations within specified days.

        Args:
            db: Database session
            user_id: Optional user ID filter
            days: Number of days to look back
            limit: Maximum number of conversations

        Returns:
            List of recent conversations
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        stmt = select(Conversation).where(
            and_(
                Conversation.updated_at >= cutoff_date,
                Conversation.is_deleted == 0
            )
        )

        if user_id:
            stmt = stmt.where(Conversation.user_id == user_id)

        stmt = stmt.order_by(desc(Conversation.updated_at)).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def search_conversations(
        self,
        db: AsyncSession,
        query: str,
        user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Conversation]:
        """
        Search conversations by title or content.

        Args:
            db: Database session
            query: Search query string
            user_id: Optional user ID filter
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of matching conversations
        """
        search_pattern = f"%{query}%"
        stmt = select(Conversation).where(
            and_(
                Conversation.title.ilike(search_pattern),
                Conversation.is_deleted == 0
            )
        )

        if user_id:
            stmt = stmt.where(Conversation.user_id == user_id)

        stmt = stmt.order_by(desc(Conversation.updated_at))
        stmt = stmt.offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def update_message_count(
        self,
        db: AsyncSession,
        conversation_id: str,
        commit: bool = True
    ) -> Optional[Conversation]:
        """
        Update the cached message count for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            commit: Whether to commit immediately

        Returns:
            Updated conversation or None
        """
        conversation = await self.get_by_id(db, conversation_id)
        if not conversation:
            return None

        # Count messages
        stmt = select(func.count()).select_from(Message).where(
            Message.conversation_id == conversation_id
        )
        result = await db.execute(stmt)
        count = result.scalar()

        conversation.message_count = count
        conversation.updated_at = datetime.utcnow()

        if commit:
            await db.commit()
            await db.refresh(conversation)

        return conversation

    async def clear_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
        commit: bool = True
    ) -> int:
        """
        Delete all messages in a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            commit: Whether to commit immediately

        Returns:
            Number of messages deleted
        """
        from sqlalchemy import delete

        stmt = delete(Message).where(Message.conversation_id == conversation_id)
        result = await db.execute(stmt)

        # Update conversation
        conversation = await self.get_by_id(db, conversation_id)
        if conversation:
            conversation.message_count = 0
            conversation.updated_at = datetime.utcnow()

        if commit:
            await db.commit()

        logger.info(f"Cleared {result.rowcount} messages from conversation {conversation_id}")
        return result.rowcount

    async def get_conversation_stats(
        self,
        db: AsyncSession,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get statistics about conversations.

        Args:
            db: Database session
            user_id: Optional user ID filter

        Returns:
            Dictionary with statistics
        """
        # Total conversations
        total_stmt = select(func.count()).select_from(Conversation).where(
            Conversation.is_deleted == 0
        )
        if user_id:
            total_stmt = total_stmt.where(Conversation.user_id == user_id)

        total_result = await db.execute(total_stmt)
        total_conversations = total_result.scalar()

        # Total messages
        message_stmt = select(func.count()).select_from(Message)
        if user_id:
            message_stmt = message_stmt.join(Conversation).where(
                Conversation.user_id == user_id
            )

        message_result = await db.execute(message_stmt)
        total_messages = message_result.scalar()

        # Recent conversations (last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_stmt = select(func.count()).select_from(Conversation).where(
            and_(
                Conversation.updated_at >= cutoff_date,
                Conversation.is_deleted == 0
            )
        )
        if user_id:
            recent_stmt = recent_stmt.where(Conversation.user_id == user_id)

        recent_result = await db.execute(recent_stmt)
        recent_conversations = recent_result.scalar()

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "recent_conversations": recent_conversations,
            "avg_messages_per_conversation": total_messages / total_conversations if total_conversations > 0 else 0
        }


class MessageRepository(BaseRepository[Message]):
    """Repository for message-related database operations."""

    def __init__(self):
        super().__init__(Message)

    async def get_by_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """
        Get all messages for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of messages
        """
        stmt = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at).offset(skip).limit(limit)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_last_n_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
        n: int = 10
    ) -> List[Message]:
        """
        Get the last N messages from a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            n: Number of messages to retrieve

        Returns:
            List of messages (most recent last)
        """
        stmt = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(desc(Message.created_at)).limit(n)

        result = await db.execute(stmt)
        messages = result.scalars().all()

        # Reverse to get chronological order
        return list(reversed(messages))

    async def create_message(
        self,
        db: AsyncSession,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        model_name: Optional[str] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        total_tokens: Optional[int] = None,
        finish_reason: Optional[str] = None,
        processing_time_ms: Optional[int] = None,
        commit: bool = True
    ) -> Message:
        """
        Create a new message with all fields.

        Args:
            db: Database session
            conversation_id: Conversation ID
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Additional metadata
            model_name: AI model name
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            total_tokens: Total tokens used
            finish_reason: Completion reason
            processing_time_ms: Processing time in milliseconds
            commit: Whether to commit immediately

        Returns:
            Created message instance
        """
        message_data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "model_name": model_name,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "finish_reason": finish_reason,
            "processing_time_ms": processing_time_ms,
        }

        message = await self.create(db, message_data, commit=False)

        # Update conversation's updated_at and message_count
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.updated_at = datetime.utcnow()
            conversation.message_count = conversation.message_count + 1

        if commit:
            await db.commit()
            await db.refresh(message)

        logger.debug(f"Created message in conversation {conversation_id}")
        return message

    async def get_messages_by_role(
        self,
        db: AsyncSession,
        conversation_id: str,
        role: str
    ) -> List[Message]:
        """
        Get all messages with a specific role.

        Args:
            db: Database session
            conversation_id: Conversation ID
            role: Message role to filter by

        Returns:
            List of messages
        """
        stmt = select(Message).where(
            and_(
                Message.conversation_id == conversation_id,
                Message.role == role
            )
        ).order_by(Message.created_at)

        result = await db.execute(stmt)
        return result.scalars().all()

    async def get_token_usage(
        self,
        db: AsyncSession,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get total token usage statistics.

        Args:
            db: Database session
            conversation_id: Optional conversation ID filter
            user_id: Optional user ID filter

        Returns:
            Dictionary with token usage stats
        """
        stmt = select(
            func.sum(Message.prompt_tokens),
            func.sum(Message.completion_tokens),
            func.sum(Message.total_tokens)
        )

        if conversation_id:
            stmt = stmt.where(Message.conversation_id == conversation_id)
        elif user_id:
            stmt = stmt.join(Conversation).where(Conversation.user_id == user_id)

        result = await db.execute(stmt)
        prompt_tokens, completion_tokens, total_tokens = result.one()

        return {
            "prompt_tokens": prompt_tokens or 0,
            "completion_tokens": completion_tokens or 0,
            "total_tokens": total_tokens or 0
        }
