"""
Non-player mistakes analysis.
"""

from collections import defaultdict
from typing import List, Dict, Any


def format_non_player_mistakes(mistakes: Dict[str, int]) -> str:
    """Format non-player mistakes for output."""
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
