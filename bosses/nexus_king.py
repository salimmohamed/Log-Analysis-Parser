"""
Nexus-King boss implementation - current raid tier.
"""

import re
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Any
from .base import Boss


class NexusKing(Boss):
    """Nexus-King boss encounter."""
    
    detection_patterns = ['nexus-king', 'Nexus-King']
    
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
        # Handle actual deaths
        if "died to" in event:
            match = re.search(r"(\w+)\s+died to (.*?)\s+\(([^)]+)\)", event)
            if match:
                # Normalize beam deaths to consistent naming
                cause = match.group(2)
                if "sweeping breath" in cause:
                    return match.group(1), "died to beam"
                elif "tank frontal" in cause:
                    return match.group(1), "died to tank frontal"
                else:
                    return match.group(1), f"died to {cause}"
        
        # Handle spirit failures
        if "failed to face their spirits" in event:
            match = re.search(r"(\w+)\s+failed to face their spirits", event)
            if match:
                return match.group(1), "failed to face their spirits"
        
        # Handle MC events (these count as mistakes)
        if "got MC'd" in event:
            match = re.search(r"(\w+)\s+got MC'd from (.*?)\s+\(([^)]+)\)", event)
            if match:
                # Use same naming as death events for consistency
                cause = match.group(2)
                if "sweeping breath" in cause:
                    return match.group(1), "died to beam"
                elif "tank frontal" in cause:
                    return match.group(1), "died to tank frontal"
                else:
                    return match.group(1), f"MC'd from {cause}"
        
        return None, None

    def analyze_non_player_mistakes(self, attempts: List[Any]) -> Dict[str, int]:
        mistakes = defaultdict(int)
        
        for attempt in attempts:
            for event in attempt.events:
                # Nexus-King doesn't really have non-player mistakes
                # Player mistakes like MC'd, failed to face spirits are handled in player stats
                if "No mistakes found" in event:
                    # This would be a non-player mistake if it existed
                    pass
        
        return mistakes
