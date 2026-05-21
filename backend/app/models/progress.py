from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, UniqueConstraint
from app.core.db import Base

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    path = Column(String, index=True, nullable=False)
    module_id = Column(String, index=True, nullable=False)
    order = Column(Integer, default=0)  # ✅ Unlock rule support
    completed_at = Column(DateTime, server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", name="uq_user_module"),
    )
