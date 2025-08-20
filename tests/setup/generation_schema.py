from typing import List

import dspy
from pydantic import BaseModel, Field


class TestCases(BaseModel):
    """Model to structure the generated test cases."""

    tasks: List[str] = Field(
        description="A list of exactly five diverse and valid user tasks.",
        min_length=5,
        max_length=5,
    )


class TestGeneratorSignature(dspy.Signature):
    """
    You are a creative QA Engineer. Your task is to analyze the HTML of a webpage
    and generate 5 diverse and valid user tasks for a web scraping agent.

    The tasks should cover different functionalities visible on the page (e.g.,
    filling different form fields, clicking various buttons, testing edge cases).
    The tasks must be phrased as natural language commands a user would give.

    Do not do any authentication and just fill forms that is already provided by the
    initiala HTML content including forms, dropdown selections, and other interactive
    elements that do not authenticate.

    Example for a financial website:
    - "Get the stock price for NVDA"
    - "Find the P/E ratio for all tech stocks with a market cap over $1 Trillion"
    - "Extract the historical price data for the last 6 months for APPL"
    """

    html_content: str = dspy.InputField(desc="The HTML content of the page to analyze.")
    test_cases: TestCases = dspy.OutputField(
        desc="Five generated user tasks for testing."
    )


class TestGeneratorAgent(dspy.Module):
    """A DSPy module that generates scraping tasks for testing purposes."""

    def __init__(self):
        super().__init__()
        self.generator = dspy.Predict(TestGeneratorSignature)

    def forward(self, html_content: str) -> TestCases:
        result = self.generator(html_content=html_content)
        return result
