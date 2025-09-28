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
    """Export attempts to CSV format with separate rows per player event."""
    # Use the attempts data directly instead of reading from file
    attempts_lines = []
    for attempt in attempts:
        # Add header line
        attempts_lines.append(f"{attempt.boss.name} #{attempt.header.split('#')[1].split()[0]}   ({attempt.header.split('(')[1]}")
        # Add events
        for event in attempt.events:
            attempts_lines.append(event)
        # Add timestamp
        attempts_lines.append(attempt.timestamp)
        # Add blank line
        attempts_lines.append("")

    # Parse attempts into CSV rows - separate row for each player event
    rows = []
    i = 0
    while i < len(attempts_lines):
        line = attempts_lines[i]
        if line.startswith('Stix Bunkjunker #') or line.startswith("Mug'Zee #") or line.startswith('Gallywix #') or line.startswith('Nexus-King #'):
            # Header line
            header = line
            events = []
            i += 1
            # Collect events until we hit a timestamp or blank line
            while i < len(attempts_lines) and attempts_lines[i] and not attempts_lines[i][0].isdigit() and not attempts_lines[i].startswith('Stix Bunkjunker #') and not attempts_lines[i].startswith("Mug'Zee #") and not attempts_lines[i].startswith('Gallywix #') and not attempts_lines[i].startswith('Nexus-King #'):
                events.append(attempts_lines[i].strip())
                i += 1
            # Timestamp line
            timestamp = ''
            if i < len(attempts_lines) and attempts_lines[i] and (attempts_lines[i].startswith('Today at') or attempts_lines[i][0].isdigit()):
                timestamp = attempts_lines[i]
                i += 1
            # Skip blank lines
            while i < len(attempts_lines) and not attempts_lines[i]:
                i += 1
            
            # Parse header for pull # and duration
            pull_match = re.search(r'#(\d+)', header)
            duration_match = re.search(r'\((\d+):(\d+)\)', header)
            pull_num = pull_match.group(1) if pull_match else ''
            duration = ''
            if duration_match:
                minutes, seconds = duration_match.groups()
                duration = f"{minutes}:{seconds.zfill(2)}"
            
            # Create separate row for each player event
            for ev in events:
                # Skip non-player events (like "No mistakes found" and timestamp lines)
                if ev.strip() and not ev.startswith('No mistakes found') and not ev.startswith('Today at'):
                    # Extract player name and event details
                    # Pattern: "  PlayerName event description (timestamp)"
                    event_clean = ev.strip()
                    
                    # Extract timestamp from the end if present
                    timestamp_match = re.search(r'\(([^)]+)\)$', event_clean)
                    event_timestamp = timestamp_match.group(1) if timestamp_match else ''
                    
                    # Remove timestamp from event description
                    event_description = re.sub(r'\s+\([^)]+\)$', '', event_clean)
                    
                    # Extract player name (first word)
                    player_match = re.match(r'^(\w+)', event_description)
                    player_name = player_match.group(1) if player_match else 'Unknown'
                    
                    # Remove player name from event description
                    event_text = re.sub(r'^\w+\s+', '', event_description)
                    
                    # Create row for this player event
                    rows.append([
                        pull_num,
                        '',  # Empty date column
                        duration,
                        player_name,
                        event_text,
                        event_timestamp
                    ])
        else:
            i += 1

    # Write to CSV (main table only)
    write_csv(rows, output_file)
