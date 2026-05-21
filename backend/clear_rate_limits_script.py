"""
Clear rate limit cache to allow immediate testing
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.rate_limiter import rate_limit_cache

def clear_rate_limits():
    """Clear all rate limit entries"""
    print("Clearing rate limit cache...")
    initial_count = len(rate_limit_cache)
    rate_limit_cache.clear()
    print(f"✓ Cleared {initial_count} rate limit entries")
    print("You can now retry signup/login immediately")

if __name__ == "__main__":
    print("="*60)
    print("Clear Rate Limits")
    print("="*60)
    clear_rate_limits()
    print("="*60)
