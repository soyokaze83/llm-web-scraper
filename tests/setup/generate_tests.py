import asyncio
import json
import os
from argparse import ArgumentParser

import dspy
from dotenv import load_dotenv
from generation_schema import TestGeneratorAgent

from src.scraper import WebScraper

load_dotenv()
API_KEY = os.environ["API_KEY"]


async def generate_cases(url: str, output_file: str):
    """Generate test cases from page URL."""

    # Configure DSPy generation model
    model_name = "gemini/gemini-2.0-flash"
    model = dspy.LM(model=model_name, api_key=API_KEY, max_tokens=8000)
    dspy.configure(lm=model, allow_async=True, adapter=dspy.JSONAdapter())

    test_generator = TestGeneratorAgent()
    try:
        async with WebScraper(url, headless=True) as scraper:
            initial_html = await scraper.get_body_content()

        test_cases_obj = test_generator(html_content=initial_html)
        tasks = test_cases_obj.test_cases.tasks

        # Save the data to the output file
        test_data = {"url": url, "tasks": tasks}
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(test_data, f, indent=2)

        print(f"Successfully saved {len(tasks)} test cases to {output_file}")

    except Exception as e:
        print(f"Failed to generate test cases: {e}")

    pass


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--url", required=True, help="URL to generate tests from")
    parser.add_argument(
        "--output", default="test_cases.json", help="Test case output file"
    )
    args = parser.parse_args()

    asyncio.run(generate_cases(args.url, args.output))
