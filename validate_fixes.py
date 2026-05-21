#!/usr/bin/env python3
"""
Validation script to verify all product creation fixes are in place
"""
import sys
import os

def check_file_content(filepath, search_strings, description):
    """Check if file contains all required strings"""
    print(f"\n📝 Checking: {description}")
    print(f"   File: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"   ❌ FAIL: File not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    all_found = True
    for search_str in search_strings:
        if search_str in content:
            print(f"   ✅ Found: {search_str[:60]}...")
        else:
            print(f"   ❌ Missing: {search_str[:60]}...")
            all_found = False
    
    return all_found

def main():
    print("=" * 70)
    print("PRODUCT CREATION FIX VALIDATION")
    print("=" * 70)
    
    checks = [
        (
            "backend/app/schemas/marketplace.py",
            [
                "currency: Optional[str] = Field(default=\"USD\"",
                "original_price: Optional[float] = Field(None, gt=0)",
            ],
            "✅ Backend Schema - Optional fields"
        ),
        (
            "backend/app/api/v1x/marketplace.py",
            [
                "from app.schemas.marketplace import DigitalProductCreate, DigitalProductUpdate",
                "product_data: DigitalProductCreate,",
                "@router.post(\"/seller/products\")",
            ],
            "✅ Backend Endpoint - Using DigitalProductCreate schema"
        ),
        (
            "src/pages/marketplace/seller/create-product.tsx",
            [
                "const submitData = {",
                "name: formData.name,",
                "price: formData.price,",
                "thumbnail_url: uploadedFiles.thumbnail || null,",
                "content_url: uploadedFiles.content || null,",
                "preview_url: uploadedFiles.preview || null,",
            ],
            "✅ Frontend Payload - Explicit field construction"
        ),
        (
            "src/pages/marketplace/seller/create-product.tsx",
            [
                "if (errorData.detail && Array.isArray(errorData.detail)) {",
                "const validationErrors = errorData.detail.map((e: any) => `${e.loc?.[1] || 'Field'}: ${e.msg}`)",
            ],
            "✅ Frontend Error Handling - Pydantic error parsing"
        ),
        (
            "backend/seed_all_demo_data.py",
            [
                "SellerAccount",
                "def seed_seller_accounts",
                "SellerAccount(",
            ],
            "✅ Seeding - SellerAccount creation"
        ),
    ]
    
    results = []
    for filepath, strings, description in checks:
        # Convert to absolute path
        abs_path = os.path.join("d:\\python code\\sfg\\skillforge-global", filepath)
        result = check_file_content(abs_path, strings, description)
        results.append((description, result))
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    for desc, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {desc}")
    
    all_pass = all(r for _, r in results)
    
    print("\n" + "=" * 70)
    if all_pass:
        print("✅ ALL CHECKS PASSED - Ready to test!")
        print("\nNext steps:")
        print("1. Start backend: cd backend && uvicorn app.main:app --reload")
        print("2. Start frontend: npm run dev")
        print("3. Navigate to: http://localhost:3000/marketplace/seller/create-product")
        print("4. Login with: sarah.chen@skillforge.com / password123")
        print("5. Fill form and click 'Save as Draft'")
    else:
        print("❌ SOME CHECKS FAILED - Review changes above")
        sys.exit(1)
    print("=" * 70)

if __name__ == "__main__":
    main()
