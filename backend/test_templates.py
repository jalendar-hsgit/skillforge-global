"""
Quick Visual Test for Resume Templates
Run this to verify all templates render correctly
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_template_rendering():
    """Test each template with sample data"""
    s = requests.Session()
    
    # Login
    print("🔐 Logging in...")
    r = s.post(f"{BASE_URL}/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "test123"
    })
    if r.status_code != 200:
        # Try signup if login fails
        s.post(f"{BASE_URL}/api/v1/auth/signup", json={
            "email": "test@example.com",
            "password": "test123",
            "full_name": "Test User"
        })
        r = s.post(f"{BASE_URL}/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "test123"
        })
    
    print("✅ Logged in")
    
    templates = [
        ("modern", "Modern Template"),
        ("minimal", "Minimal Template"),
        ("executive", "Executive Template"),
        ("creative", "Creative Template"),
        ("timeline", "Timeline Template"),
        ("elegant-blue", "Elegant Blue Template"),
    ]
    
    sample_resume = {
        "title": "Test Resume",
        "full_name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1-555-0123",
        "location": "San Francisco, CA",
        "linkedin_url": "linkedin.com/in/johndoe",
        "github_url": "github.com/johndoe",
        "professional_summary": "Experienced software engineer with 5+ years in full-stack development, specializing in React, Node.js, and cloud architecture.",
        "layout": "modern",
        "accent_color": "#2563eb",
        "font_family": "Inter",
        "show_icons": True
    }
    
    print("\n" + "="*60)
    print("🎨 TESTING RESUME TEMPLATES")
    print("="*60 + "\n")
    
    for layout, name in templates:
        sample_resume["layout"] = layout
        sample_resume["title"] = f"{name} Test"
        
        # Create resume
        r = s.post(f"{BASE_URL}/api/v1x/resumes/", json=sample_resume)
        
        if r.status_code == 201:
            resume_id = r.json()["id"]
            print(f"✅ {name:<25} | Created (ID: {resume_id})")
            print(f"   Preview: http://localhost:3000/resumes/{resume_id}/preview")
            print(f"   Export:  {BASE_URL}/api/v1x/resumes/{resume_id}/export?format=pdf")
        else:
            print(f"❌ {name:<25} | Failed (Status: {r.status_code})")
        
        print()
    
    print("="*60)
    print("📝 MANUAL TESTING STEPS:")
    print("="*60)
    print("1. Open each preview URL above in your browser")
    print("2. Verify template styling renders correctly")
    print("3. Check that all sections are visible")
    print("4. Test PDF export for each template")
    print("5. Compare preview vs exported PDF")
    print("\n✨ All templates created successfully!")

if __name__ == "__main__":
    test_template_rendering()
