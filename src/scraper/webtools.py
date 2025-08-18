import asyncio
from typing import Dict, List

from zendriver import Tab


class WebInteractionTools:
    """A collection of robust tools for an LLM agent to navigate and scrape dynamic websites."""

    def __init__(self, page: Tab):
        self.page = page

    async def get_current_url(self) -> str:
        """Returns the current URL of the webpage to understand the agent's location."""
        return f"Current URL is: {self.page.url}"

    async def list_interactive_elements(self) -> List[Dict[str, str]]:
        """
        Provides a list of all visible interactive elements (links, buttons, inputs, selects).
        Use this to discover what actions are possible on the page, especially if you are unsure of a CSS selector.
        """
        elements = await self.page.select_all(
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
            element = await self.page.select(css_selector)
            if element:
                return element.text_all.strip()
            return f"Error: Element with selector '{css_selector}' not found."
        except Exception as e:
            return f"Error reading element '{css_selector}': {e}"

    async def type_into_element(self, css_selector: str, text: str) -> str:
        """
        Waits for a specific input field to be ready, then types the given text into it.
        """
        try:
            element = await self.page.select(css_selector)
            if element:
                await element.send_keys(text)
                return f"Successfully typed '{text}' into element '{css_selector}'."
            return f"Error: Element with selector '{css_selector}' not found after waiting."
        except Exception as e:
            return f"Error typing into '{css_selector}': {e}"

    async def click_element(self, css_selector: str) -> str:
        """
        Clicks an element using multiple fallback approaches to improve reliability.
        """
        try:
            # First attempt to find the element
            element = await self.page.select(css_selector)
            if not element:
                return f"Error: Element with selector '{css_selector}' not found."

            # Check if element is visible using get_position
            position = await element.get_position()
            if not position:
                return f"Error: Element '{css_selector}' is not visible or not positioned in viewport."

            await self.page.evaluate(f"""
                var element = document.querySelector("{css_selector}");
                if (element) element.click();
            """)

            return f"Successfully clicked element '{css_selector}'."

        except Exception as e:
            return f"Error clicking element '{css_selector}': {e}"

    async def select_dropdown_option(self, css_selector: str, value: str) -> str:
        """
        Selects an option from a <select> dropdown element.
        The 'value' should match the 'value' attribute of an <option> tag.
        """
        try:
            select_element = await self.page.select(css_selector)
            if not select_element:
                return f"Error: Element '{css_selector}' is not a dropdown."

            option_to_select = await select_element.query_selector(
                f"option[value='{value}']"
            )
            if option_to_select:
                await option_to_select.select_option()
                return f"Successfully selected option with value '{value}' in dropdown '{css_selector}'."
            else:
                return f"Error: Option with value '{value}' not found in dropdown '{css_selector}'."
        except Exception as e:
            return f"Error selecting dropdown option: {e}"

    async def navigate_to_url(self, url: str) -> str:
        """Navigates the browser tab to a new URL."""
        await self.page.get(url)
        return f"Successfully navigated to {url}."

    async def scroll_page(self, direction: str) -> str:
        """Scrolls the page. 'direction' must be 'up' or 'down'."""
        if direction.lower() == "down":
            await self.page.evaluate("window.scrollBy(0, window.innerHeight);")
            return "Scrolled down."
        elif direction.lower() == "up":
            await self.page.evaluate("window.scrollBy(0, -window.innerHeight);")
            return "Scrolled up."
        return "Error: Invalid scroll direction. Use 'up' or 'down'."

    async def wait_loading(self, css_selector: str, timeout: int = 30) -> str:
        """
        Waits for a specific element (like a loading spinner or loading message) to disappear from the page.
        Ensure a loading process is complete before proceeding.
        """
        try:
            loop = asyncio.get_event_loop()
            start_time = loop.time()

            while True:
                element = await self.page.query_selector(css_selector)
                if not element:
                    return f"Element '{css_selector}' disappeared successfully."

                if loop.time() - start_time > timeout:
                    raise asyncio.TimeoutError(
                        f"Element '{css_selector}' did not disappear within {timeout} seconds."
                    )

                await asyncio.sleep(0.5)

        except asyncio.TimeoutError as e:
            return f"Error: {e}"
        except Exception as e:
            return f"An error occurred while waiting for element '{css_selector}' to disappear: {e}"
