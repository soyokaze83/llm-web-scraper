from typing import Any, Dict

import dspy

from src.scraper.webscraper import WebScraper
from src.scraper.webtools import WebInteractionTools


class ScraperAgentSignature(dspy.Signature):
    """
    You are an expert web navigation agent. Your goal is to find and store the HTML content that answers the user's task.

    **General Strategy and Workflow:**
    Your process is a cycle of Action -> Verification.

    1.  **Plan**: Analyze the HTML and the user's task to form a plan.

    2.  **Act & Verify Cycle**:
        * **Action**: Use a tool like `click_element` or `type_into_element` to perform a key action (e.g., submit a search).
        * **Verification**: After every action, you must verify the result to see if your plan is working. This involves several steps:
            * **a. Wait**: Use `wait_loading` to pause until a key part of the *expected new content* has appeared. A good selector might be for a row in a results table (e.g., '#searchResults .grid tr').
            * **b. Observe**: After the wait succeeds, use the efficient `get_body_content(css_selector=...)` to capture the HTML of the relevant page section (e.g., '#searchResults').
            * **c. Analyze**: Check the observed HTML. Does it contain the final data? Or is it an intermediate state, like a "still loading..." message or an error?

    3.  **Handle Dynamic Content (Looping)**:
        * If your analysis shows the content is not yet the final result (e.g., it's still a loading message), you should **re-evaluate and repeat the verification step**. You might need to wait longer or use `get_body_content` again to check for updates.
        This allows you to handle dynamic pages that load data in stages.

    3.  **Finish**:
        * Once your verification confirms you have the final data on the page, you **MUST** call the `store_and_finish` tool.
        * Provide the CSS selector for the main results container (e.g., '#searchResults') to this tool. This is your final step.
    """

    html_content: str = dspy.InputField(desc="The initial HTML content of the webpage.")
    task: str = dspy.InputField(desc="The user's instruction.")
    confirmation: str = dspy.OutputField(
        desc="A confirmation message that the final HTML has been stored."
    )


class ScraperAgent(dspy.Module):
    """DSPy module to navigate a website, find the target page, and store the result."""

    def __init__(
        self,
        web_scraper: WebScraper,
        interaction_tools: WebInteractionTools,
        state: Dict[str, Any],
    ):
        super().__init__()
        self.scraper = web_scraper
        self.tools = interaction_tools
        self.shared_state = state  # Store reference to the shared state object
        self.agent = dspy.ReAct(
            signature=ScraperAgentSignature, tools=self._get_tools()
        )

    async def aforward(self, full_content: str, user_task: str):
        return await self.agent.acall(html_content=full_content, task=user_task)

    async def _store_and_finish(self, css_selector: str) -> str:
        """
        Retrieves the HTML content of the given selector and stores it in the shared state, then finishes the task.
        """
        print("Storing final HTML content...")
        final_html = await self.scraper.get_body_content(css_selector=css_selector)
        self.shared_state["final_html"] = final_html
        return f"Successfully retrieved and stored the HTML content from selector '{css_selector}'. The task is complete."

    def _get_tools(self):
        """Configures tools and wraps async functions to be sync-callable."""

        tools = [
            # Interactive tools
            self.tools.type_into_element,
            self.tools.click_element,
            self.tools.select_dropdown_option,
            self.tools.navigate_to_url,
            self.tools.scroll_page,
            self.tools.wait_loading,
            # Page HTML scraping tools
            self.scraper.get_body_content,
            self.scraper.get_head_content,
            self.scraper.get_current_url,
            self.scraper.list_interactive_elements,
            self.scraper.read_content_of_element,
            # Internal agent tool
            self._store_and_finish,
        ]
        return tools
