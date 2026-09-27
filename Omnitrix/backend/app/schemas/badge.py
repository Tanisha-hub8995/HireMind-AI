from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class BadgeItem(BaseModel):
    id: str
    name: str
    category: str
    stars: int = 1
    max_stars: int = 5
    tier: str = "BRONZE"  # BRONZE, SILVER, GOLD, PLATINUM, DIAMOND
    icon: str = "⭐"
    description: str
    unlocked: bool = True
    progress_percentage: float = 0.0
    current_value: float = 0.0
    target_value: float = 100.0
    unlocked_at: Optional[datetime] = None


class UserLevelInfo(BaseModel):
    current_level: int = 1
    level_title: str = "Apprentice Engineer (1-Star)"
    stars_earned: int = 1
    total_stars_possible: int = 30
    xp: int = 0
    xp_to_next_level: int = 500
    level_progress_percentage: float = 0.0
    badges_unlocked_count: int = 1
    total_badges_count: int = 6


class BadgesResponse(BaseModel):
    user_id: int
    level_info: UserLevelInfo
    badges: List[BadgeItem] = []
    recent_unlocked_badges: List[BadgeItem] = []
