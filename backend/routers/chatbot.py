"""
Chatbot Router
Handles AI chatbot interactions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from database import get_db
from models import User, ChatHistory
from schemas import ChatHistoryCreate, ChatHistoryResponse
from utils.auth import get_current_active_user
from ai.chatbot import chatbot

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


@router.post("/ask", response_model=dict)
def ask_chatbot(
    question: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ask the AI chatbot a question"""
    # Build context from user data
    context = chatbot.get_conversation_context(current_user.id, db)
    
    # Get answer
    answer = chatbot.get_answer(question, context)
    
    # Save to chat history
    new_chat = ChatHistory(
        user_id=current_user.id,
        question=question,
        answer=answer,
        context=str(context)[:1000]  # Truncate context for storage
    )
    
    db.add(new_chat)
    db.commit()
    
    return {
        'question': question,
        'answer': answer,
        'timestamp': datetime.utcnow()
    }


@router.get("/history", response_model=List[ChatHistoryResponse])
def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get chat history for the current user"""
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).order_by(ChatHistory.timestamp.desc()).offset(skip).limit(limit).all()
    
    return history


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
def clear_chat_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Clear chat history for the current user"""
    db.query(ChatHistory).filter(
        ChatHistory.user_id == current_user.id
    ).delete()
    
    db.commit()
    
    return None
