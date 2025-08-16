import asyncio
import json
from typing import Any, Dict, List

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
    You are a web agent. Your goal is to interact with the given HTML content to complete the user's task.
    You must use the provided tools to find elements, fill forms, click buttons, and extract information.
    Your final answer MUST be a single, valid JSON string containing the extracted data.
    """

    distilled_content: str = dspy.InputField(
        desc="A JSON string summarizing the forms and tables on the webpage."
    )
    task: str = dspy.InputField(desc="The natural language instruction from the user.")
    answer: JSONOutput = dspy.OutputField(
        desc="A valid JSON string with the final extracted data."
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

        tools = self._get_tools()
        self.agent = dspy.ReAct(ScraperAgentSignature, tools=tools)

    async def aforward(self, distilled_content: Dict[str, Any], user_task: str):
        json_distilled_content = json.dumps(distilled_content, indent=2)
        result = await self.agent.acall(
            distilled_content=json_distilled_content, task=user_task
        )
        return result

    def _get_tools(self):
        """Configures tools and wraps async functions to be sync-callable."""

        tools = [
            self.tools.get_current_url,
            self.tools.list_interactive_elements,
            self.tools.read_content_of_element,
            self.tools.type_into_element,
            self.tools.click_element,
            self.tools.select_dropdown_option,
            self.tools.navigate_to_url,
            self.tools.scroll_page,
            self.scraper.get_distilled_dom,
            self.scraper.get_full_content,
        ]
        return tools
