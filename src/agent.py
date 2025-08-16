from typing import List, Optional

import dspy
from pydantic import BaseModel

from webscraper import WebScraper


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

    html_content: str = dspy.InputField(desc="The full HTML content of the webpage.")
    task: str = dspy.InputField(desc="The natural language instruction from the user.")
    answer: JSONOutput = dspy.OutputField(
        desc="A valid JSON string with the final extracted data."
    )


class ScraperAgent(dspy.Module):
    """DSPy module to scrape based on defined DSPy signature."""

    def __init__(
        self, model_id: str, api_key: str, scrape_tool: Optional[WebScraper] = None
    ):
        self.signature = dspy.functional.TypedPredictor(ScraperAgentSignature)
        self.scrape_tool = scrape_tool

        # TODO: Define model with DSPy

    def forward(self, html_content: str, user_task: str):
        tools = self._get_tools()
        agent = dspy.ReAct(ScraperAgentSignature, tools=tools)
        result = agent(html_content, user_task)

        return result

    def _get_tools(self):
        pass
