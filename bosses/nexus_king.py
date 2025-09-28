"""
Nexus-King boss implementation for the new raid tier.
"""

import re
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Any
from .base import Boss


class NexusKing(Boss):
    """Nexus-King boss encounter."""
    
    def __init__(self):
        super().__init__("Nexus-King")
        self.mechanics = [
            "Vanquish (tank frontal)",
            "Besiege (sweeping breath)", 
            "Spirits (face spirits)",
            "Rip (Behead fissure)"
        ]
        self.death_causes = [
            "tank frontal",
            "sweeping breath", 
            "standing on a fissure left by Behead",
            "failed to face their spirits"
        ]
        self.non_player_mistakes = [
            "got MC'd from tank frontal",
            "got MC'd from sweeping breath",
            "failed to face their spirits"
        ]

    def is_attempt_header(self, line: str) -> bool:
        return "Nexus-King #" in line

    def is_boss_event(self, line: str) -> bool:
        return any(event in line for event in [
            "got MC'd from",
            "died to",
            "failed to face their spirits",
            "No mistakes found"
        ])

    def extract_player_death(self, event: str) -> Tuple[Optional[str], Optional[str]]:
        # Handle "died to" events
        if "died to" in event:
            match = re.search(r"(\w+)\s+died to (.*?)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), match.group(2)
        
        # Handle "failed to face their spirits" events
        if "failed to face their spirits" in event:
            match = re.search(r"(\w+)\s+failed to face their spirits", event)
            if match:
                return match.group(1), "failed to face their spirits"
        
        # Handle "got MC'd" events (these are mistakes, not deaths)
        if "got MC'd" in event:
            match = re.search(r"(\w+)\s+got MC'd from (.*?)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), f"MC'd from {match.group(2)}"
        
        return None, None

    def analyze_non_player_mistakes(self, attempts: List[Any]) -> Dict[str, int]:
        mistakes = defaultdict(int)
        
        for attempt in attempts:
            for event in attempt.events:
                # Only count actual non-player mistakes (like boss enrage, mechanics failing, etc.)
                # Player mistakes like MC'd, failed to face spirits are handled in player stats
                if "No mistakes found" in event:
                    # This would be a non-player mistake if it existed
                    pass
        
        return mistakes
