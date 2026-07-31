import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        
        await page.goto(f"file://{__import__('os').path.abspath('test_showpicker.html')}")
        
        # Click the wrapper (top left corner, not on the input)
        await page.mouse.click(10, 10)
        await asyncio.sleep(0.5)
        
        # Click the input center
        box = await page.locator('#mydate').bounding_box()
        await page.mouse.click(box['x'] + box['width']/2, box['y'] + box['height']/2)
        await asyncio.sleep(0.5)
        
        await browser.close()

asyncio.run(main())
