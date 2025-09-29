"""
CSV export functionality.
"""

import csv
import re
from typing import List, Any


def write_csv(rows: List[List[str]], output_file: str) -> None:
    """Write data to CSV file."""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Pull #', 'Date', 'Duration', 'Player', 'Event', 'Timestamp'])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output_file}")


def export_to_csv(attempts: List[Any], output_file: str) -> None:
    """Export player statistics to CSV format."""
    from analyzers.player_stats import analyze_player_stats
    
    # Analyze player statistics
    player_stats = analyze_player_stats(attempts)
    
    # Create statistics rows
    rows = []
    for player, causes in player_stats.items():
        total_deaths = sum(causes.values())
        if total_deaths == 0:
            continue
            
        # Count specific mistake types
        beam_mistakes = sum(count for cause, count in causes.items() if 'beam' in cause)
        spirits_mistakes = sum(count for cause, count in causes.items() if 'spirits' in cause)
        tank_frontal_mistakes = sum(count for cause, count in causes.items() if 'tank frontal' in cause)
        other_mistakes = total_deaths - beam_mistakes - spirits_mistakes - tank_frontal_mistakes
        
        rows.append([
            player,
            total_deaths,
            beam_mistakes,
            spirits_mistakes,
            tank_frontal_mistakes,
            other_mistakes
        ])
    
    # Sort by total deaths (descending)
    rows.sort(key=lambda x: x[1], reverse=True)
    
    # Write statistics CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Player', 'Total_Deaths', 'Beam_Mistakes', 'Spirits_Mistakes', 'Tank_Frontal_Mistakes', 'Other_Mistakes'])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} player statistics to {output_file}")
