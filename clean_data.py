"""
WoW raid log parser - processes Discord bot output into structured data.
"""

import re
from datetime import datetime
from collections import defaultdict
from typing import List, Any, Dict

from bosses import detect_boss_from_content
from parsers.timestamp import is_timestamp, parse_timestamp
from analyzers.player_stats import analyze_player_stats, format_player_stats
from analyzers.mistakes import format_non_player_mistakes
from exporters.csv import export_to_csv


class Attempt:
    """Represents a single boss attempt."""
    
    def __init__(self, header: str, events: List[str], timestamp: str, boss):
        self.header = header
        self.events = events
        self.timestamp = timestamp
        self.datetime = parse_timestamp(timestamp)
        self.boss = boss
        # Extract duration from header
        duration_match = re.search(r"\((\d+):(\d+)\)", header)
        if duration_match:
            minutes, seconds = map(int, duration_match.groups())
            self.duration = minutes * 60 + seconds
        else:
            self.duration = 0

    def format_attempt(self, attempt_number: int) -> List[str]:
        """Format the attempt with the new number."""
        duration = self.header.split('(')[1]
        return [self.boss.format_attempt(attempt_number, self.header, duration)] + self.events + [self.timestamp]


def get_worst_offenders(stats: Dict[str, Dict[str, int]]) -> str:
    """Show top 5 players for each mistake type."""
    if not stats:
        return ""
    
    # Count up all the mistakes by type
    mistake_totals = defaultdict(int)
    for player, mistakes in stats.items():
        for mistake, count in mistakes.items():
            mistake_totals[mistake] += count
    
    # Sort by frequency
    sorted_mistakes = sorted(mistake_totals.items(), key=lambda x: x[1], reverse=True)
    
    output = ["\nWorst Offenders:\n"]
    
    for mistake_type, total_count in sorted_mistakes:
        # Get top 5 players for this mistake
        player_counts = []
        for player, mistakes in stats.items():
            if mistake_type in mistakes:
                player_counts.append((player, mistakes[mistake_type]))
        
        player_counts.sort(key=lambda x: x[1], reverse=True)
        top_5 = player_counts[:5]
        
        if top_5:
            output.append(f"{mistake_type} (Total: {total_count}):")
            for i, (player, count) in enumerate(top_5, 1):
                output.append(f"  {i}. {player}: {count} times")
            output.append("")  # Blank line between events
    
    return "\n".join(output)


