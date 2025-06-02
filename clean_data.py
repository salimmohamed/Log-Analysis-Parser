import re
from datetime import datetime
from collections import defaultdict
import csv
from abc import ABC, abstractmethod

class Boss(ABC):
    def __init__(self, name):
        self.name = name
        self.mechanics = []
        self.death_causes = []
        self.non_player_mistakes = []

    @abstractmethod
    def is_attempt_header(self, line):
        """Check if line is a boss attempt header"""
        pass

    @abstractmethod
    def is_boss_event(self, line):
        """Check if line is a boss-specific event"""
        pass

    @abstractmethod
    def extract_player_death(self, line):
        """Extract player name and death cause from event line"""
        pass

    @abstractmethod
    def analyze_non_player_mistakes(self, attempts):
        """Analyze non-player mistakes for this boss"""
        pass

    def format_attempt(self, attempt_number, header, duration):
        """Format attempt header with new number"""
        return f"{self.name} #{attempt_number}   ({duration}"

class MugZee(Boss):
    def __init__(self):
        super().__init__("Mug'Zee")
        self.mechanics = [
            "Unstable Cluster Bomb",
            "Goblin-Guided Rocket",
            "Boss enrage",
            "Goon enrage"
        ]
        self.death_causes = [
            "Frostshatter Spear",
            "Stormfury stun",
            "Goon's frontal",
            "Molten Golden Knuckles frontal",
            "electrocution line",
            "popping a mine"
        ]
        self.non_player_mistakes = [
            "Unstable Cluster Bomb not soaked",
            "Goblin-Guided Rocket under-soaked",
            "Boss enrage",
            "Goon enrage",
            "popping mine"
        ]

    def is_attempt_header(self, line):
        return "Mug'Zee #" in line

    def is_boss_event(self, line):
        return any(event in line for event in [
            "died to",
            "was not soaked",
            "was soaked by fewer than",
            "Boss enraged",
            "Goon enraged",
            "No mistakes found"
        ])

    def extract_player_death(self, event):
        if "died to" in event:
            match = re.search(r"(\w+)\s+died to (.*?)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), match.group(2)
        return None, None

    def analyze_non_player_mistakes(self, attempts):
        mistakes = defaultdict(int)
        for attempt in attempts:
            for event in attempt.events:
                if "was not soaked" in event:
                    mistakes["Cluster bomb not soaked"] += 1
                elif "was soaked by fewer than" in event:
                    mistakes["Rocket under-soaked"] += 1
                elif "Boss enraged" in event:
                    mistakes["Boss enrage"] += 1
                elif "Goon enraged" in event:
                    mistakes["Goon enrage"] += 1
        return mistakes

class StixBunkjunker(Boss):
    def __init__(self):
        super().__init__("Stix Bunkjunker")
        self.mechanics = [
            "ball",
            "bombshell",
            "scrapmaster"
        ]
        self.death_causes = [
            "ball expired",
            "hit a bombshell",
            "Bombshell did not die in time",
            "missed their Scrapmaster"
        ]
        self.non_player_mistakes = [
            "ball expired",
            "hit a bombshell",
            "Bombshell did not die in time",
            "missed their Scrapmaster"
        ]

    def is_attempt_header(self, line):
        return "Stix Bunkjunker #" in line

    def is_boss_event(self, line):
        return any(event in line for event in [
            "died to",
            "ball expired",
            "hit a bombshell",
            "Bombshell did not die in time",
            "missed their Scrapmaster",
            "No mistakes found"
        ])

    def extract_player_death(self, event):
        # missed their Scrapmaster on <marker>
        match = re.match(r"\s*(\w+) missed their Scrapmaster on (\w+) \(([^)]+)\)", event)
        if match:
            player = match.group(1)
            marker = match.group(2)
            return player, f"missed their Scrapmaster on {marker}"
        # hit a bombshell
        match = re.match(r"\s*(\w+) hit a bombshell \(([^)]+)\)", event)
        if match:
            player = match.group(1)
            return player, "hit a bombshell"
        # ball expired
        match = re.match(r"\s*(\w+)'s ball expired \(([^)]+)\)", event)
        if match:
            player = match.group(1)
            return player, "ball expired"
        # died to
        if "died to" in event:
            match = re.search(r"(\w+)\s+died to (.*?)\s+\(([^)]+)\)", event)
            if match:
                return match.group(1), match.group(2)
        return None, None

    def analyze_non_player_mistakes(self, attempts):
        mistakes = defaultdict(int)
        for attempt in attempts:
            for event in attempt.events:
                if "ball expired" in event:
                    mistakes["Ball expired"] += 1
                elif "hit a bombshell" in event:
                    mistakes["Hit bombshell"] += 1
                elif "Bombshell did not die in time" in event:
                    mistakes["Bombshell not killed"] += 1
                elif "missed their Scrapmaster" in event:
                    mistakes["Missed scrapmaster"] += 1
        return mistakes

def is_timestamp(line):
    # Match [HH:MM:SS] or [HH:MM:SS.mmm] or M/D/YYYY H:MM AM/PM or M/D/YYYY at H:MM AM/PM
    return bool(
        re.match(r'\[\d{2}:\d{2}:\d{2}(\.\d{3})?\]', line.strip()) or
        re.match(r'\d{1,2}/\d{1,2}/\d{4}(\s+at)?\s+\d{1,2}:\d{2}\s*[AP]M', line.strip())
    )

def parse_timestamp(line):
    # Try [HH:MM:SS(.mmm)]
    match = re.search(r'\[(\d{2}:\d{2}:\d{2}(\.\d{3})?)\]', line)
    if match:
        time_str = match.group(1)
        try:
            if '.' in time_str:
                time_str, ms = time_str.split('.')
                dt = datetime.strptime(time_str, '%H:%M:%S')
                dt = dt.replace(microsecond=int(ms) * 1000)
            else:
                dt = datetime.strptime(time_str, '%H:%M:%S')
            return dt
        except ValueError:
            return None
    # Try M/D/YYYY H:MM AM/PM or M/D/YYYY at H:MM AM/PM
    match = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})(?:\s+at)?\s+(\d{1,2}):(\d{2})\s*([AP]M)', line.strip())
    if match:
        month, day, year, hour, minute, ampm = match.groups()
        month, day, year, hour, minute = map(int, [month, day, year, hour, minute])
        if ampm == 'PM' and hour != 12:
            hour += 12
        elif ampm == 'AM' and hour == 12:
            hour = 0
        try:
            return datetime(year, month, day, hour, minute)
        except ValueError:
            return None
    return None

