"""
Modular log analysis parser with automatic boss detection.
"""

import re
from datetime import datetime
from collections import defaultdict
from typing import List, Any

# Import our modular components
from bosses import detect_boss_from_content
from parsers.timestamp import is_timestamp, parse_timestamp, parse_attempt_duration
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


def normalize_player_name(name: str) -> str:
    """Normalize player name for consistency."""
    # Remove any emoji patterns
    name = re.sub(r':[^:]+:', '', name)
    # Remove any extra whitespace
    name = name.strip()
    # Convert to title case for consistency
    return name.title()


def ordinal(n: int) -> str:
    """Returns 1st, 2nd, 3rd, 4th, etc."""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"


def clean_data(input_file: str, output_file: str, csv_file: str, boss) -> None:
    """Main data cleaning function."""
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    attempts = []
    current_attempt = None
    current_events = []
    current_timestamp = None
    current_pull_number = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Skip the experimental warning line
        if ":warning: Experimental :warning:" in line:
            continue
        
        # Clean emojis from line, but preserve timestamp format
        # First, let's be more careful about what we remove
        cleaned_line = line.strip()
        
        # Remove emoji patterns but preserve the structure
        # Pattern: :NexusKing_Spirits: :Monk~3: Bredie failed to face their spirits in set: 2 (1:29.7)
        # Should become: Bredie failed to face their spirits in set: 2 (1:29.7)
        cleaned_line = re.sub(r':[^:]+:\s*:[^:]+:\s*', '', cleaned_line)
        
        # If that didn't work, try the more aggressive approach
        if ':NexusKing_' in cleaned_line or ':Shaman~' in cleaned_line or ':Warlock~' in cleaned_line:
            cleaned_line = re.sub(r':[^:]+:', '', cleaned_line).strip()
        
        # Skip if line is empty after cleaning
        if not cleaned_line:
            continue
            
        # Check if this is a boss attempt header
        if boss.is_attempt_header(cleaned_line):
            # Extract pull number
            pull_match = re.search(r'#(\d+)', cleaned_line)
            if pull_match:
                pull_number = int(pull_match.group(1))
                # If this is the same pull number as current, append events instead of creating new attempt
                if pull_number == current_pull_number:
                    continue
                # Save previous attempt if it exists
                if current_attempt and current_timestamp:  # Only save if we have both header and timestamp
                    # Remove any "Part X" from the attempt header
                    current_attempt = re.sub(r'\s*-\s*Part\s+\d+', '', current_attempt)
                    attempts.append(Attempt(current_attempt, current_events, current_timestamp, boss))
                current_attempt = cleaned_line
                current_events = []
                current_timestamp = None  # Reset timestamp for new attempt
                current_pull_number = pull_number
            continue
            
        # If we're in a boss attempt, only keep relevant lines
        if current_attempt:
            if is_timestamp(cleaned_line):
                current_timestamp = cleaned_line
            elif boss.is_boss_event(cleaned_line):
                current_events.append("  " + cleaned_line)  # Indent events
    
    # Add the last attempt if there is one
    if current_attempt and current_timestamp:  # Only add if we have both header and timestamp
        # Remove any "Part X" from the attempt header
        current_attempt = re.sub(r'\s*-\s*Part\s+\d+', '', current_attempt)
        attempts.append(Attempt(current_attempt, current_events, current_timestamp, boss))
    
    # Filter out any attempts that don't have events (might be from other bosses)
    attempts = [attempt for attempt in attempts if attempt.events]
    
    # Sort attempts by timestamp
    attempts.sort(key=lambda x: x.datetime)
    
    # Generate the cleaned output with renumbered attempts
    cleaned_lines = []
    for i, attempt in enumerate(attempts, 1):
        cleaned_lines.extend(attempt.format_attempt(i))
        cleaned_lines.append("")  # Add blank line between attempts
    
    # Analyze player statistics
    player_stats = analyze_player_stats(attempts)
    stats_output = format_player_stats(player_stats)
    
    # Analyze non-player mistakes
    non_player_mistakes = boss.analyze_non_player_mistakes(attempts)
    mistakes_output = format_non_player_mistakes(non_player_mistakes)
    
    # Write the cleaned data and statistics to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write the attempt data
        f.writelines(line + "\n" for line in cleaned_lines)
        f.write("\n" + "="*50 + "\n\n")  # Separator
        # Write the player statistics
        f.write(stats_output)
        # Write the non-player mistakes summary
        f.write(mistakes_output)
    
    # Export to CSV
    export_to_csv(attempts, csv_file)
    print(f"Data has been cleaned and saved to {output_file}")
    print(f"CSV data has been saved to {csv_file}")
    print(f"Detected boss: {boss.name}")
    print("\nVerifying cleaning process...")
    verify_cleaning(input_file, output_file)
    print("Verification results have been saved to verification_results.txt")


def verify_cleaning(input_file: str, output_file: str) -> None:
    """Verify the cleaning process."""
    with open(input_file, 'r', encoding='utf-8') as f:
        input_lines = f.readlines()
    with open(output_file, 'r', encoding='utf-8') as f:
        output_lines = f.readlines()
    
    # Skip the experimental warning line in input
    input_lines = [line for line in input_lines if ":warning: Experimental :warning:" not in line]
    
    # Remove all emoji patterns (text surrounded by colons) from input
    input_lines = [re.sub(r':[^:]+:', '', line).strip() for line in input_lines]
    input_lines = [line for line in input_lines if line]  # Remove empty lines
    
    # Remove statistics section from output
    stats_start = output_lines.index("="*50 + "\n")
    output_lines = output_lines[:stats_start]
    output_lines = [line.strip() for line in output_lines if line.strip()]
    
    # Verify that all output lines exist in input
    missing_lines = []
    for line in output_lines:
        if line not in input_lines:
            missing_lines.append(line)
    
    # Write verification results
    with open("verification_results.txt", 'w', encoding='utf-8') as f:
        f.write("Verification Results:\n\n")
        if not missing_lines:
            f.write("All lines in the cleaned output exist in the original input.\n")
        else:
            f.write("The following lines in the cleaned output were not found in the original input:\n")
            for line in missing_lines:
                f.write(f"- {line}\n")
        
        # Add statistics about the cleaning process
        f.write("\nCleaning Statistics:\n")
        f.write(f"Original input lines: {len(input_lines)}\n")
        f.write(f"Cleaned output lines: {len(output_lines)}\n")
        f.write(f"Lines removed: {len(input_lines) - len(output_lines)}\n")
        if missing_lines:
            f.write(f"Lines not found in original: {len(missing_lines)}\n")


if __name__ == "__main__":
    input_file = "data.txt"
    output_file = "cleaned_data.txt"
    csv_file = "cleaned_data.csv"
    
    # Automatically detect boss from content
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
        boss = detect_boss_from_content(content)
    
    print(f"Auto-detected boss: {boss.name}")
    print(f"Boss mechanics: {', '.join(boss.mechanics)}")
    
    clean_data(input_file, output_file, csv_file, boss)