def clean_data(input_file: str, output_file: str, csv_file: str, boss) -> None:
    """Parse Discord bot output and generate clean raid data."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
        return
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return
    
    attempts = []
    current_header = None
    current_events = []
    current_timestamp = None
    current_pull_number = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip Discord bot warnings
        if ":warning: Experimental :warning:" in line:
            continue
        
        # Strip emojis but keep the actual content
        cleaned_line = line.strip()
        
        # Remove Discord emoji patterns like :NexusKing_Spirits: :Monk~3:
        # This is a bit hacky but works for the bot's output format
        cleaned_line = re.sub(r':[^:]+:\s*:[^:]+:\s*', '', cleaned_line)
        
        # Fallback for stubborn emoji patterns
        if ':NexusKing_' in cleaned_line or ':Shaman~' in cleaned_line or ':Warlock~' in cleaned_line:
            cleaned_line = re.sub(r':[^:]+:', '', cleaned_line).strip()
        
        if not cleaned_line:
            continue
            
        # Look for boss attempt headers like "Nexus-King #1 (2:33)"
        if boss.is_attempt_header(cleaned_line):
            pull_match = re.search(r'#(\d+)', cleaned_line)
            if pull_match:
                pull_number = int(pull_match.group(1))
                # Skip duplicate pull numbers (sometimes the bot sends duplicates)
                if pull_number == current_pull_number:
                    continue
                # Save the previous attempt if we have both header and timestamp
                if current_header and current_timestamp:
                    # Clean up "Part X" suffixes from headers
                    current_header = re.sub(r'\s*-\s*Part\s+\d+', '', current_header)
                    attempts.append(Attempt(current_header, current_events, current_timestamp, boss))
                current_header = cleaned_line
                current_events = []
                current_timestamp = None  # Reset for new attempt
                current_pull_number = pull_number
            continue
            
        # Process events for the current attempt
        if current_header:
            if is_timestamp(cleaned_line):
                current_timestamp = cleaned_line
            elif boss.is_boss_event(cleaned_line):
                current_events.append("  " + cleaned_line)  # Indent for readability
    
    # Don't forget the last attempt
    if current_header and current_timestamp:
        current_header = re.sub(r'\s*-\s*Part\s+\d+', '', current_header)
        attempts.append(Attempt(current_header, current_events, current_timestamp, boss))
    
    # Filter out empty attempts (sometimes from other bosses)
    attempts = [attempt for attempt in attempts if attempt.events]
    
    # Sort by timestamp to get chronological order
    attempts.sort(key=lambda x: x.datetime)
    
    # Generate clean output with renumbered attempts
    output_lines = []
    for i, attempt in enumerate(attempts, 1):
        output_lines.extend(attempt.format_attempt(i))
        output_lines.append("")  # Blank line between attempts
    
    # Generate player stats and summaries
    player_stats = analyze_player_stats(attempts)
    stats_output = format_player_stats(player_stats)
    
    # Check for non-player mistakes (boss enrage, etc.)
    non_player_mistakes = boss.analyze_non_player_mistakes(attempts)
    mistakes_output = format_non_player_mistakes(non_player_mistakes)
    
    # Show who's making the most mistakes
    worst_offenders = get_worst_offenders(player_stats)
    
    # Write everything to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(line + "\n" for line in output_lines)
            f.write("\n" + "="*50 + "\n\n")  # Separator
            f.write(stats_output)
            f.write(worst_offenders)
            f.write(mistakes_output)
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")
        return
    
    # Export to CSV
    try:
        export_to_csv(attempts, csv_file)
        print(f"Data has been cleaned and saved to {output_file}")
        print(f"CSV data has been saved to {csv_file}")
        print(f"Detected boss: {boss.name}")
    except Exception as e:
        print(f"Error exporting CSV: {e}")
        return
    
    print("\nVerifying cleaning process...")
    try:
        verify_cleaning(input_file, output_file)
        print("Verification results have been saved to verification_results.txt")
    except Exception as e:
        print(f"Error during verification: {e}")


def verify_cleaning(input_file: str, output_file: str) -> None:
    """Double-check that we didn't lose any important data during cleaning."""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_lines = f.readlines()
        with open(output_file, 'r', encoding='utf-8') as f:
            output_lines = f.readlines()
    except Exception as e:
        print(f"Error reading files for verification: {e}")
        return
    
    # Clean up input to match what we actually process
    input_lines = [line for line in input_lines if ":warning: Experimental :warning:" not in line]
    input_lines = [re.sub(r':[^:]+:', '', line).strip() for line in input_lines]
    input_lines = [line for line in input_lines if line]  # Remove empty lines
    
    # Remove the stats section from output for comparison
    try:
        stats_start = output_lines.index("="*50 + "\n")
        output_lines = output_lines[:stats_start]
    except ValueError:
        # No stats section found, use all lines
        pass
    output_lines = [line.strip() for line in output_lines if line.strip()]
    
    # Check if any important data got lost
    missing_lines = []
    for line in output_lines:
        if line not in input_lines:
            missing_lines.append(line)
    
    # Write verification report
    try:
        with open("verification_results.txt", 'w', encoding='utf-8') as f:
            f.write("Verification Results:\n\n")
            if not missing_lines:
                f.write("All lines in the cleaned output exist in the original input.\n")
            else:
                f.write("The following lines in the cleaned output were not found in the original input:\n")
                for line in missing_lines:
                    f.write(f"- {line}\n")
            
            # Show cleaning stats
            f.write("\nCleaning Statistics:\n")
            f.write(f"Original input lines: {len(input_lines)}\n")
            f.write(f"Cleaned output lines: {len(output_lines)}\n")
            f.write(f"Lines removed: {len(input_lines) - len(output_lines)}\n")
            if missing_lines:
                f.write(f"Lines not found in original: {len(missing_lines)}\n")
    except Exception as e:
        print(f"Error writing verification results: {e}")


if __name__ == "__main__":
    input_file = "data.txt"
    output_file = "cleaned_data.txt"
    csv_file = "cleaned_data.csv"
    
    # Figure out which boss we're dealing with
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            boss = detect_boss_from_content(content)
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
        print("Make sure you have copied the Discord bot output to data.txt")
        exit(1)
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        exit(1)
    
    print(f"Auto-detected boss: {boss.name}")
    print(f"Boss mechanics: {', '.join(boss.mechanics)}")
    
    clean_data(input_file, output_file, csv_file, boss)
