from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime
import uuid
import httpx

load_dotenv()

app = FastAPI(title="Mistral AI Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mistral API configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# In-memory conversation storage (use Redis/DB for production)
conversations = {}


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    system_prompt: Optional[str] = "You are a helpful AI assistant. You are knowledgeable, helpful, and provide accurate, well-structured responses. You can help with coding, writing, analysis, math, and general questions."
    max_tokens: Optional[int] = 4096
    temperature: Optional[float] = 0.7


class ConversationCreate(BaseModel):
    title: Optional[str] = "New Chat"


class ConversationUpdate(BaseModel):
    title: str


@app.get("/")
async def root():
    return {"message": "Mistral AI Chatbot API is running"}


@app.get("/conversations")
async def get_conversations():
    """Get all conversations"""
    conv_list = []
    for conv_id, conv_data in conversations.items():
        conv_list.append({
            "id": conv_id,
            "title": conv_data.get("title", "New Chat"),
            "created_at": conv_data.get("created_at"),
            "updated_at": conv_data.get("updated_at"),
            "message_count": len(conv_data.get("messages", []))
        })
    # Sort by updated_at descending
    conv_list.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return conv_list


@app.post("/conversations")
async def create_conversation(data: ConversationCreate):
    """Create a new conversation"""
    conv_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    conversations[conv_id] = {
        "title": data.title,
        "messages": [],
        "created_at": now,
        "updated_at": now
    }
    return {"id": conv_id, "title": data.title, "created_at": now}


@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation with messages"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {
        "id": conversation_id,
        **conversations[conversation_id]
    }


@app.put("/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, data: ConversationUpdate):
    """Update conversation title"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversations[conversation_id]["title"] = data.title
    conversations[conversation_id]["updated_at"] = datetime.utcnow().isoformat()
    return {"id": conversation_id, "title": data.title}


@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    del conversations[conversation_id]
    return {"message": "Conversation deleted"}


@app.post("/chat")
async def chat(request: ChatRequest):
    """Send a message and get a response"""
    if not MISTRAL_API_KEY:
        raise HTTPException(status_code=500, detail="MISTRAL_API_KEY not configured")

    try:
        # Create or get conversation
        if request.conversation_id and request.conversation_id in conversations:
            conv_id = request.conversation_id
        else:
            conv_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            # Generate title from first message
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversations[conv_id] = {
                "title": title,
                "messages": [],
                "created_at": now,
                "updated_at": now
            }

        # Add user message
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat()
        }
        conversations[conv_id]["messages"].append(user_message)

        # Prepare messages for Mistral
        messages = [{"role": "system", "content": request.system_prompt}]
        messages.extend([
            {"role": msg["role"], "content": msg["content"]}
            for msg in conversations[conv_id]["messages"]
        ])

        # Call Mistral API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                MISTRAL_API_URL,
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistral-small-latest",
                    "messages": messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens
                }
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            response_data = response.json()
            assistant_content = response_data["choices"][0]["message"]["content"]

        # Add assistant message
        assistant_message = {
            "role": "assistant",
            "content": assistant_content,
            "timestamp": datetime.utcnow().isoformat()
        }
        conversations[conv_id]["messages"].append(assistant_message)
        conversations[conv_id]["updated_at"] = datetime.utcnow().isoformat()

        return {
            "conversation_id": conv_id,
            "message": assistant_message,
            "usage": response_data.get("usage", {})
        }

    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Send a message and get a streaming response"""
    if not MISTRAL_API_KEY:
        raise HTTPException(status_code=500, detail="MISTRAL_API_KEY not configured")

    try:
        # Create or get conversation
        if request.conversation_id and request.conversation_id in conversations:
            conv_id = request.conversation_id
        else:
            conv_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversations[conv_id] = {
                "title": title,
                "messages": [],
                "created_at": now,
                "updated_at": now
            }

        # Add user message
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat()
        }
        conversations[conv_id]["messages"].append(user_message)

        # Prepare messages for Mistral
        messages = [{"role": "system", "content": request.system_prompt}]
        messages.extend([
            {"role": msg["role"], "content": msg["content"]}
            for msg in conversations[conv_id]["messages"]
        ])

        async def generate():
            full_response = ""
            try:
                # Send conversation ID first
                yield f"data: {json.dumps({'type': 'conversation_id', 'id': conv_id})}\n\n"

                async with httpx.AsyncClient(timeout=120.0) as client:
                    async with client.stream(
                        "POST",
                        MISTRAL_API_URL,
                        headers={
                            "Authorization": f"Bearer {MISTRAL_API_KEY}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "mistral-small-latest",
                            "messages": messages,
                            "temperature": request.temperature,
                            "max_tokens": request.max_tokens,
                            "stream": True
                        }
                    ) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            yield f"data: {json.dumps({'type': 'error', 'message': error_text.decode()})}\n\n"
                            return

                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str.strip() == "[DONE]":
                                    break

                                try:
                                    data = json.loads(data_str)
                                    if "choices" in data and len(data["choices"]) > 0:
                                        delta = data["choices"][0].get("delta", {})
                                        if "content" in delta:
                                            text = delta["content"]
                                            full_response += text
                                            yield f"data: {json.dumps({'type': 'content', 'text': text})}\n\n"
                                except json.JSONDecodeError:
                                    continue

                # Save assistant message
                assistant_message = {
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.utcnow().isoformat()
                }
                conversations[conv_id]["messages"].append(assistant_message)
                conversations[conv_id]["updated_at"] = datetime.utcnow().isoformat()
                yield f"data: {json.dumps({'type': 'done'})}\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversations/{conversation_id}/clear")
async def clear_conversation(conversation_id: str):
    """Clear messages in a conversation"""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conversations[conversation_id]["messages"] = []
    conversations[conversation_id]["updated_at"] = datetime.utcnow().isoformat()
    return {"message": "Conversation cleared"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
