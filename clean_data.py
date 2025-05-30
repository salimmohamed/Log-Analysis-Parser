import re
from datetime import datetime
from collections import defaultdict
import csv

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

def parse_timestamp(timestamp_str):
    # Convert timestamp string to datetime object
    return datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M %p")

def parse_attempt_duration(duration_str):
    # Extract minutes and seconds from duration string like "(4:33)"
    match = re.match(r"\((\d+):(\d+)\)", duration_str)
    if match:
        minutes, seconds = map(int, match.groups())
        return minutes * 60 + seconds
    return 0

class Attempt:
    def __init__(self, header, events, timestamp):
        self.header = header
        self.events = events
        self.timestamp = timestamp
        self.datetime = parse_timestamp(timestamp)
        # Extract duration from header
        duration_match = re.search(r"\((\d+):(\d+)\)", header)
        if duration_match:
            minutes, seconds = map(int, duration_match.groups())
            self.duration = minutes * 60 + seconds
        else:
            self.duration = 0

    def format_attempt(self, attempt_number):
        # Format the attempt with the new number
        new_header = f"Mug'Zee #{attempt_number}   ({self.header.split('(')[1]}"
        return [new_header] + self.events + [self.timestamp]

def analyze_player_stats(attempts):
    player_stats = defaultdict(lambda: defaultdict(int))
    
    for attempt in attempts:
        for event in attempt.events:
            if "died to" in event:
                player, cause = extract_player_death(event)
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

def analyze_non_player_mistakes(attempts):
    non_player_mistakes = defaultdict(int)
    
    for attempt in attempts:
        for event in attempt.events:
            if "died to" not in event:  # Only count non-death events
                # Extract the mistake type
                if "was not soaked" in event:
                    non_player_mistakes["Unstable Cluster Bomb not soaked"] += 1
                elif "was soaked by fewer than" in event:
                    non_player_mistakes["Goblin-Guided Rocket under-soaked"] += 1
                elif "Boss enraged" in event:
                    non_player_mistakes["Boss enrage"] += 1
                elif "Goon enraged" in event:
                    non_player_mistakes["Goon enrage"] += 1
    
    return non_player_mistakes

def format_non_player_mistakes(mistakes):
    if not mistakes:
        return "No non-player mistakes found."
        
    output = ["\nNon-Player Mistakes Summary:"]
    total_mistakes = sum(mistakes.values())
    output.append(f"Total non-player mistakes: {total_mistakes}")
    output.append("")
    
    # Sort mistakes by frequency
    sorted_mistakes = sorted(mistakes.items(), key=lambda x: x[1], reverse=True)
    for mistake, count in sorted_mistakes:
        output.append(f"{mistake}: {count} times")
    
    return "\n".join(output)

def ordinal(n):
    # Returns 1st, 2nd, 3rd, 4th, etc.
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def normalize_player_name(name):
    # Replace special characters with their ASCII equivalents
    replacements = {
        'é': 'e',
        'ò': 'o',
        'ó': 'o',
        'à': 'a',
        'á': 'a',
        'è': 'e',
        'ì': 'i',
        'í': 'i',
        'ù': 'u',
        'ú': 'u',
        'ñ': 'n',
        'ç': 'c',
        'ë': 'e',
        'ï': 'i',
        'ü': 'u',
        'ÿ': 'y',
        'œ': 'oe',
        'æ': 'ae',
        'ß': 'ss'
    }
    normalized = name
    for special, ascii_char in replacements.items():
        normalized = normalized.replace(special, ascii_char)
    return normalized

