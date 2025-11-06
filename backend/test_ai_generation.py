"""
Test AI generation endpoints to diagnose issues
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_ai_bullets():
    """Test bullet points generation"""
    print("=" * 60)
    print("TEST: AI Bullet Points Generation")
    print("=" * 60)
    
    # First login to get auth cookie
    login_data = {"email": "test@example.com", "password": "password123"}
    login_resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code}")
        print(login_resp.text)
        return False
    
    cookies = login_resp.cookies
    print(f"Logged in successfully")
    
    # Test AI bullets endpoint
    bullets_data = {
        "job_title": "Software Engineer",
        "company": "Tech Corp",
        "description": "Developed web applications and managed databases"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1x/resume-ai/bullets",
            json=bullets_data,
            cookies=cookies,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("\n✅ AI Bullets Generation: PASS")
            return True
        else:
            print(f"\n❌ AI Bullets Generation: FAIL (status {response.status_code})")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def test_ai_summary():
    """Test professional summary generation"""
    print("\n" + "=" * 60)
    print("TEST: AI Professional Summary Generation")
    print("=" * 60)
    
    # First login
    login_data = {"email": "test@example.com", "password": "password123"}
    login_resp = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code}")
        return False
    
    cookies = login_resp.cookies
    
    # Test AI summary endpoint
    summary_data = {
        "current_position": "Software Engineer",
        "years_experience": 5,
        "key_skills": ["Python", "FastAPI", "React"],
        "industry": "Technology"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1x/resume-ai/professional-summary",
            json=summary_data,
            cookies=cookies,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("\n✅ AI Summary Generation: PASS")
            return True
        else:
            print(f"\n❌ AI Summary Generation: FAIL (status {response.status_code})")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def check_config():
    """Check backend configuration"""
    print("\n" + "=" * 60)
    print("Configuration Check")
    print("=" * 60)
    
    # Check if backend is up
    try:
        response = requests.get(f"{BASE_URL}/healthz", timeout=5)
        print(f"Backend Status: {response.status_code}")
        
        # Try to get some config info (if exposed)
        # Note: In production, don't expose config via API
        print("\nTo enable AI generation, set one of these environment variables:")
        print("  - OPENAI_API_KEY=your-openai-key")
        print("  - ANTHROPIC_API_KEY=your-anthropic-key")
        print("  - Use Ollama locally (AI_PROVIDER=ollama)")
        
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("AI GENERATION DIAGNOSTIC TEST")
    print("=" * 60)
    
    # Check config
    if not check_config():
        print("\nBackend is not responding.")
        return
    
    # Test AI endpoints
    test_ai_bullets()
    test_ai_summary()
    
    print("\n" + "=" * 60)
    print("DIAGNOSIS:")
    print("=" * 60)
    print("If tests fail with errors about API keys, you need to:")
    print("1. Create a .env file in the backend directory")
    print("2. Add one of these:")
    print("   OPENAI_API_KEY=sk-your-key-here")
    print("   ANTHROPIC_API_KEY=sk-ant-your-key-here")
    print("   AI_PROVIDER=ollama (if using local Ollama)")
    print("\n3. Restart the backend server")


if __name__ == "__main__":
    main()
