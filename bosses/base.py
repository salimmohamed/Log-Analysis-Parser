"""
Base class for boss encounter implementations.
"""

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Any


class Boss(ABC):
    """
    Base class for all boss encounters.
    
    Subclasses must define a class-level 'detection_patterns' attribute:
    A list of strings used to identify the boss from log file content.
    
    Example:
        class NexusKing(Boss):
            detection_patterns = ['nexus-king', 'Nexus-King']
    """
    
    def __init__(self, name: str):
        self.name = name
        self.mechanics: List[str] = []
        self.death_causes: List[str] = []
        self.non_player_mistakes: List[str] = []

    @abstractmethod
    def is_attempt_header(self, line: str) -> bool:
        """Check if this line is a boss attempt header."""
        pass

    @abstractmethod
    def is_boss_event(self, line: str) -> bool:
        """Check if this line contains a boss event."""
        pass

    @abstractmethod
    def extract_player_death(self, line: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract player name and death cause from event line."""
        pass

    @abstractmethod
    def analyze_non_player_mistakes(self, attempts: List[Any]) -> Dict[str, int]:
        """Count non-player mistakes (boss enrage, etc.)."""
        pass

    def format_attempt(self, attempt_number: int, header: str, duration: str) -> str:
        """Format attempt header with new number."""
        return f"{self.name} #{attempt_number}   ({duration}"

    def get_boss_info(self) -> Dict[str, Any]:
        """Get boss info for debugging."""
        return {
            'name': self.name,
            'mechanics': self.mechanics,
            'death_causes': self.death_causes,
            'non_player_mistakes': self.non_player_mistakes
        }