def export_to_csv(attempts, output_file):
    headers = [
        'Pull #',
        'Date',
        'Duration',
        'Events',
        'Player Deaths'
    ]
    attempts_by_day = defaultdict(list)
    for attempt in attempts:
        day = attempt.datetime.strftime("%m/%d/%Y")
        attempts_by_day[day].append(attempt)
    sorted_days = sorted(attempts_by_day.keys(), key=lambda x: datetime.strptime(x, "%m/%d/%Y"))
    rows = []
    attempt_number = 1
    for day in sorted_days:
        day_attempts = attempts_by_day[day]
        day_attempts.sort(key=lambda x: x.datetime)
        for attempt in day_attempts:
            # Process events - include both player deaths and raid events
            simplified_events = []
            has_non_player_mistake = False
            for event in attempt.events:
                event = event.strip()
                if "died to" in event:
                    match = re.search(r"(\w+)\s+died to (.*?)\s+\(([^)]+)\)", event)
                    if match:
                        player, cause, time = match.groups()
                        # Normalize player name and simplify the cause text
                        player = normalize_player_name(player)
                        cause = cause.replace("the ", "").replace("Frostshatter Spear", "frost spear").replace("popping a mine", "mine").replace("the Stormfury stun", "stun").replace("the Goon's frontal", "goon frontal").replace("the Molten Golden Knuckles frontal", "boss frontal")
                        simplified_events.append(f"{player} {cause}")
                elif "was not soaked" in event:
                    simplified_events.append("cluster bomb not soaked")
                    has_non_player_mistake = True
                elif "was soaked by fewer than" in event:
                    simplified_events.append("rocket under-soaked")
                    has_non_player_mistake = True
                elif "Boss enraged" in event:
                    simplified_events.append("boss enrage")
                    has_non_player_mistake = True
                elif "Goon enraged" in event:
                    simplified_events.append("goon enrage")
                    has_non_player_mistake = True
                elif "No mistakes found" in event:
                    simplified_events.append("messed up so bad bot couldn't find out")
            
            # Process player deaths for the detailed column
            death_times = []
            for event in attempt.events:
                if "died to" in event:
                    match = re.search(r"(\w+)\s+died to.*?\(([^)]+)\)", event)
                    if match:
                        player, time = match.groups()
                        # Normalize player name
                        player = normalize_player_name(player)
                        death_times.append((player, time))
            formatted_deaths = []
            for i, (player, time) in enumerate(death_times, 1):
                formatted_deaths.append(f"{player} ({time}) ({ordinal(i)} Death)")
            
            # Convert duration from seconds to minutes:seconds format
            minutes = attempt.duration // 60
            seconds = attempt.duration % 60
            duration_formatted = f"{minutes}:{seconds:02d}"
            
            # Determine the deaths column value
            deaths_column = '; '.join(formatted_deaths) if formatted_deaths else ("insta-wipe" if has_non_player_mistake else "messed up so bad bot couldn't find out")
            
            rows.append([
                attempt_number,
                attempt.datetime.strftime("%m/%d/%Y"),
                duration_formatted,
                '; '.join(simplified_events) if simplified_events else "messed up so bad bot couldn't find out",
                deaths_column
            ])
            attempt_number += 1
    # Write the main table
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
        # Add a blank line, then the raid mistakes tally
        f.write("\nRaid Mistakes Tally:\n")
        writer2 = csv.writer(f)
        writer2.writerow(["Mistake Type", "Count"])
        non_player_mistakes = analyze_non_player_mistakes(attempts)
        for mistake, count in sorted(non_player_mistakes.items(), key=lambda x: x[1], reverse=True):
            writer2.writerow([mistake, count])
            
        # Add player mistake tally
        f.write("\nPlayer Mistake Tally:\n")
        writer3 = csv.writer(f)
        writer3.writerow(["Player", "Total Mistakes"])
        
        # Count mistakes for each player
        player_mistakes = defaultdict(int)
        # Add mechanic-specific mistake tracking
        mechanic_mistakes = defaultdict(lambda: defaultdict(int))
        
        for attempt in attempts:
            for event in attempt.events:
                if "died to" in event:
                    match = re.search(r"(\w+)\s+died to (.*?)\s+\([^)]+\)", event)
                    if match:
                        player = normalize_player_name(match.group(1))
                        mechanic = match.group(2).strip()
                        # Simplify mechanic names for consistency
                        mechanic = mechanic.replace("the ", "").replace("Frostshatter Spear", "frost spear").replace("popping a mine", "mine").replace("the Stormfury stun", "stun").replace("the Goon's frontal", "goon frontal").replace("the Molten Golden Knuckles frontal", "boss frontal")
                        player_mistakes[player] += 1
                        mechanic_mistakes[mechanic][player] += 1
        
        # Sort players by total mistakes (descending)
        sorted_players = sorted(player_mistakes.items(), key=lambda x: x[1], reverse=True)
        for player, count in sorted_players:
            writer3.writerow([player, count])
            
        # Add mechanic mistake tally
        f.write("\nMechanic Mistake Tally:\n")
        writer4 = csv.writer(f)
        writer4.writerow(["Mechanic", "Worst Offenders"])
        
        # Sort mechanics alphabetically for consistent output
        for mechanic in sorted(mechanic_mistakes.keys()):
            # Get top 3 offenders for this mechanic
            offenders = sorted(mechanic_mistakes[mechanic].items(), key=lambda x: x[1], reverse=True)[:3]
            offender_str = "; ".join(f"{player} ({count})" for player, count in offenders)
            writer4.writerow([mechanic, offender_str])

