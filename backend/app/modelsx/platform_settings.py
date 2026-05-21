"""
Platform Settings model for storing global configuration
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.db import Base
import json


class PlatformSetting(Base):
    """Store platform-wide configuration settings"""
    __tablename__ = "platform_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)  # JSON-encoded value
    value_type = Column(String(20), nullable=False)  # string, boolean, integer, json
    description = Column(String(500))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def get_value(self):
        """Decode the stored value based on type"""
        if self.value_type == "boolean":
            return self.value.lower() == "true"
        elif self.value_type == "integer":
            return int(self.value)
        elif self.value_type == "json":
            return json.loads(self.value)
        else:  # string
            return self.value

    @classmethod
    def set_value(cls, key: str, value, value_type: str, description: str = None):
        """Helper to encode a value for storage"""
        if value_type == "json":
            encoded = json.dumps(value)
        elif value_type == "boolean":
            encoded = "true" if value else "false"
        else:
            encoded = str(value)
        
        return {
            "key": key,
            "value": encoded,
            "value_type": value_type,
            "description": description
        }
