"""
Gallywix boss implementation (archived from previous tier).
"""

import re
from collections import defaultdict
from typing import List, Tuple, Optional, Dict, Any
from ..base import Boss


class Gallywix(Boss):
    """Gallywix boss encounter (archived)."""
    
    def __init__(self):
        super().__init__("Gallywix")
        self.mechanics = [
            "Giga Blast",
            "Giga Blast Residue",
            "Overloaded Rockets",
            "Bigger Badder Bomb Blast",
            "Bad Belated Boom",
            "Cuff Bomb",
            "boss landing",
            "Sabotage Zone",
            "clicking a dud",
            "boss aggro",
            "Wrenchmonger enrage",
            "Sentry Shock Barrage",
            "Technicians' Juice It",
            "Haywire Workshop",
            "Mayhem Rockets"
        ]
        self.death_causes = [
            "Giga Blast",
            "Giga Blast Residue",
            "Overloaded Rockets",
            "Bigger Badder Bomb Blast",
            "Bad Belated Boom",
            "Cuff Bomb",
            "boss landing",
            "Sabotage Zone",
            "clicking a dud",
            "boss aggro",
            "Wrenchmonger enrage",
            "Sentry Shock Barrage",
            "Haywire Workshop",
            "Mayhem Rockets"
        ]
        self.non_player_mistakes = [
            "Canister under-soaked",
            "Wrenchmonger enrage",
            "Sentry Shock Barrage",
            "Technicians' Juice It",
            "No mistakes found"
        ]

    def is_attempt_header(self, line: str) -> bool:
        return "Gallywix #" in line

    def is_boss_event(self, line: str) -> bool:
        return any(event in line for event in [
            "died to",
            "was hit by",
            "died with",
            "was soaked by fewer than",
            "was enraged",
            "cast went off",
            "No mistakes found"
        ])

    def extract_player_death(self, event: str) -> Tuple[Optional[str], Optional[str]]:
        # died to
        if "died to" in event:
            match = re.search(r"(\w+)\s+died to (.*?)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), match.group(2)
        # was hit by (non-fatal)
        if "was hit by" in event:
            match = re.search(r"(\w+)\s+was hit by (.*?)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), f"hit by {match.group(2)}"
        # died with
        if "died with" in event:
            match = re.search(r"(\w+)\s+died with (.*?)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), f"died with {match.group(2)}"
        # was enraged and killed
        if "was enraged" in event and "killed" in event:
            match = re.search(r"\[-\]\s+\w+\s+\d+.*?killed\s+(\w+)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), "killed by enraged add"
        return None, None

    def analyze_non_player_mistakes(self, attempts: List[Any]) -> Dict[str, int]:
        mistakes = defaultdict(int)
        canister_breakdown = defaultdict(int)
        for attempt in attempts:
            for event in attempt.events:
                if "was soaked by fewer than" in event:
                    # Extract canister number and type
                    match = re.search(r'(DPS|Heal)\s+Canister\s+#(\d+)\s+was soaked by fewer than', event)
                    if match:
                        canister_type = match.group(1)
                        canister_number = match.group(2)
                        canister_key = f"{canister_type} Canister #{canister_number}"
                        canister_breakdown[canister_key] += 1
                    mistakes["Canister under-soaked"] += 1
                elif "was enraged" in event and "killed" in event:
                    mistakes["Wrenchmonger enrage"] += 1
                elif "Shock Barrage cast went off" in event:
                    mistakes["Sentry Shock Barrage"] += 1
                elif "Juice It cast(s) went off" in event:
                    mistakes["Technicians' Juice It"] += 1
        
        # Add detailed canister breakdown to mistakes
        for canister, count in canister_breakdown.items():
            mistakes[f"{canister} under-soaked"] = count
            
        return mistakes
