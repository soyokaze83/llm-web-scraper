import asyncio
import os
from typing import Any

import dspy
import pytest
from conftest import key_rotator, load_test_cases
from dspy.utils.callback import BaseCallback

from src.agent.extractor_agent import ExtractorAgent
from src.agent.scraper_agent import ScraperAgent
from src.scraper.webscraper import WebScraper
from src.scraper.webtools import WebInteractionTools


class ToolLoggingCallback(BaseCallback):
    """A callback handler for logging tool usage."""

    def __init__(self):
        super().__init__()
        self._tool_calls = {}
        self.active_agent_name = "SYSTEM"

    def on_tool_start(self, call_id: str, instance: Any, inputs: dict[str, Any]):
        """Triggered before a tool is called."""
        tool_name = instance.name
        if not tool_name or tool_name == "finish":
            return
        self._tool_calls[call_id] = tool_name
        print("-" * 50)
        print(f"🤖 Scraper Agent - Calling Tool: {tool_name}")
        if inputs:
            print(f"   Inputs: {inputs}")

    def on_tool_end(
        self, call_id: str, outputs: Any | None, exception: Exception | None = None
    ):
        """Triggered after a tool has finished."""
        tool_name = self._tool_calls.pop(call_id, None)
        if not tool_name:
            return
        if exception:
            print(f"🚨 Tool Error: {exception}")
        else:
            if outputs:
                outputs = str(outputs)
                if len(outputs) > 100:
                    outputs = f"{outputs[:100]}..."
                print(f"👀 Observation: {outputs}")
        print("-" * 50 + "\n")


# The parametrize decorator stays the same
@pytest.mark.parametrize("url, task", load_test_cases())
def test_scraping_pipeline(url, task):
    """
    Runs the full scraper -> extractor pipeline for a given task.
    """

    print(f"\n🧪 Running test for task: '{task}'")

    logger = ToolLoggingCallback()
    model_name = os.environ["MODEL_NAME"]
    next_api_key = key_rotator.get_next_key()
    next_lm = dspy.LM(
        model=model_name,
        api_key=next_api_key,
        max_tokens=8000,
    )
    dspy.configure(
        lm=next_lm, allow_async=True, callbacks=[logger], adapter=dspy.JSONAdapter()
    )

    async def run_pipeline():
        async with WebScraper(url, headless=True) as scraper:
            initial_content = await scraper.get_body_content()
            webtools = WebInteractionTools(scraper.tab)
            shared_state = {"final_html": None}

            scraper_agent = ScraperAgent(
                web_scraper=scraper, interaction_tools=webtools, state=shared_state
            )
            extractor_agent = ExtractorAgent()

            await scraper_agent.acall(full_content=initial_content, user_task=task)
            final_html = shared_state.get("final_html")

            assert final_html, "ScraperAgent failed to store HTML."

            extract_result = await extractor_agent.aforward(
                html_content=final_html, user_task=task
            )

            answer = extract_result.answer
            assert answer and answer.data, "ExtractorAgent returned no data."
            assert "No data found" not in str(answer.data), (
                "ExtractorAgent explicitly found no data."
            )

            print(f"Answer: {answer}")

    asyncio.run(run_pipeline())
