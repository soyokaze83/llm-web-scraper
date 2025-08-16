import asyncio
from typing import Any, Dict, Optional, Type

import zendriver as zd
from zendriver import Browser, Element, Tab


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

    async def get_full_content(self) -> str:
        """
        Get full HTML content from the requested URL page.

        Returns:
            The full HTML content of the URL page in string format.
        """

        if not self.tab or not self.browser:
            raise RuntimeError(
                "Scraper not started. Please use 'async with WebScraper(...)'."
            )

        await self.tab.select("body")  # Navigate tab to body content
        full_content = await self.tab.get_content()
        return full_content

    async def get_distilled_dom(self) -> Dict[str, Any]:
        """
        Get distilled DOM of URL page with important fields i.e. forms & tables.

        Returns:
            Forms and table data of URL page.
        """

        if not self.tab or not self.browser:
            raise RuntimeError(
                "Scraper not started. Please use 'async with WebScraper(...)'."
            )

        # PROCESS FORMS
        forms_data = []
        all_forms = await self.tab.select_all("form")

        # Pre-fetch all labels and create a map for faster lookup
        all_labels = await self.tab.select_all("label")
        label_map = {
            label.attrs.get("for"): label.text_all.strip()
            for label in all_labels
            if label.attrs.get("for")
        }

        for form in all_forms:
            controls = []

            # 1. Process select tags
            for sel in await form.query_selector_all("select"):
                label = await self._find_desc(sel, label_map)

                options = [
                    o.text_all.strip() for o in await sel.query_selector_all("option")
                ]
                controls.append(
                    {
                        "type": "select",
                        "label": label,
                        "options": options,
                    }
                )

            # 2. Process input tags
            for inp in await form.query_selector_all("input"):
                label = await self._find_desc(inp, label_map)
                controls.append(
                    {
                        "type": "input",
                        "input_type": inp.attrs.get("type", "text"),
                        "label": label,
                        "placeholder": inp.attrs.get("placeholder"),
                    }
                )

            # 3. Process button tags
            for btn in await form.query_selector_all("button, input[type=submit]"):
                text = btn.text_all.strip() or btn.attrs.get("value")
                controls.append({"type": "button", "text": text})

            forms_data.append(
                {
                    "id": form.attrs.get("id"),
                    "action": form.attrs.get("action"),
                    "controls": controls,
                }
            )

        # PROCESS TABLES: <th>, <tr>, <td>
        tables_data = []
        all_tables = await self.tab.select_all("table")
        for table in all_tables:
            headers = [
                th.text_all.strip() for th in await table.query_selector_all("th")
            ]

            sample_rows = []
            all_rows = await table.query_selector_all("tr")
            for row in all_rows[:3]:
                cells = [
                    td.text_all.strip() for td in await row.query_selector_all("td")
                ]
                if cells:
                    sample_rows.append(cells)

            tables_data.append(
                {
                    "id": table.attrs.get("id"),
                    "headers": headers,
                    "sample_rows": sample_rows,
                }
            )

        return {"forms": forms_data, "tables": tables_data}

    async def _find_desc(
        self, element: Element, label_map: Dict[str, str]
    ) -> Optional[str]:
        """
        Finds commonly used description for user input tags.

        Args:
            element (Element): The form element to find the description.
            label_map (Dict): Dict mapping label 'for' attribute to text content.

        Returns:
            The user input tag description.
        """

        # Find from label tags using pre-fetched label map
        elem_id = element.attrs.get("id")
        if elem_id and elem_id in label_map:
            return label_map[elem_id]

        parent = element.parent
        while parent:
            if parent.node_name == "LABEL":
                return parent.text_all.strip()
            parent = parent.parent

        # Fallback if no label tag found
        description = (
            element.attrs.get("placeholder")
            or element.attrs.get("aria-label")
            or element.attrs.get("name")
        )

        return description
