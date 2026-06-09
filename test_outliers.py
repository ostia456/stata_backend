import asyncio
from playwright.async_api import async_playwright

async def test_pdf():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test PDF</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            h1 { color: blue; }
        </style>
    </head>
    <body>
        <h1>Test de génération PDF</h1>
        <p>Ceci est un test de génération PDF avec Playwright.</p>
        <p>Date: 2026-06-09</p>
    </body>
    </html>
    """
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_content(html_content, wait_until="networkidle")
        pdf_bytes = await page.pdf(format='A4')
        await browser.close()
        
        with open("test_output.pdf", "wb") as f:
            f.write(pdf_bytes)
        
        print("✅ PDF généré avec succès: test_output.pdf")

asyncio.run(test_pdf())