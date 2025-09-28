"""
Mug'Zee boss implementation (archived from previous tier).
"""

import re
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Any
from ..base import Boss


class MugZee(Boss):
    """Mug'Zee boss encounter (archived)."""
    
    def __init__(self):
        super().__init__("Mug'Zee")
        self.mechanics = [
            "Unstable Cluster Bomb",
            "Goblin-Guided Rocket",
            "Boss enrage",
            "Goon enrage"
        ]
        self.death_causes = [
            "Frostshatter Spear",
            "Stormfury stun",
            "Goon's frontal",
            "Molten Golden Knuckles frontal",
            "electrocution line",
            "popping a mine"
        ]
        self.non_player_mistakes = [
            "Unstable Cluster Bomb not soaked",
            "Goblin-Guided Rocket under-soaked",
            "Boss enrage",
            "Goon enrage",
            "popping mine"
        ]

    def is_attempt_header(self, line: str) -> bool:
        return "Mug'Zee #" in line

    def is_boss_event(self, line: str) -> bool:
        return any(event in line for event in [
            "died to",
            "was not soaked",
            "was soaked by fewer than",
            "Boss enraged",
            "Goon enraged",
            "No mistakes found"
        ])

    def extract_player_death(self, event: str) -> Tuple[Optional[str], Optional[str]]:
        if "died to" in event:
            match = re.search(r"(\w+)\s+died to (.*?)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), match.group(2)
        return None, None

    def analyze_non_player_mistakes(self, attempts: List[Any]) -> Dict[str, int]:
        mistakes = defaultdict(int)
        for attempt in attempts:
            for event in attempt.events:
                if "was not soaked" in event:
                    mistakes["Cluster bomb not soaked"] += 1
                elif "was soaked by fewer than" in event:
                    mistakes["Rocket under-soaked"] += 1
                elif "Boss enraged" in event:
                    mistakes["Boss enrage"] += 1
                elif "Goon enraged" in event:
                    mistakes["Goon enrage"] += 1
        return mistakes
