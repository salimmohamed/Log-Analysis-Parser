import re
from datetime import datetime

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
    
    # Write the cleaned data to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(line + "\n" for line in cleaned_lines)

if __name__ == "__main__":
    input_file = "data.txt"
    output_file = "cleaned_data.txt"
    clean_data(input_file, output_file)
    print(f"Data has been cleaned and saved to {output_file}") 