import re
from datetime import datetime
from collections import defaultdict

def is_boss_attempt_header(line):
    # Matches lines like "Mug'Zee #1   (4:33)"
    return bool(re.match(r"Mug'Zee #\d+\s+\(\d+:\d+\)", line.strip()))

def is_timestamp(line):
    # Matches lines like "5/24/2025 6:40 PM"
    return bool(re.match(r"\d+/\d+/\d{4}\s+\d+:\d+\s+[AP]M", line.strip()))

def is_boss_event(line):
    # Matches lines that contain boss mechanics or deaths
    boss_events = [
        "died to",
        "was not soaked",
        "was soaked by fewer than",
        "Boss enraged",
        "Goon enraged",
        "No mistakes found"
    ]
    return any(event in line for event in boss_events)

def extract_player_death(line):
    # Extract player name and death cause from a death event line
    match = re.match(r"\s*(\w+)\s+died to (.*?)\s+\(.*\)", line)
    if match:
        return match.group(1), match.group(2)
    return None, None

def analyze_player_stats(cleaned_lines):
    player_stats = defaultdict(lambda: defaultdict(int))
    
    for line in cleaned_lines:
        if "died to" in line:
            player, cause = extract_player_death(line)
            if player and cause:
                player_stats[player][cause] += 1
    
    return player_stats

def format_player_stats(player_stats):
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

def clean_data(input_file, output_file):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    current_attempt = []
    in_boss_attempt = False
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Skip the experimental warning line
        if ":warning: Experimental :warning:" in line:
            continue
            
        # Remove all emoji patterns (text surrounded by colons)
        cleaned_line = re.sub(r':[^:]+:', '', line).strip()
        
        # Skip if line is empty after cleaning
        if not cleaned_line:
            continue
            
        # Check if this is a boss attempt header
        if is_boss_attempt_header(cleaned_line):
            # If we were processing a previous attempt, save it
            if current_attempt:
                cleaned_lines.extend(current_attempt)
                cleaned_lines.append("")  # Add a blank line between attempts
            current_attempt = [cleaned_line]
            in_boss_attempt = True
            continue
            
        # If we're in a boss attempt, only keep relevant lines
        if in_boss_attempt:
            if is_timestamp(cleaned_line):
                current_attempt.append(cleaned_line)
                in_boss_attempt = False  # End of attempt
            elif is_boss_event(cleaned_line):
                current_attempt.append("  " + cleaned_line)  # Indent events
    
    # Add the last attempt if there is one
    if current_attempt:
        cleaned_lines.extend(current_attempt)
    
    # Analyze player statistics
    player_stats = analyze_player_stats(cleaned_lines)
    stats_output = format_player_stats(player_stats)
    
    # Write the cleaned data and statistics to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write the attempt data
        f.writelines(line + "\n" for line in cleaned_lines)
        f.write("\n" + "="*50 + "\n\n")  # Separator
        # Write the player statistics
        f.write(stats_output)

if __name__ == "__main__":
    input_file = "data.txt"
    output_file = "cleaned_data.txt"
    clean_data(input_file, output_file)
    print(f"Data has been cleaned and saved to {output_file}") 