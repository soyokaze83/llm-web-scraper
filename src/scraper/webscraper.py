from typing import Optional, Type

import zendriver as zd
from zendriver import Browser, Tab


class WebScraper:
    """An asynchronous context manager for web scraping with zendriver."""

    def __init__(self, url: str, headless: bool = True):
        """
        Initializes the scraper with a target URL and browser options.

        Args:
            url (str): The initial URL to navigate to when the scraper starts.
            headless (bool): Whether to run the browser in headless mode.
        """
        self.start_url = url
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.tab: Optional[Tab] = None

    async def __aenter__(self):
        """Starts the browser and navigates to the URL."""
        print("Starting scraper...")
        self.browser = await zd.start(headless=self.headless)
        self.tab = await self.browser.get(self.start_url)
        print("Scraper started successfully.")
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ):
        """Stops the browser, ensuring cleanup."""
        if self.browser:
            print("Stopping scraper...")
            await self.browser.stop()
            print("Scraper stopped successfully.")

    async def get_content(self, selector: Optional[str] = None) -> str:
        """
        Gets body HTML content from the current page.

        If a selector is provided, it returns the outer HTML of the first
        matching element. Otherwise, it returns the HTML of the entire page.

        Args:
            selector (Optional[str]): A CSS selector to find a specific element.
        """
        if not self.tab or not self.browser:
            raise RuntimeError(
                "Scraper not started. Please use 'async with WebScraper(...)'."
            )

        if selector:
            print(f"Finding element with selector: '{selector}'")
            selector_html = await self.tab.find_all(selector)
            selector_html = [str(html) for html in selector_html]
            content = "\n".join(selector_html)
        else:
            print("Getting HTML body...")
            body_html = await self.tab.select("body")
            content = await body_html.get_html()

        return content
