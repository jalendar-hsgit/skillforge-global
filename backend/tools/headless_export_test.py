"""
Headless browser test for resume export using Playwright.
Attempts to export a resume from the editor and saves the PDF.
"""
import asyncio
import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

async def test_export():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright not installed. Install with: pip install playwright")
        print("Then run: playwright install")
        return

    resume_id = 277
    frontend_url = "http://localhost:3001"  # dev server may use 3001 if 3000 is taken
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Set up download handler to capture PDF
        download_path = os.path.join(os.getcwd(), f"export_test_resume_{resume_id}.pdf")
        
        async def handle_download(download):
            await download.save_as(download_path)
            print(f"✓ PDF saved to: {download_path}")
        
        page.on("download", handle_download)
        
        try:
            # Navigate to the resume editor
            editor_url = f"{frontend_url}/resumes/{resume_id}/edit"
            print(f"[1/4] Navigating to {editor_url}...")
            await page.goto(editor_url, wait_until="networkidle", timeout=30000)
            
            # Wait for editor to load
            print("[2/4] Waiting for editor to load...")
            await page.wait_for_selector('[data-testid="btn-export"]', timeout=15000)
            
            # Click Export button
            print("[3/4] Clicking Export button...")
            export_btn = await page.query_selector('[data-testid="btn-export"]')
            if export_btn:
                await export_btn.click()
                # Wait a bit for PDF to download
                await asyncio.sleep(3)
                print("[4/4] Export complete!")
            else:
                print("✗ Export button not found")
        
        except Exception as e:
            print(f"✗ Test failed: {e}")
        
        finally:
            await browser.close()

if __name__ == '__main__':
    asyncio.run(test_export())
