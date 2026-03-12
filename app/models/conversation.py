from sqlalchemy import Column, String, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from .base import Base

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(UUID(as_uuid=True), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    messages = Column(JSON)
