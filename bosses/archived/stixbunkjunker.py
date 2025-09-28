"""
Stix Bunkjunker boss implementation (archived from previous tier).
"""

import re
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Any
from ..base import Boss


class StixBunkjunker(Boss):
    """Stix Bunkjunker boss encounter (archived)."""
    
    def __init__(self):
        super().__init__("Stix Bunkjunker")
        self.mechanics = [
            "ball",
            "bombshell",
            "scrapmaster"
        ]
        self.death_causes = [
            "ball expired",
            "hit a bombshell",
            "Bombshell did not die in time",
            "missed their Scrapmaster"
        ]
        self.non_player_mistakes = [
            "ball expired",
            "hit a bombshell",
            "Bombshell did not die in time",
            "missed their Scrapmaster"
        ]

    def is_attempt_header(self, line: str) -> bool:
        return "Stix Bunkjunker #" in line

    def is_boss_event(self, line: str) -> bool:
        return any(event in line for event in [
            "died to",
            "ball expired",
            "hit a bombshell",
            "Bombshell did not die in time",
            "missed their Scrapmaster",
            "No mistakes found"
        ])

    def extract_player_death(self, event: str) -> Tuple[Optional[str], Optional[str]]:
        # missed their Scrapmaster on <marker>
        match = re.match(r"\s*(\w+) missed their Scrapmaster on (\w+) \(([^)]+)\)", event)
        if match:
            player = match.group(1)
            marker = match.group(2)
            return player, f"missed their Scrapmaster on {marker}"
        # hit a bombshell
        match = re.match(r"\s*(\w+) hit a bombshell \(([^)]+)\)", event)
        if match:
            player = match.group(1)
            return player, "hit a bombshell"
        # ball expired
        match = re.match(r"\s*(\w+)'s ball expired \(([^)]+)\)", event)
        if match:
            player = match.group(1)
            return player, "ball expired"
        # died to
        if "died to" in event:
            match = re.search(r"(\w+)\s+died to (.*?)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), match.group(2)
        return None, None

    def analyze_non_player_mistakes(self, attempts: List[Any]) -> Dict[str, int]:
        mistakes = defaultdict(int)
        for attempt in attempts:
            for event in attempt.events:
                if "ball expired" in event:
                    mistakes["Ball expired"] += 1
                elif "hit a bombshell" in event:
                    mistakes["Hit bombshell"] += 1
                elif "Bombshell did not die in time" in event:
                    mistakes["Bombshell not killed"] += 1
                elif "missed their Scrapmaster" in event:
                    mistakes["Missed scrapmaster"] += 1
        return mistakes
