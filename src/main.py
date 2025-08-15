import asyncio

from webscraper import WebScraper


async def main():
    url_input = input("Enter link: ")
    user_input = input("What would you like to scrape?\n")

    async with WebScraper(url_input, headless=True) as scraper:
        full_html = await scraper.get_content(selector="input")
        print(full_html)


if __name__ == "__main__":
    asyncio.run(main())
