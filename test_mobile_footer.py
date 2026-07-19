import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 375, "height": 812})
        await page.goto("http://127.0.0.1:5000/")
        # Scroll to bottom
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)
        # Take a screenshot of the footer payment partners part
        await page.screenshot(path="mobile_footer.png", full_page=True)
        await browser.close()

asyncio.run(main())
