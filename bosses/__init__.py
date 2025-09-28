"""
Boss registry system for automatic boss detection and loading.
"""

from .base import Boss
from .nexus_king import NexusKing
from .archived.mugzee import MugZee
from .archived.stixbunkjunker import StixBunkjunker
from .archived.gallywix import Gallywix

# Registry of all available bosses
BOSS_REGISTRY = {
    'nexus-king': NexusKing,
    'mugzee': MugZee,
    'stix-bunkjunker': StixBunkjunker,
    'gallywix': Gallywix,
}

def detect_boss_from_content(content: str) -> Boss:
    """
    Automatically detect which boss is in the content and return appropriate instance.
    """
    content_lower = content.lower()
    
    # Check for boss patterns in order of priority (newest first)
    if 'nexus-king' in content_lower or 'Nexus-King' in content:
        return NexusKing()
    elif "mug'zee" in content_lower or 'mugzee' in content_lower:
        return MugZee()
    elif 'stix bunkjunker' in content_lower:
        return StixBunkjunker()
    elif 'gallywix' in content_lower:
        return Gallywix()
    else:
        raise ValueError(f"Unknown boss type in content. Available bosses: {list(BOSS_REGISTRY.keys())}")

def get_boss_by_name(boss_name: str) -> Boss:
    """
    Get a boss instance by name.
    """
    if boss_name.lower() not in BOSS_REGISTRY:
        raise ValueError(f"Unknown boss: {boss_name}. Available: {list(BOSS_REGISTRY.keys())}")
    
    return BOSS_REGISTRY[boss_name.lower()]()