def clean_data(input_file, output_file):
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    attempts = []
    current_attempt = None
    current_events = []
    
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
            # Save previous attempt if it exists
            if current_attempt:
                attempts.append(Attempt(current_attempt, current_events, current_timestamp))
            current_attempt = cleaned_line
            current_events = []
            continue
            
        # If we're in a boss attempt, only keep relevant lines
        if current_attempt:
            if is_timestamp(cleaned_line):
                current_timestamp = cleaned_line
            elif is_boss_event(cleaned_line):
                current_events.append("  " + cleaned_line)  # Indent events
    
    # Add the last attempt if there is one
    if current_attempt:
        attempts.append(Attempt(current_attempt, current_events, current_timestamp))
    
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
    non_player_mistakes = analyze_non_player_mistakes(attempts)
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
    csv_output_file = output_file.replace('.txt', '.csv')
    export_to_csv(attempts, csv_output_file)

def verify_cleaning(original_file, cleaned_file):
    verification_results = ["Starting verification process..."]
    
    # Read both files
    with open(original_file, 'r', encoding='utf-8') as f:
        original_lines = [line.strip() for line in f.readlines() if line.strip()]
    with open(cleaned_file, 'r', encoding='utf-8') as f:
        cleaned_lines = [line.strip() for line in f.readlines() if line.strip()]
    
    # Extract attempts from both files
    original_attempts = []
    cleaned_attempts = []
    current_attempt = []
    current_cleaned_attempt = []
    
    for line in original_lines:
        if is_boss_attempt_header(line):
            if current_attempt:
                original_attempts.append(current_attempt)
            current_attempt = [line]
        elif current_attempt and (is_timestamp(line) or is_boss_event(line)):
            # Remove emojis and experimental warning
            cleaned_line = re.sub(r':[^:]+:', '', line).strip()
            if cleaned_line and ":warning: Experimental :warning:" not in line:
                current_attempt.append(cleaned_line)
    if current_attempt:
        original_attempts.append(current_attempt)
    
    for line in cleaned_lines:
        if is_boss_attempt_header(line):
            if current_cleaned_attempt:
                cleaned_attempts.append(current_cleaned_attempt)
            current_cleaned_attempt = [line]
        elif current_cleaned_attempt and (is_timestamp(line) or is_boss_event(line)):
            current_cleaned_attempt.append(line)
    if current_cleaned_attempt:
        cleaned_attempts.append(current_cleaned_attempt)
    
    # Compare number of attempts
    verification_results.append(f"\nAttempt count comparison:")
    verification_results.append(f"Original attempts: {len(original_attempts)}")
    verification_results.append(f"Cleaned attempts: {len(cleaned_attempts)}")
    
    if len(original_attempts) != len(cleaned_attempts):
        verification_results.append("WARNING: Number of attempts doesn't match!")
    
    # Compare timestamps
    original_timestamps = set()
    cleaned_timestamps = set()
    
    for attempt in original_attempts:
        for line in attempt:
            if is_timestamp(line):
                original_timestamps.add(line)
    
    for attempt in cleaned_attempts:
        for line in attempt:
            if is_timestamp(line):
                cleaned_timestamps.add(line)
    
    verification_results.append(f"\nTimestamp comparison:")
    verification_results.append(f"Original unique timestamps: {len(original_timestamps)}")
    verification_results.append(f"Cleaned unique timestamps: {len(cleaned_timestamps)}")
    
    if original_timestamps != cleaned_timestamps:
        verification_results.append("WARNING: Timestamps don't match exactly!")
        verification_results.append("Timestamps in original but not in cleaned: " + str(original_timestamps - cleaned_timestamps))
        verification_results.append("Timestamps in cleaned but not in original: " + str(cleaned_timestamps - original_timestamps))
    
    # Compare events
    original_events = defaultdict(int)
    cleaned_events = defaultdict(int)
    
    for attempt in original_attempts:
        for line in attempt:
            if is_boss_event(line) and "died to" not in line:
                event = re.sub(r':[^:]+:', '', line).strip()
                if event and ":warning: Experimental :warning:" not in event:
                    original_events[event] += 1
    
    for attempt in cleaned_attempts:
        for line in attempt:
            if is_boss_event(line) and "died to" not in line:
                cleaned_events[line] += 1
    
    verification_results.append(f"\nEvent comparison:")
    verification_results.append("Events in original but not in cleaned:")
    for event, count in original_events.items():
        if event not in cleaned_events or cleaned_events[event] != count:
            verification_results.append(f"  {event}: {count} times in original, {cleaned_events.get(event, 0)} times in cleaned")
    
    verification_results.append("\nEvents in cleaned but not in original:")
    for event, count in cleaned_events.items():
        if event not in original_events or original_events[event] != count:
            verification_results.append(f"  {event}: {count} times in cleaned, {original_events.get(event, 0)} times in original")
    
    # Compare player deaths
    original_deaths = defaultdict(lambda: defaultdict(int))
    cleaned_deaths = defaultdict(lambda: defaultdict(int))
    
    for attempt in original_attempts:
        for line in attempt:
            if "died to" in line:
                player, cause = extract_player_death(line)
                if player and cause:
                    original_deaths[player][cause] += 1
    
    for attempt in cleaned_attempts:
        for line in attempt:
            if "died to" in line:
                player, cause = extract_player_death(line)
                if player and cause:
                    cleaned_deaths[player][cause] += 1
    
    verification_results.append(f"\nPlayer death comparison:")
    verification_results.append("Deaths in original but not in cleaned:")
    for player in original_deaths:
        for cause, count in original_deaths[player].items():
            if player not in cleaned_deaths or cause not in cleaned_deaths[player] or cleaned_deaths[player][cause] != count:
                verification_results.append(f"  {player} - {cause}: {count} times in original, {cleaned_deaths.get(player, {}).get(cause, 0)} times in cleaned")
    
    verification_results.append("\nDeaths in cleaned but not in original:")
    for player in cleaned_deaths:
        for cause, count in cleaned_deaths[player].items():
            if player not in original_deaths or cause not in original_deaths[player] or original_deaths[player][cause] != count:
                verification_results.append(f"  {player} - {cause}: {count} times in cleaned, {original_deaths.get(player, {}).get(cause, 0)} times in original")
    
    # Write verification results to file
    with open("verification_results.txt", 'w', encoding='utf-8') as f:
        f.write("\n".join(verification_results))
    
    return verification_results

if __name__ == "__main__":
    input_file = "data.txt"
    output_file = "cleaned_data.txt"
    clean_data(input_file, output_file)
    print(f"Data has been cleaned and saved to {output_file}")
    print(f"CSV data has been saved to {output_file.replace('.txt', '.csv')}")
    print("\nVerifying cleaning process...")
    verify_cleaning(input_file, output_file)
    print("Verification results have been saved to verification_results.txt") 