import asyncio
import json

from scraper.webscraper import WebScraper


async def main():
    # url_input = input("Enter link: ")
    # user_input = input("What would you like to scrape?\n")

    url_input = "https://shorthorn.digitalbeef.com/"

    async with WebScraper(url_input, headless=True) as scraper:
        full_html = await scraper.get_full_content()
        print(full_html)

        distilled_dom = await scraper.get_distilled_dom()
        print(distilled_dom)

        with open("distilled_dom.json", "w", encoding="utf-8") as f:
            json.dump(distilled_dom, f, indent=4)


if __name__ == "__main__":
    asyncio.run(main())
