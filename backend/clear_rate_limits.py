"""
Clear rate limiter in-memory state for testing.
Import and run after server starts.
"""
def clear_rate_limits():
    try:
        from app.services.rate_limiter import _events
        _events.clear()
        print("✅ Rate limits cleared")
        return True
    except Exception as e:
        print(f"❌ Failed to clear rate limits: {e}")
        return False


if __name__ == "__main__":
    clear_rate_limits()
