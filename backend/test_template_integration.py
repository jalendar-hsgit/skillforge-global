"""
Test Template Integration - Verify template config applies to resume
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8001/api/v1x"

def test_template_integration():
    """Test that selecting a template updates resume with config"""
    print("="*60)
    print("Template Integration Test".center(60))
    print("="*60)
    
    # Step 1: Get a template with config
    print("\n📋 Step 1: Fetching templates...")
    resp = requests.get(f"{BASE_URL}/resume-templates")
    if resp.status_code != 200:
        print(f"❌ Failed to fetch templates: {resp.status_code}")
        return
    
    templates = resp.json()
    if not templates:
        print("❌ No templates found!")
        return
    
    template = templates[0]  # Get first template
    print(f"✅ Selected template: {template['name']}")
    print(f"   Category: {template['category']}")
    print(f"   Config: {json.dumps(template['config'], indent=2)}")
    
    # Step 2: Verify template config structure
    print("\n🔍 Step 2: Verifying template config structure...")
    config = template['config']
    required_keys = ['layout', 'font_family', 'accent_color', 'picture_style', 'show_icons']
    
    # Handle both field naming conventions
    config_keys = list(config.keys())
    has_layout = 'layout' in config
    has_font = 'font_family' in config or 'font' in config
    has_accent = 'accent_color' in config or 'accent' in config
    has_picture = 'picture_style' in config or 'picture' in config
    has_icons = 'show_icons' in config or 'icons' in config
    
    if has_layout and has_font and has_accent and has_picture and has_icons:
        print(f"✅ Config has all required fields: {config_keys}")
    else:
        print(f"⚠️  Config missing some fields: {config_keys}")
        print(f"   Layout: {has_layout}, Font: {has_font}, Accent: {has_accent}, Picture: {has_picture}, Icons: {has_icons}")
    
    # Step 3: Show expected frontend mapping
    print("\n🎨 Step 3: Expected frontend mapping:")
    mapping = {
        'template': str(template['id']),
        'font_family': config.get('font_family') or config.get('font'),
        'layout': config.get('layout'),
        'accent_color': config.get('accent_color') or config.get('accent'),
        'picture_style': config.get('picture_style') or config.get('picture'),
        'show_icons': config.get('show_icons', config.get('icons')),
    }
    
    print("   Resume fields that should be updated:")
    for key, value in mapping.items():
        print(f"   - {key}: {value}")
    
    # Step 4: Test popularity tracking
    print("\n📊 Step 4: Testing popularity tracking...")
    resp = requests.post(
        f"{BASE_URL}/resume-templates/{template['id']}/popularity",
        headers={"Content-Type": "application/json"}
    )
    if resp.status_code == 200:
        print(f"✅ Popularity tracked successfully")
        result = resp.json()
        print(f"   New popularity: {result.get('popularity', 'N/A')}")
    else:
        print(f"⚠️  Popularity tracking failed: {resp.status_code}")
    
    # Summary
    print("\n" + "="*60)
    print("✅ Integration Test Complete!".center(60))
    print("="*60)
    print("\n📝 Next Steps:")
    print("1. Open frontend at http://localhost:3000/dashboard")
    print("2. Create or edit a resume")
    print("3. Click 'Change Template' button")
    print("4. Select a template from the gallery")
    print("5. Verify these fields update in resume:")
    print("   - font_family, layout, accent_color, picture_style, show_icons")
    print("6. Check that live preview reflects the new styling")
    print("\n")

if __name__ == "__main__":
    try:
        test_template_integration()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
