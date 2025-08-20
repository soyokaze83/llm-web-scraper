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

        # Navigate to website URL
        await self.tab.get(self.start_url)

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

    async def get_head_content(self) -> str:
        """Get head section of the HTML page."""

        if not self.tab or not self.browser:
            raise RuntimeError(
                "Scraper not started. Please use 'async with WebScraper(...)'."
            )

        return await self.tab.select("head")

    async def get_body_content(self, css_selector: Optional[str] = None) -> str:
        """
        Get HTML content from the page. If a css_selector is provided, gets content
        from that specific element. Otherwise, returns the entire body.
        Using a specific selector is highly recommended for efficiency.
        """
        if not self.tab:
            raise RuntimeError("Scraper not started.")

        selector_to_use = css_selector or "body"

        try:
            element = await self.tab.select(selector_to_use)
            if element:
                return str(element)  # Return the element's outer HTML
            return f"Error: Element with selector '{selector_to_use}' not found."
        except Exception as e:
            return f"Error getting content for selector '{selector_to_use}': {e}"
