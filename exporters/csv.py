"""
CSV export functionality.
"""

import csv
from typing import List, Any


def export_to_csv(attempts: List[Any], output_file: str) -> None:
    """Export player statistics to CSV format."""
    from analyzers.player_stats import analyze_player_stats
    
    player_stats = analyze_player_stats(attempts)
    rows = []
    
    for player, mistakes in player_stats.items():
        total_mistakes = sum(mistakes.values())
        if total_mistakes == 0:
            continue
            
        # Count specific mistake types (hardcoded for Nexus-King)
        beam_mistakes = sum(count for cause, count in mistakes.items() if 'beam' in cause)
        spirits_mistakes = sum(count for cause, count in mistakes.items() if 'spirits' in cause)
        tank_frontal_mistakes = sum(count for cause, count in mistakes.items() if 'tank frontal' in cause)
        other_mistakes = total_mistakes - beam_mistakes - spirits_mistakes - tank_frontal_mistakes
        
        rows.append([
            player,
            total_mistakes,
            beam_mistakes,
            spirits_mistakes,
            tank_frontal_mistakes,
            other_mistakes
        ])
    
    rows.sort(key=lambda x: x[1], reverse=True)
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Player', 'Total_Deaths', 'Beam_Mistakes', 'Spirits_Mistakes', 'Tank_Frontal_Mistakes', 'Other_Mistakes'])
            writer.writerows(rows)
        print(f"Wrote {len(rows)} player statistics to {output_file}")
    except Exception as e:
        print(f"Error writing CSV: {e}")
        raise
