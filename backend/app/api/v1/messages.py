"""
Messaging API Router - Phase 3.3
Direct messages and conversations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List
from datetime import datetime

from app.core.db import get_db
from app.models import User
from app.modelsx.social import Conversation, Message
from app.schemas.social_schemas import (
    ConversationResponse, ConversationCreate,
    MessageResponse, MessageCreate, MessageMarkReadRequest,
    ConversationWithMessages
)
from app.api.deps import get_current_user

# Phase 3.5: Real-time event emission
from app.services.realtime_events import on_message_created

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's conversations"""
    conversations = db.query(Conversation).filter(
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id
        ),
        Conversation.is_archived == False
    ).order_by(
        desc(Conversation.last_message_at)
    ).offset(skip).limit(limit).all()
    
    return conversations


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conv_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start new conversation with user"""
    if conv_data.participant2_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot start conversation with yourself")
    
    # Check if conversation already exists
    existing = db.query(Conversation).filter(
        or_(
            and_(
                Conversation.participant1_id == current_user.id,
                Conversation.participant2_id == conv_data.participant2_id
            ),
            and_(
                Conversation.participant1_id == conv_data.participant2_id,
                Conversation.participant2_id == current_user.id
            )
        )
    ).first()
    
    if existing:
        return existing
    
    new_conv = Conversation(
        participant1_id=current_user.id,
        participant2_id=conv_data.participant2_id
    )
    
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv


@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    conversation_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation with messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id
        )
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at
    ).offset(skip).limit(limit).all()
    
    conversation.messages = messages
    return conversation


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message(
    msg_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message in conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == msg_data.conversation_id,
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id
        )
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    new_message = Message(
        conversation_id=msg_data.conversation_id,
        sender_id=current_user.id,
        content=msg_data.content,
        attachment_url=msg_data.attachment_url
    )
    
    db.add(new_message)
    conversation.last_message_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    
    # Determine recipient (other participant in conversation)
    recipient_id = (
        conversation.participant2_id
        if conversation.participant1_id == current_user.id
        else conversation.participant1_id
    )
    
    # Emit real-time event
    await on_message_created(
        message_id=new_message.id,
        conversation_id=msg_data.conversation_id,
        sender_id=current_user.id,
        sender_name=current_user.name or current_user.email,
        recipient_id=recipient_id,
        content=msg_data.content,
        created_at=new_message.created_at
    )
    
    return new_message


@router.post("/messages/mark-read")
def mark_messages_read(
    request: MessageMarkReadRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark messages as read"""
    messages = db.query(Message).filter(
        Message.id.in_(request.message_ids),
        Message.sender_id != current_user.id
    ).all()
    
    for msg in messages:
        msg.is_read = True
        msg.read_at = datetime.utcnow()
    
    db.commit()
    return {"marked": len(messages)}


@router.patch("/conversations/{conversation_id}/archive", response_model=ConversationResponse)
def archive_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Archive conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        or_(
            Conversation.participant1_id == current_user.id,
            Conversation.participant2_id == current_user.id
        )
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.is_archived = True
    db.commit()
    db.refresh(conversation)
    return conversation


@router.delete("/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete own message"""
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message.sender_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot delete other user's messages")
    
    db.delete(message)
    db.commit()
