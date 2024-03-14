from pydantic import BaseModel


class SessionStatsResult(BaseModel):
    """Session stats result"""

    total: int


class MessageStatsResult(BaseModel):
    """Message stats result"""

    total: int
    likes: int
    dislikes: int
    regenerations: int
    ratings: int


class StatsResult(BaseModel):
    """Stats result"""

    sessions: SessionStatsResult
    messages: MessageStatsResult
