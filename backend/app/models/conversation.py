"""
SQLAlchemy database models for conversations and messages.
These models define the database schema and relationships.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


class Conversation(Base):
    """
    Conversation model representing a chat session.
    Stores conversation metadata and configuration.
    """

    __tablename__ = "conversations"

    # Primary key
    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        unique=True,
        nullable=False,
        index=True
    )

    # Basic fields
    title = Column(
        String(200),
        nullable=False,
        default="New Chat",
        index=True
    )

    # System configuration
    system_prompt = Column(
        Text,
        nullable=True,
        comment="Custom system prompt for this conversation"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True
    )

    # User association (for multi-user support)
    user_id = Column(
        String(36),
        nullable=True,
        index=True,
        comment="User ID if authentication is enabled"
    )

    # Metadata
    metadata = Column(
        JSON,
        nullable=True,
        default=dict,
        comment="Additional metadata as JSON"
    )

    # Soft delete
    is_deleted = Column(
        Integer,
        default=0,
        nullable=False,
        index=True,
        comment="Soft delete flag (0=active, 1=deleted)"
    )

    # Statistics
    message_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Cached message count for performance"
    )

    # AI configuration
    temperature = Column(
        String(10),
        nullable=True,
        default="0.7",
        comment="Temperature setting for this conversation"
    )

    max_tokens = Column(
        Integer,
        nullable=True,
        default=4096,
        comment="Max tokens setting for this conversation"
    )

    model_name = Column(
        String(100),
        nullable=True,
        comment="AI model used for this conversation"
    )

    # Relationships
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="Message.created_at"
    )

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_conversation_user_created', 'user_id', 'created_at'),
        Index('idx_conversation_updated', 'updated_at'),
        Index('idx_conversation_deleted', 'is_deleted', 'updated_at'),
    )

    def __repr__(self):
        return f"<Conversation(id='{self.id}', title='{self.title}', messages={len(self.messages)})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "system_prompt": self.system_prompt,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "user_id": self.user_id,
            "metadata": self.metadata,
            "message_count": self.message_count,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "model_name": self.model_name,
        }

    def to_summary_dict(self):
        """Convert model to summary dictionary (for list views)."""
        last_message = None
        if self.messages:
            last_message = self.messages[-1].content[:100] if len(self.messages[-1].content) > 100 else self.messages[-1].content

        return {
            "id": self.id,
            "title": self.title,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "message_count": self.message_count,
            "last_message_preview": last_message,
        }


class Message(Base):
    """
    Message model representing individual messages in a conversation.
    Stores message content, metadata, and associations.
    """

    __tablename__ = "messages"

    # Primary key
    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        unique=True,
        nullable=False,
        index=True
    )

    # Foreign key to conversation
    conversation_id = Column(
        String(36),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Message fields
    role = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Message role: user, assistant, or system"
    )

    content = Column(
        Text,
        nullable=False,
        comment="Message content"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )

    # Metadata
    metadata = Column(
        JSON,
        nullable=True,
        default=dict,
        comment="Additional metadata as JSON"
    )

    # Token usage tracking
    prompt_tokens = Column(
        Integer,
        nullable=True,
        comment="Number of prompt tokens used"
    )

    completion_tokens = Column(
        Integer,
        nullable=True,
        comment="Number of completion tokens used"
    )

    total_tokens = Column(
        Integer,
        nullable=True,
        comment="Total tokens used"
    )

    # AI response metadata
    model_name = Column(
        String(100),
        nullable=True,
        comment="AI model that generated this message"
    )

    finish_reason = Column(
        String(50),
        nullable=True,
        comment="Reason for completion (stop, length, etc.)"
    )

    # Processing time
    processing_time_ms = Column(
        Integer,
        nullable=True,
        comment="Time taken to generate response in milliseconds"
    )

    # Relationships
    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_message_conversation_created', 'conversation_id', 'created_at'),
        Index('idx_message_role', 'role'),
    )

    def __repr__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id='{self.id}', role='{self.role}', content='{content_preview}')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.metadata,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "model_name": self.model_name,
            "finish_reason": self.finish_reason,
            "processing_time_ms": self.processing_time_ms,
        }


class User(Base):
    """
    User model for authentication and authorization.
    Optional - only needed if implementing user management.
    """

    __tablename__ = "users"

    # Primary key
    id = Column(
        String(36),
        primary_key=True,
        default=generate_uuid,
        unique=True,
        nullable=False,
        index=True
    )

    # User credentials
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    username = Column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    # Profile
    full_name = Column(
        String(200),
        nullable=True
    )

    # Status
    is_active = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Account active status (0=inactive, 1=active)"
    )

    is_verified = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Email verification status (0=unverified, 1=verified)"
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    last_login = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # API Keys
    api_key_hash = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="Hashed API key for programmatic access"
    )

    # Metadata
    metadata = Column(
        JSON,
        nullable=True,
        default=dict
    )

    # Indexes
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
    )

    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"

    def to_dict(self):
        """Convert model to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "is_active": bool(self.is_active),
            "is_verified": bool(self.is_verified),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
