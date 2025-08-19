from typing import List

import dspy
from pydantic import BaseModel

from src.scraper.webscraper import WebScraper
from src.scraper.webtools import WebInteractionTools


class JSONOutput(BaseModel):
    """Model definition for scraped data JSON output."""

    header: List[str]
    data: List[List[str]]


class ScraperAgentSignature(dspy.Signature):
    """
    You are a web data scraping agent. Your goal is to interact with the given HTML content to complete the user's task.
    You must use the provided tools to find elements, fill forms, click buttons, and extract information.

    **IMPORTANT WORKFLOW:**
    1. Analyze the HTML and the task to understand what information to extract.
    2. Use tools to interact with the page if necessary (e.g., clicking buttons, filling forms).
    3. After any action that changes the page (like a click or form submission), you MUST use `wait_loading`.
        Crucially, you MUST wait for a specific child element that indicates the data has fully loaded.
        - **BAD:** Waiting for a container ID like '#searchResults' is unreliable if it shows a "loading..." message first.
        - **GOOD:** Wait for an element *inside* the container, like `#searchResults table`. This ensures the data is actually present.
    4. After waiting, you MUST use `get_body_content` to get the updated HTML of the page.
    5. Use `read_content_of_element` to extract the relevant text from the new content.
    6. Format your final answer as a single, valid JSON object following the structure of a JSON table with headers and rows.
    """

    html_content: str = dspy.InputField(
        desc="The full HTML content of the current state of the webpage."
    )
    task: str = dspy.InputField(desc="The natural language instruction from the user.")
    answer: JSONOutput = dspy.OutputField(
        desc=(
            "A valid JSON object with 'header' and 'data' keys. "
            "For tabular data, 'header' should be the column titles and 'data' the rows. "
            "For non-tabular information (e.g., a paragraph), still have the same column and row output structure "
            ", relevant with the user's requested task. "
            "If the extracted data has no header or is empty, you MUST return the exact string 'No header found.' "
            "If there is no data from the extraction, you MUST return the exact string 'No data found.'"
        )
    )


class ScraperAgent(dspy.Module):
    """DSPy module to scrape based on defined DSPy signature."""

    def __init__(
        self,
        web_scraper: WebScraper,
        interaction_tools: WebInteractionTools,
    ):
        super().__init__()
        self.signature = dspy.Predict(ScraperAgentSignature)
        self.scraper = web_scraper
        self.tools = interaction_tools

        all_tools = self._get_tools()
        self.agent = dspy.ReAct(signature=ScraperAgentSignature, tools=all_tools)

    async def aforward(self, full_content: str, user_task: str):
        result = await self.agent.acall(html_content=full_content, task=user_task)
        return result

    def _get_tools(self):
        """Configures tools and wraps async functions to be sync-callable."""

        tools = [
            # Interactive tools
            self.tools.get_current_url,
            self.tools.list_interactive_elements,
            self.tools.read_content_of_element,
            self.tools.type_into_element,
            self.tools.click_element,
            self.tools.select_dropdown_option,
            self.tools.navigate_to_url,
            self.tools.scroll_page,
            self.tools.wait_loading,
            # Page HTML scraping tools
            self.scraper.get_body_content,
            self.scraper.get_head_content,
        ]
        return tools
