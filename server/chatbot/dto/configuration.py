from typing import Optional
from pydantic import BaseModel
from chatbot.db.model import Config


class LanguageResult(BaseModel):
    """Language result"""
    code: str
    title: str

    class Config:
        """Language result configuration"""
        orm_mode = True


class Configuration(BaseModel):
    """Configuration DTO"""
    name: Config
    value: Optional[str]


class ConfigurationUpdate(BaseModel):
    """Configuration update DTO"""
    language: str


class ConfigurationResult(Configuration):
    """Configuration result"""
    class Config:
        """Configuration result configuration"""
        orm_mode = True
