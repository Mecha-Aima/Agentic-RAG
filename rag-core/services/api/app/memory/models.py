from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime

Base = declarative_base()

class ChatHistory(Base):
    """
    SQLAlchemy Model for the 'chat_history' table.
    Stores the raw conversation log for auditing and context.
    """
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    session_id = Column(String(255), index=True, nullable=False)
    
    user_id = Column(String(255), index=True, nullable=False)
    
    # Role: 'user', 'assistant', or 'system'
    role = Column(String(50), nullable=False)
    
    content = Column(Text, nullable=False)
    
    # Metadata: Token usage, latency, model version used
    metadata_ = Column(JSON, default={}, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)