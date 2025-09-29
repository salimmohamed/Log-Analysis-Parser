"""
Boss detection and loading.
"""

from .base import Boss
from .nexus_king import NexusKing
from .archived.mugzee import MugZee
from .archived.stixbunkjunker import StixBunkjunker
from .archived.gallywix import Gallywix

def detect_boss_from_content(content: str) -> Boss:
    """Figure out which boss we're dealing with."""
    content_lower = content.lower()
    
    # Check for boss patterns (newest first)
    if 'nexus-king' in content_lower or 'Nexus-King' in content:
        return NexusKing()
    elif "mug'zee" in content_lower or 'mugzee' in content_lower:
        return MugZee()
    elif 'stix bunkjunker' in content_lower:
        return StixBunkjunker()
    elif 'gallywix' in content_lower:
        return Gallywix()
    else:
        raise ValueError(f"Unknown boss type in content. Available bosses: nexus-king, mugzee, stix-bunkjunker, gallywix")
