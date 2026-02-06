"""
Pydantic schemas for conversation-related API requests and responses.
These schemas define the structure of data flowing through the API.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator


class MessageBase(BaseModel):
    """Base message schema."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

    @validator("role")
    def validate_role(cls, v):
        """Validate message role."""
        if v not in ["user", "assistant", "system"]:
            raise ValueError("Role must be 'user', 'assistant', or 'system'")
        return v


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    pass


class MessageResponse(MessageBase):
    """Schema for message in API responses."""
    id: Optional[str] = Field(None, description="Message ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    conversation_id: Optional[str] = Field(None, description="Associated conversation ID")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "msg_123abc",
                "role": "assistant",
                "content": "Hello! How can I help you today?",
                "timestamp": "2024-01-15T10:30:00Z",
                "conversation_id": "conv_456def"
            }
        }


class ConversationBase(BaseModel):
    """Base conversation schema."""
    title: str = Field(
        default="New Chat",
        max_length=200,
        description="Conversation title"
    )


class ConversationCreate(ConversationBase):
    """Schema for creating a new conversation."""
    system_prompt: Optional[str] = Field(
        None,
        max_length=2000,
        description="Custom system prompt for this conversation"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Project Planning Discussion",
                "system_prompt": "You are a helpful project management assistant."
            }
        }


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="New conversation title"
    )
    system_prompt: Optional[str] = Field(
        None,
        max_length=2000,
        description="Updated system prompt"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Updated Project Planning"
            }
        }


class ConversationSummary(ConversationBase):
    """Schema for conversation summary (list view)."""
    id: str = Field(..., description="Conversation ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    message_count: int = Field(default=0, description="Number of messages in conversation")
    last_message_preview: Optional[str] = Field(
        None,
        max_length=100,
        description="Preview of the last message"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "conv_456def",
                "title": "Project Planning Discussion",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "message_count": 5,
                "last_message_preview": "Let me help you create a project timeline..."
            }
        }


class ConversationDetail(ConversationBase):
    """Schema for detailed conversation view."""
    id: str = Field(..., description="Conversation ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    messages: List[MessageResponse] = Field(default=[], description="Conversation messages")
    system_prompt: Optional[str] = Field(None, description="System prompt for this conversation")
    metadata: Optional[dict] = Field(default={}, description="Additional metadata")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "conv_456def",
                "title": "Project Planning Discussion",
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "messages": [
                    {
                        "id": "msg_123abc",
                        "role": "user",
                        "content": "Help me plan a project",
                        "timestamp": "2024-01-15T10:00:00Z"
                    }
                ],
                "system_prompt": "You are a helpful project management assistant.",
                "metadata": {}
            }
        }


class ChatRequest(BaseModel):
    """Schema for chat message request."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User message"
    )
    conversation_id: Optional[str] = Field(
        None,
        description="Existing conversation ID (creates new if not provided)"
    )
    system_prompt: Optional[str] = Field(
        None,
        max_length=2000,
        description="Custom system prompt override"
    )
    max_tokens: Optional[int] = Field(
        default=4096,
        ge=256,
        le=8192,
        description="Maximum tokens in response"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Response creativity (0.0-1.0)"
    )
    stream: Optional[bool] = Field(
        default=True,
        description="Enable streaming response"
    )

    @validator("message")
    def validate_message(cls, v):
        """Validate message content."""
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What are the best practices for API design?",
                "conversation_id": "conv_456def",
                "temperature": 0.7,
                "max_tokens": 4096,
                "stream": True
            }
        }


class ChatResponse(BaseModel):
    """Schema for chat response."""
    conversation_id: str = Field(..., description="Conversation ID")
    message: MessageResponse = Field(..., description="Assistant's response message")
    usage: Optional[dict] = Field(None, description="Token usage statistics")
    finish_reason: Optional[str] = Field(None, description="Reason for completion")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_456def",
                "message": {
                    "id": "msg_789ghi",
                    "role": "assistant",
                    "content": "Here are the best practices for API design...",
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                "usage": {
                    "prompt_tokens": 50,
                    "completion_tokens": 200,
                    "total_tokens": 250
                },
                "finish_reason": "stop"
            }
        }


class StreamChunk(BaseModel):
    """Schema for streaming response chunks."""
    type: str = Field(..., description="Chunk type: 'conversation_id', 'content', 'done', 'error'")
    id: Optional[str] = Field(None, description="Conversation ID (for conversation_id type)")
    text: Optional[str] = Field(None, description="Text content (for content type)")
    message: Optional[str] = Field(None, description="Error message (for error type)")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "content",
                "text": "Hello! "
            }
        }


class ConversationListResponse(BaseModel):
    """Schema for paginated conversation list."""
    conversations: List[ConversationSummary] = Field(
        default=[],
        description="List of conversations"
    )
    total: int = Field(default=0, description="Total number of conversations")
    page: int = Field(default=1, ge=1, description="Current page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")
    has_more: bool = Field(default=False, description="Whether more pages exist")

    class Config:
        json_schema_extra = {
            "example": {
                "conversations": [],
                "total": 42,
                "page": 1,
                "page_size": 20,
                "has_more": True
            }
        }


class DeleteResponse(BaseModel):
    """Schema for delete operation response."""
    message: str = Field(..., description="Success message")
    deleted_id: str = Field(..., description="ID of deleted resource")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Conversation deleted successfully",
                "deleted_id": "conv_456def"
            }
        }


class ClearResponse(BaseModel):
    """Schema for clear operation response."""
    message: str = Field(..., description="Success message")
    conversation_id: str = Field(..., description="Cleared conversation ID")
    cleared_count: int = Field(..., description="Number of messages cleared")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Conversation cleared successfully",
                "conversation_id": "conv_456def",
                "cleared_count": 10
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")
    request_id: Optional[str] = Field(None, description="Request ID for tracking")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "Invalid message format",
                "details": {
                    "field": "message",
                    "issue": "Message too long"
                },
                "request_id": "req_abc123"
            }
        }
