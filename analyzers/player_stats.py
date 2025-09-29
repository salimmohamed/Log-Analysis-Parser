"""
Player statistics analysis.
"""

from collections import defaultdict
from typing import List, Dict, Any


def analyze_player_stats(attempts: List[Any]) -> Dict[str, Dict[str, int]]:
    """Count up player mistakes from all attempts."""
    player_stats = defaultdict(lambda: defaultdict(int))
    
    for attempt in attempts:
        for event in attempt.events:
            player, cause = attempt.boss.extract_player_death(event)
            if player and cause:
                player_stats[player][cause] += 1
    
    return player_stats


def format_player_stats(player_stats: Dict[str, Dict[str, int]]) -> str:
    """Format player stats for output."""
    output = ["Player Statistics:\n"]
    
    # Sort by total mistakes
    sorted_players = sorted(
        player_stats.items(),
        key=lambda x: sum(x[1].values()),
        reverse=True
    )
    
    for player, mistakes in sorted_players:
        total_mistakes = sum(mistakes.values())
        if total_mistakes == 0:
            continue
            
        # Show mistake breakdown
        mistake_list = [f"{mistake} x{count}" for mistake, count in sorted(mistakes.items(), key=lambda x: x[1], reverse=True)]
        output.append(f"{player} (Total deaths: {total_mistakes})")
        output.append("  " + ", ".join(mistake_list))
        output.append("")  # Blank line between players
    
    return "\n".join(output)
