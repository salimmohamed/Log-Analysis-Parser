"""
Player statistics analysis.
"""

from collections import defaultdict
from typing import List, Dict, Any


def analyze_player_stats(attempts: List[Any]) -> Dict[str, Dict[str, int]]:
    """Analyze player death statistics from attempts."""
    player_stats = defaultdict(lambda: defaultdict(int))
    
    for attempt in attempts:
        for event in attempt.events:
            player, cause = attempt.boss.extract_player_death(event)
            if player and cause:
                player_stats[player][cause] += 1
    
    return player_stats


def format_player_stats(player_stats: Dict[str, Dict[str, int]]) -> str:
    """Format player statistics for output."""
    output = ["Player Statistics:\n"]
    
    # Sort players by total deaths
    sorted_players = sorted(
        player_stats.items(),
        key=lambda x: sum(x[1].values()),
        reverse=True
    )
    
    for player, causes in sorted_players:
        total_deaths = sum(causes.values())
        if total_deaths == 0:
            continue
            
        # Format the causes
        cause_list = [f"{cause} x{count}" for cause, count in sorted(causes.items(), key=lambda x: x[1], reverse=True)]
        output.append(f"{player} (Total deaths: {total_deaths})")
        output.append("  " + ", ".join(cause_list))
        output.append("")  # Blank line between players
    
    return "\n".join(output)
