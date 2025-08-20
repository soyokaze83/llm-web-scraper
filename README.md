# MrScraper AI Team Candidate Bounty: Intelligent Web Scraping

This project introduces an AI-powered web scraper designed especially for the challenge involving the user's natural language command processing. Instead of inputting fixed inputs, users can simply provide a URL and state their stating objective, such as "Get me information on cows with a weaning weight below 30". I decided to pick this approach because it just seems easier for the user to use a scraper with freedom of choice through natural language. With this strategy in mind, the scraper I've developed will work for both the easy and hard websites stated in the challenge.

The core of this scraper is an agentic LLM built with **DSPy** for defining the agent's logic and with the support of **PyDantic** for data validation and structured output. This agent is equipped with a set of specialized tools to interact with web pages mostly powered by the suggested **Zendriver**. The entire solution is implemented in Python and includes a testing feature using **PyTest**.

## Workflow
Below is a diagram illustrating the workflow of my proposed AI scraper for this challenge.

<div align="center">
  <img src="static/llm-scraper-flow.png">
</div>

### Step-by-Step Explanation
* **User Input**: The process begins when the user provides the target website's URL and a natural language command (e.g., "Get the table for cows from Alabama with a weight of more than 50 pounds").

* **Initial Page Fetch**: A Python script takes these inputs and fetches the initial HTML content from the given URL.

* **Action Planning (Web Scraping Agent)**: The initial HTML and the user's command are sent to the first LLM, the Web Scraping Agent. This agent analyzes the user's intent and the webpage's structure to determine the correct sequence of actions needed, such as filling out form fields or clicking buttons.

* **Browser Automation**: The Web Scraping Agent executes the planned actions, automating the browser to navigate to the final page that contains the requested data.

* **Data Extraction (Extractor Agent)**: The final HTML of the results page is passed to a second LLM, the Extractor Agent. This agent's specialized task is to parse the HTML, identify the target data, and structure it into a clean table format with headers and rows.

* **Final Output**: The structured data from the Extractor Agent is saved to an output file, completing the scraping process.

#### **Why don't I just use one single agent let's say the Web Scraping Agent?**
This is because the Web Scraping Agent has maximum input token limits where it'll iteratively have an expanding memory on every tool use. When it reaches the final output data, it'll most likely reach its maximum token limit and truncate the output, making the resulting data lose its quality. Here, splitting the task of scraping and extraction would my go to plan to conserve token usage and model capabilities.

## How to Run the Code
1. **Clone the Repository**
```bash
git clone https://github.com/soyokaze83/llm-web-scraper.git
cd llm-web-scraper
```
2. **`uv` Setup & Dependency Installation**
```bash
uv venv  # Create new virtual environment
uv sync  # Sync dependencies with pyproject.toml
```
3. **Fill in `.env`**
```bash
cp .env.example .env
```
Here's a description of each environment variable:
- `API_KEY`: The API key used for the model in the main script.
- `MODEL_NAME`: Model name for the model used as both scraper and extractor agents.
- `TEST_API_KEYS`: Multiple API keys separated by commas. Multiple keys are provided to avoid limit rate errors on testing. Providing a single API key would still work.

4. **Run Script**
```bash
# With python command
python src/main.py
# With uv command
uv run src/main.py
```
The script will then request for a URL and ask what would you like to scrape from the website.


## Testing
The testing is done using `pytest` where before running the actual test, we would require test cases. To support dynamic test cases based on an input URL, I'll be making use of DSPy as well to generate test cases based on the HTML structure of the website URL. In order to generate these test cases, execute the following commands:

```bash
# Example URL https://shorthorn.digitalbeef.com/
python tests/setup/generate_tests.py --url {WEBSITE_URL}
```

The output would be written to `test_cases.json` by default. After this test case file has been generated, we may now execute the test script with the following commands.

```bash
# With pytest
pytest
# With pytest (recommended verbose mode)
pytest -s -v
# With uv
uv run pytest -s -v
```