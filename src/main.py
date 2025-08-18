import asyncio
import json
import os
import uuid
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
    """
    A callback handler for logging tool usage, which now ignores the internal 'finish' tool.
    """

    def __init__(self):
        super().__init__()
        self._tool_calls = {}

    def on_tool_start(self, call_id: str, instance: Any, inputs: dict[str, Any]):
        """Triggered before a tool is called."""
        tool_name = instance.name
        self._tool_calls[call_id] = tool_name  # Store the tool name

        print("─" * 50)
        print(f"🤖 Calling Tool: {tool_name}")

        # Ignore DSPy's internal 'finish' tool
        if tool_name == "finish":
            return

        if inputs:
            print(f"   Inputs: {inputs}")

    def on_tool_end(
        self, call_id: str, outputs: Any | None, exception: Exception | None = None
    ):
        """Triggered after a tool has finished."""
        tool_name = self._tool_calls.pop(call_id, None)

        # Ignore DSPy's internal 'finish' tool
        if tool_name == "finish":
            print("Wrapping up scraping process...")
            print("─" * 50 + "\n")
            return

        if exception:
            print(f"🚨 Tool Error: {exception}")
        else:
            if outputs:
                outputs = str(outputs)
                if len(outputs) > 100:
                    outputs = f"{outputs[:100]}..."
            print(f"👀 Observation: {outputs}")
        print("─" * 50 + "\n")


async def main():
    url_input = input("🔗 Enter link: ")
    user_input = input("❓ What would you like to scrape?\n")
    model_name = "gemini/gemini-2.5-flash"
    print()

    logger = ToolLoggingCallback()

    model = dspy.LM(
        model=model_name,
        api_key=API_KEY,
    )
    dspy.configure(
        lm=model, allow_async=True, callbacks=[logger], adapter=dspy.JSONAdapter()
    )

    async with WebScraper(url_input, headless=True) as scraper:
        full_content = await scraper.get_body_content()
        webtools = WebInteractionTools(scraper.tab)

        # Start and call async agent
        agent = ScraperAgent(web_scraper=scraper, interaction_tools=webtools)
        result = await agent.acall(full_content=full_content, user_task=user_input)

    print(f"\nReasoning: {result.reasoning}")
    print(f"Answer: {result.answer}")

    # Construct final output to JSON output
    final_output = result.answer.model_dump()
    final_output["url"] = url_input
    final_output["prompt"] = user_input
    final_output["model"] = model_name

    # Output & save file
    random_uuid = uuid.uuid4()
    output_file = f"result_{random_uuid}.json"
    if not os.path.exists("result"):
        os.makedirs("result", exist_ok=True)

    output_path = os.path.join("result", output_file)
    print(f"\nDumping results into {output_path}...")
    with open(output_path, "w", encoding="utf-8") as output:
        json.dump(result.answer.model_dump(), output, indent=2)
    print(f"Successfully saved results to {output_file}!")


if __name__ == "__main__":
    asyncio.run(main())
