import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 375, "height": 812})
        await page.goto("http://127.0.0.1:5000/")
        # Check if razorpay is visible
        is_visible = await page.is_visible('img[alt="Razorpay"]')
        print(f"Razorpay visible: {is_visible}")
        is_paypal_visible = await page.is_visible('img[alt="PayPal"]')
        print(f"PayPal visible: {is_paypal_visible}")
        await browser.close()

asyncio.run(main())