def parse_attempt_duration(duration_str):
    # Extract minutes and seconds from duration string like "(4:33)"
    match = re.match(r"\((\d+):(\d+)\)", duration_str)
    if match:
        minutes, seconds = map(int, match.groups())
        return minutes * 60 + seconds
    return 0

class Attempt:
    def __init__(self, header, events, timestamp, boss):
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

    def format_attempt(self, attempt_number):
        # Format the attempt with the new number
        duration = self.header.split('(')[1]
        return [self.boss.format_attempt(attempt_number, self.header, duration)] + self.events + [self.timestamp]

def analyze_player_stats(attempts):
    player_stats = defaultdict(lambda: defaultdict(int))
    
    for attempt in attempts:
        for event in attempt.events:
            player, cause = attempt.boss.extract_player_death(event)
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
    popping_mine_count = 0
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
        # Count popping mine deaths as a non-player mistake
        for event in attempt.events:
            if "died to popping a mine" in event:
                popping_mine_count += 1
    if popping_mine_count > 0:
        non_player_mistakes["popping mine"] = popping_mine_count
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
    # Remove any emoji patterns
    name = re.sub(r':[^:]+:', '', name)
    # Remove any extra whitespace
    name = name.strip()
    # Convert to title case for consistency
    return name.title()

def write_csv(rows, output_file):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Pull #', 'Date', 'Duration', 'Events', 'Player Deaths'])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {output_file}")

def export_to_csv(attempts, output_file):
    input_file = 'cleaned_data.txt'
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]

    # Find the separator line for summary/statistics
    try:
        stats_start = lines.index('='*50)
    except ValueError:
        stats_start = len(lines)

    # Parse attempts section
    attempts_lines = lines[:stats_start]
    summary_lines = lines[stats_start:]

    # Parse attempts into CSV rows
    rows = []
    i = 0
    while i < len(attempts_lines):
        line = attempts_lines[i]
        if line.startswith('Stix Bunkjunker #') or line.startswith("Mug'Zee #"):
            # Header line
            header = line
            events = []
            i += 1
            # Collect events until we hit a timestamp or blank line
            while i < len(attempts_lines) and attempts_lines[i] and not attempts_lines[i][0].isdigit() and not attempts_lines[i].startswith('Stix Bunkjunker #') and not attempts_lines[i].startswith("Mug'Zee #"):
                events.append(attempts_lines[i].strip())
                i += 1
            # Timestamp line
            timestamp = ''
            if i < len(attempts_lines) and attempts_lines[i] and attempts_lines[i][0].isdigit():
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
            # Events and deaths
            event_strs = []
            deaths = []
            for ev in events:
                if 'Death)' in ev or 'expired' in ev or 'missed their Scrapmaster' in ev or 'hit a bombshell' in ev or 'Bombshell did not die in time' in ev:
                    deaths.append(ev)
                else:
                    event_strs.append(ev)
            # For this format, just join all events as one string, and all deaths as one string
            rows.append([
                pull_num,
                timestamp.split()[0] if timestamp else '',
                duration,
                '; '.join(event_strs) if event_strs else '',
                '; '.join(deaths) if deaths else ''
            ])
        else:
            i += 1

    # Write to CSV (main table only)
    write_csv(rows, output_file)

    # Write summary/statistics to a separate txt file
    with open('cleaned_data_summary.txt', 'w', encoding='utf-8') as f:
        for line in summary_lines:
            f.write(line + '\n')

def clean_data(input_file, output_file, csv_file, boss):
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
        # For StixBunkjunker missed Scrapmaster, keep only the marker as a word, strip all other emojis
        if isinstance(boss, StixBunkjunker) and 'missed their Scrapmaster on' in line:
            # Extract marker
            marker_match = re.search(r':Marker_(\w+):', line)
            if marker_match:
                marker = marker_match.group(1).lower()
                # Remove all emojis
                cleaned_line = re.sub(r':[^:]+:', '', line)
                # Insert marker word at the end
                cleaned_line = re.sub(r'missed their Scrapmaster on\s*', f'missed their Scrapmaster on {marker} ', cleaned_line)
                cleaned_line = cleaned_line.strip()
            else:
                # If no marker found, just remove emojis
                cleaned_line = re.sub(r':[^:]+:', '', line)
        else:
            # Remove all emoji patterns (text surrounded by colons)
            cleaned_line = re.sub(r':[^:]+:', '', line).strip()
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
    print("\nVerifying cleaning process...")
    verify_cleaning(input_file, output_file)
    print("Verification results have been saved to verification_results.txt")

def verify_cleaning(input_file, output_file):
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
    
    # Create boss instance based on input file content
    with open(input_file, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        if "Mug'Zee" in first_line:
            boss = MugZee()
        elif "Stix Bunkjunker" in first_line:
            boss = StixBunkjunker()
        else:
            raise ValueError("Unknown boss type in input file")
    
    clean_data(input_file, output_file, csv_file, boss) 