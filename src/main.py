import asyncio
import os
from typing import Any

import dspy
from dotenv import load_dotenv
from dspy.utils.callback import BaseCallback

from agent import ScraperAgent
from src.scraper.webscraper import WebScraper
from src.scraper.webtools import WebInteractionTools

load_dotenv()
API_KEY = os.environ["API_KEY"]


class ToolLoggingCallback(BaseCallback):
    """A callback handler for logging tool usage, matching the BaseCallback source."""

    def on_tool_start(self, call_id: str, instance: Any, inputs: dict[str, Any]):
        """Triggered before a tool is called, using the exact signature."""
        print("─" * 50)
        # Get the tool's name from the instance object provided by the callback
        tool_name = instance.name
        print(f"🤖 Calling Tool: {tool_name}")
        if inputs:
            print(f"   Inputs: {inputs}")

    def on_tool_end(
        self, call_id: str, outputs: Any | None, exception: Exception | None = None
    ):
        """Triggered after a tool has finished, using the exact signature."""
        # Handle cases where the tool might raise an error
        if exception:
            print(f"🚨 Tool Error: {exception}")
        else:
            print(f"👀 Observation: {outputs}")
        print("─" * 50 + "\n")


async def main():
    # url_input = input("Enter link: ")
    # user_input = input("What would you like to scrape?\n")

    url_input = "https://shorthorn.digitalbeef.com/"
    user_input = "Get me data on bulls with a maximum weaning weight of 30"

    logger = ToolLoggingCallback()

    model = dspy.LM(
        model="gemini/gemini-2.0-flash",
        api_key=API_KEY,
    )
    dspy.configure(lm=model, allow_async=True, callbacks=[logger])

    async with WebScraper(url_input, headless=True) as scraper:
        # Get distilled DOM & web interaction tools for agent
        distilled_dom = await scraper.get_distilled_dom()
        webtools = WebInteractionTools(scraper.tab)

        # Start and call async agent
        agent = ScraperAgent(web_scraper=scraper, interaction_tools=webtools)
        result = await agent.acall(
            distilled_content=distilled_dom, user_task=user_input
        )

    print(result)
    print(f"Answer: {result.answer}")


if __name__ == "__main__":
    asyncio.run(main())
