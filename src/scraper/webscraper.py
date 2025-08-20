from typing import Dict, List, Optional, Type

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

    async def get_current_url(self) -> str:
        """Returns the current URL of the webpage to understand the agent's location."""
        return f"Current URL is: {self.tab.url}"

    async def list_interactive_elements(self) -> List[Dict[str, str]]:
        """
        Provides a list of all visible interactive elements (links, buttons, inputs, selects).
        Use this to discover what actions are possible on the page, especially if you are unsure of a CSS selector.
        """
        elements = await self.tab.select_all(
            "a, button, input:not([type=hidden]), select"
        )
        interactive_elements = []
        for el in elements:
            try:
                position = await el.get_position()
                if position:
                    text = el.text_all.strip().replace("\n", " ").replace("\t", " ")
                    tag = el.tag_name
                    attrs = el.attrs

                    el_info = {
                        "tag": tag.lower(),
                        "text": text
                        if text
                        else attrs.get(
                            "aria-label", attrs.get("name", attrs.get("id", ""))
                        ),
                    }
                    if "id" in attrs and attrs["id"]:
                        el_info["css_selector"] = f"#{attrs['id']}"

                    interactive_elements.append(el_info)
            except Exception:
                continue
        return interactive_elements

    async def read_content_of_element(self, css_selector: str) -> str:
        """
        Reads the full text content of an element found by its CSS selector.
        Useful for extracting data from paragraphs, divs, or table cells.
        """
        try:
            element = await self.tab.select(css_selector)
            if element:
                return element.text_all.strip()
            return f"Error: Element with selector '{css_selector}' not found."
        except Exception as e:
            return f"Error reading element '{css_selector}': {e}"
