import re

def count_unique_attempts():
    with open('data.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all Gallywix attempt headers
    pattern = r'Gallywix #(\d+)\s+\([^)]+\)'
    matches = re.findall(pattern, content)
    
    # Count unique attempt numbers
    unique_attempts = set()
    for match in matches:
        unique_attempts.add(int(match))
    
    print(f"Total Gallywix attempt headers found: {len(matches)}")
    print(f"Unique attempt numbers: {len(unique_attempts)}")
    print(f"Max attempt number: {max(unique_attempts)}")
    
    # Count by session
    lines = content.split('\n')
    session_attempts = {}
    current_session = None
    
    for line in lines:
        if 'Log Analysis' in line and '—' in line:
            # Extract date from session header
            date_match = re.search(r'—\s+(\d+/\d+/\d+)', line)
            if date_match:
                current_session = date_match.group(1)
                session_attempts[current_session] = set()
        
        if 'Gallywix #' in line:
            attempt_match = re.search(r'Gallywix #(\d+)', line)
            if attempt_match and current_session:
                session_attempts[current_session].add(int(attempt_match.group(1)))
    
    print("\nAttempts by session:")
    total_unique = set()
    for session, attempts in session_attempts.items():
        print(f"{session}: {len(attempts)} unique attempts (max #: {max(attempts) if attempts else 0})")
        total_unique.update(attempts)
    
    print(f"\nTotal unique attempts across all sessions: {len(total_unique)}")
    print(f"Attempt numbers: {sorted(total_unique)}")

if __name__ == "__main__":
    count_unique_attempts() 