"""
Phase 2.3 API Endpoints
=======================

6 routers implementing 28 endpoints for Phase 2.3 features:
- Mentor Verification (6 endpoints)
- Analytics (6 endpoints)
- Payments (4 endpoints)
- Video Sessions (4 endpoints)
- Messaging (4 endpoints)
- Forum (6 endpoints + advanced)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.db import get_db
from app.core.security import get_current_user
from app.models import User
from app.modelsx.phase_2_3_models import (
    MentorVerificationDocument,
    AnalyticsMetric,
    MentorAnalyticsSummary,
    SessionPayment,
    VideoSession,
    SessionRecording,
    SessionChatMessage,
)
from app.modelsx.social import Message, Conversation
from app.modelsx.payout import MentorPayout
from app.modelsx.forums import ForumCategory, ForumThread, ForumReply

# Alias for backward compatibility
ForumTopic = ForumCategory
from app.schemas.phase_2_3_schemas import (
    DocumentResponse,
    AnalyticsSummaryResponse,
    PaymentResponse,
    VideoSessionResponse,
    ChatMessageResponse,
    MessageResponse,
    ForumThreadResponse,
    ForumReplyResponse,
)

# ============================================================
# ROUTER 1: MENTOR VERIFICATION
# ============================================================
verification_router = APIRouter(prefix="/verification", tags=["verification"])


@verification_router.post("/documents/upload", response_model=DocumentResponse)
async def upload_verification_document(
    document_type: str,
    document_url: str,
    file_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Upload verification document"""
    # Check if user is mentor
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    # Create document
    doc = MentorVerificationDocument(
        mentor_id=mentor.id,
        document_type=document_type,
        document_url=document_url,
        file_name=file_name,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@verification_router.get("/documents", response_model=list[DocumentResponse])
async def list_verification_documents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List verification documents for current mentor"""
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    documents = db.query(MentorVerificationDocument).filter_by(mentor_id=mentor.id).all()
    return documents


@verification_router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_verification_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get verification document details"""
    doc = db.query(MentorVerificationDocument).filter_by(id=doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check authorization
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if doc.mentor_id != mentor.id and user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return doc


@verification_router.delete("/documents/{doc_id}")
async def delete_verification_document(
    doc_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete verification document"""
    doc = db.query(MentorVerificationDocument).filter_by(id=doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check authorization
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if doc.mentor_id != mentor.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(doc)
    db.commit()
    return {"status": "deleted"}


@verification_router.get("/status")
async def get_verification_status(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get current verification status"""
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    documents = db.query(MentorVerificationDocument).filter_by(mentor_id=mentor.id).all()
    
    return {
        "mentor_id": mentor.id,
        "documents_count": len(documents),
        "approved": sum(1 for d in documents if d.status == "APPROVED"),
        "pending": sum(1 for d in documents if d.status == "PENDING"),
        "rejected": sum(1 for d in documents if d.status == "REJECTED"),
    }


# ============================================================
# ROUTER 2: ANALYTICS
# ============================================================
analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])


@analytics_router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get analytics summary for current mentor"""
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    summary = db.query(MentorAnalyticsSummary).filter_by(mentor_id=mentor.id).first()
    if not summary:
        # Create new summary
        summary = MentorAnalyticsSummary(mentor_id=mentor.id)
        db.add(summary)
        db.commit()
        db.refresh(summary)
    
    return summary


@analytics_router.get("/metrics")
async def get_analytics_metrics(
    period: str = "monthly",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get detailed metrics for current mentor"""
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    metrics = db.query(AnalyticsMetric).filter_by(
        mentor_id=mentor.id,
        period=period
    ).all()
    
    return {"period": period, "metrics": metrics}


@analytics_router.post("/track")
async def track_metric(
    metric_type: str,
    metric_value: float,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Track a new metric (admin only)"""
    if user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    metric = AnalyticsMetric(
        mentor_id=user.id,
        metric_type=metric_type,
        metric_value=metric_value,
    )
    db.add(metric)
    db.commit()
    return {"id": metric.id, "status": "tracked"}


@analytics_router.get("/revenue")
async def get_revenue_analytics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get revenue analytics for current mentor"""
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    total_earned = db.query("session_payments").filter(
        and_(
            "mentor_id" == mentor.id,
            "status" == "COMPLETED"
        )
    ).sum("amount")
    
    return {
        "mentor_id": mentor.id,
        "total_earned": total_earned or 0.0,
        "currency": "USD",
    }


@analytics_router.get("/engagement")
async def get_engagement_analytics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get engagement metrics for current mentor"""
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    summary = db.query(MentorAnalyticsSummary).filter_by(mentor_id=mentor.id).first()
    
    return {
        "total_sessions": summary.total_sessions if summary else 0,
        "student_count": summary.student_count if summary else 0,
        "completion_rate": summary.completion_rate if summary else 0.0,
        "average_rating": summary.average_rating if summary else 0.0,
    }


# ============================================================
# ROUTER 3: PAYMENTS
# ============================================================
payments_router = APIRouter(prefix="/payments", tags=["payments"])


@payments_router.post("/process", response_model=PaymentResponse)
async def process_payment(
    session_id: int,
    amount: float,
    payment_method: str = "card",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Process payment for session"""
    # Create payment record
    payment = SessionPayment(
        session_id=session_id,
        user_id=user.id,
        mentor_id=0,  # Will be set from session
        amount=amount,
        payment_method=payment_method,
        status="PENDING",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    
    return payment


@payments_router.get("/history", response_model=list[PaymentResponse])
async def get_payment_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get payment history for current user"""
    payments = db.query(SessionPayment).filter_by(user_id=user.id).offset(skip).limit(limit).all()
    return payments


@payments_router.post("/refund/{payment_id}")
async def refund_payment(
    payment_id: int,
    reason: str = "",
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Request refund for payment"""
    payment = db.query(SessionPayment).filter_by(id=payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # Check authorization
    if payment.user_id != user.id and user.role not in ["ADMIN", "SUPERADMIN"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    payment.status = "REFUNDED"
    db.commit()
    
    return {"status": "refunded", "payment_id": payment_id}


@payments_router.get("/balance")
async def get_payment_balance(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get current balance (for mentors)"""
    mentor = db.query("mentors").filter_by(user_id=user.id).first()
    if not mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    return {
        "mentor_id": mentor.id,
        "total_earned": 0.0,
        "total_paid": 0.0,
        "available_balance": 0.0,
        "currency": "USD",
    }


# ============================================================
# ROUTER 4: VIDEO SESSIONS
# ============================================================
video_router = APIRouter(prefix="/video", tags=["video"])


@video_router.post("/session/create", response_model=VideoSessionResponse)
async def create_video_session(
    mentor_session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create video session"""
    video = VideoSession(
        mentor_session_id=mentor_session_id,
        room_id=f"room_{mentor_session_id}_{int(datetime.utcnow().timestamp())}",
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video


@video_router.get("/session/{session_id}", response_model=VideoSessionResponse)
async def get_video_session(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get video session details"""
    video = db.query(VideoSession).filter_by(id=session_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video session not found")
    return video


@video_router.put("/session/{session_id}")
async def update_video_session(
    session_id: int,
    status: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update video session status"""
    video = db.query(VideoSession).filter_by(id=session_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video session not found")
    
    video.status = status
    if status == "ACTIVE":
        video.start_time = datetime.utcnow()
    elif status == "COMPLETED":
        video.end_time = datetime.utcnow()
    
    db.commit()
    return {"status": "updated"}


@video_router.get("/recording/{session_id}")
async def get_session_recording(
    session_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get recording for video session"""
    recording = db.query(SessionRecording).filter(
        SessionRecording.video_session_id == session_id
    ).first()
    
    if not recording:
        return {"status": "no recording"}
    
    return {
        "id": recording.id,
        "url": recording.recording_url,
        "duration": recording.duration_seconds,
    }


# ============================================================
# ROUTER 5: MESSAGING
# ============================================================
messaging_router = APIRouter(prefix="/messaging", tags=["messaging"])


@messaging_router.post("/message/send")
async def send_message(
    recipient_id: int,
    message: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send direct message to user"""
    msg = Message(
        sender_id=user.id,
        recipient_id=recipient_id,
        message=message,
        conversation_id=f"conv_{min(user.id, recipient_id)}_{max(user.id, recipient_id)}",
    )
    db.add(msg)
    db.commit()
    return {"id": msg.id, "status": "sent"}


@messaging_router.get("/conversation/{user_id}")
async def get_conversation(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get conversation with another user"""
    # Build conversation ID
    conv_id = f"conv_{min(user.id, user_id)}_{max(user.id, user_id)}"
    
    messages = db.query(Message).filter_by(conversation_id=conv_id).offset(skip).limit(limit).all()
    
    return {
        "conversation_id": conv_id,
        "messages": messages,
        "count": len(messages),
    }


@messaging_router.get("/conversations")
async def list_conversations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all conversations for current user"""
    # Get recent messages for each conversation
    messages = db.query(Message).filter(
        (Message.sender_id == user.id) | (Message.recipient_id == user.id)
    ).all()
    
    conversations = {}
    for msg in messages:
        other_id = msg.recipient_id if msg.sender_id == user.id else msg.sender_id
        if msg.conversation_id not in conversations:
            conversations[msg.conversation_id] = {
                "other_user_id": other_id,
                "last_message": msg.message,
                "last_message_time": msg.created_at,
            }
    
    return list(conversations.values())


@messaging_router.post("/chat/message")
async def send_chat_message(
    video_session_id: int,
    message: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Send chat message during video session"""
    chat_msg = SessionChatMessage(
        video_session_id=video_session_id,
        user_id=user.id,
        message=message,
    )
    db.add(chat_msg)
    db.commit()
    return {"id": chat_msg.id, "status": "sent"}


# ============================================================
# ROUTER 6: FORUM
# ============================================================
forum_router = APIRouter(prefix="/forum", tags=["forum"])


@forum_router.get("/topics")
async def list_forum_topics(
    db: Session = Depends(get_db),
):
    """List all forum topics"""
    topics = db.query(ForumTopic).all()
    return topics


@forum_router.get("/topic/{topic_id}/threads")
async def list_forum_threads(
    topic_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """List threads in a topic"""
    threads = db.query(ForumThread).filter_by(topic_id=topic_id).offset(skip).limit(limit).all()
    return threads


@forum_router.post("/thread/create", response_model=ForumThreadResponse)
async def create_forum_thread(
    topic_id: int,
    title: str,
    content: str,
    tags: list = [],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Create new forum thread"""
    thread = ForumThread(
        topic_id=topic_id,
        creator_id=user.id,
        title=title,
        content=content,
        slug=title.lower().replace(" ", "-"),
        tags=tags,
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread


@forum_router.get("/thread/{thread_id}", response_model=ForumThreadResponse)
async def get_forum_thread(
    thread_id: int,
    db: Session = Depends(get_db),
):
    """Get forum thread details"""
    thread = db.query(ForumThread).filter_by(id=thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Increment view count
    thread.view_count += 1
    db.commit()
    
    return thread


@forum_router.post("/thread/{thread_id}/reply", response_model=ForumReplyResponse)
async def create_forum_reply(
    thread_id: int,
    content: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Reply to forum thread"""
    thread = db.query(ForumThread).filter_by(id=thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    reply = ForumReply(
        thread_id=thread_id,
        creator_id=user.id,
        content=content,
    )
    db.add(reply)
    thread.reply_count += 1
    db.commit()
    db.refresh(reply)
    
    return reply
