from typing import List

import dspy
from pydantic import BaseModel


class JSONOutput(BaseModel):
    """Model definition for scraped data JSON output."""

    header: List[str]
    data: List[List[str]]


class ExtractorAgentSignature(dspy.Signature):
    """
    You are an expert data extraction agent. Your sole task is to analyze the provided HTML content and extract the information required to fulfill the user's task.
    Format your final answer as a single, valid JSON object following the structure of a JSON table with headers and rows.
    """

    html_content: str = dspy.InputField(
        desc="The full HTML content of the webpage containing the target data."
    )
    task: str = dspy.InputField(
        desc="The original natural language instruction from the user."
    )
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


class ExtractorAgent(dspy.Module):
    """A DSPy module that excels at extracting structured data from static HTML."""

    def __init__(self):
        super().__init__()
        self.extractor = dspy.Predict(ExtractorAgentSignature)

    def forward(self, html_content: str, user_task: str):
        return self.extractor(html_content=html_content, task=user_task)

    async def aforward(self, html_content: str, user_task: str):
        return await self.extractor.acall(html_content=html_content, task=user_task)
