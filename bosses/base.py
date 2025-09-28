"""
Abstract base class for all boss implementations.
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Any


class Boss(ABC):
    """Abstract base class for all boss encounters."""
    
    def __init__(self, name: str):
        self.name = name
        self.mechanics: List[str] = []
        self.death_causes: List[str] = []
        self.non_player_mistakes: List[str] = []

    @abstractmethod
    def is_attempt_header(self, line: str) -> bool:
        """Check if line is a boss attempt header."""
        pass

    @abstractmethod
    def is_boss_event(self, line: str) -> bool:
        """Check if line is a boss-specific event."""
        pass

    @abstractmethod
    def extract_player_death(self, line: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract player name and death cause from event line."""
        pass

    @abstractmethod
    def analyze_non_player_mistakes(self, attempts: List[Any]) -> Dict[str, int]:
        """Analyze non-player mistakes for this boss."""
        pass

    def format_attempt(self, attempt_number: int, header: str, duration: str) -> str:
        """Format attempt header with new number."""
        return f"{self.name} #{attempt_number}   ({duration}"

    def get_boss_info(self) -> Dict[str, Any]:
        """Get boss information for debugging/display purposes."""
        return {
            'name': self.name,
            'mechanics': self.mechanics,
            'death_causes': self.death_causes,
            'non_player_mistakes': self.non_player_mistakes
        }
