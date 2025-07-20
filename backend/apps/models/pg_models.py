from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
import datetime

Base = declarative_base()

class ChatMetric(Base):
    __tablename__ = "chat_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String)
    intent = Column(String)
    response_time = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)