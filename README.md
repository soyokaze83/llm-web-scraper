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

The output would be written to `test_cases.json` by default. It would something like the following:
```json
{
  "url": "https://shorthorn.digitalbeef.com/",
  "tasks": [
    "Search for an animal with the registration number '12345'",
    "Search for a ranch with the name containing 'ABC'",
    "Search for an animal by tattoo 'XYZ123'",
    "Search for animals with a minimum weaning weight of 50 and a maximum weaning weight of 100",
    "Calculate the due date for a cow bred on '01/01/2025'"
  ]
}
```
 After this test case file has been generated, we may now execute the test script with the following commands.

```bash
# With pytest
pytest
# With pytest (recommended verbose mode)
pytest -s -v
# With uv
uv run pytest -s -v
```

## Example `main.py` Run
```bash
>>> python ./src/main.py
🔗 Enter link: https://shorthorn.digitalbeef.com/
❓ What would you like to scrape?
Search for animals with a minimum weaning weight of 50 and a maximum weaning weight of 100

Starting scraper...
Scraper started successfully.
--------------------------------------------------
🤖 Scraper Agent - Calling Tool: type_into_element
   Inputs: {'kwargs': {'css_selector': '#minwwt', 'text': '50'}}
👀 Observation: Successfully typed '50' into element '#minwwt'.
--------------------------------------------------

--------------------------------------------------
🤖 Scraper Agent - Calling Tool: type_into_element
   Inputs: {'kwargs': {'css_selector': '#maxwwt', 'text': '100'}}
👀 Observation: Successfully typed '100' into element '#maxwwt'.
--------------------------------------------------

--------------------------------------------------
🤖 Scraper Agent - Calling Tool: click_element
   Inputs: {'kwargs': {'css_selector': "input[value='Search...'][onclick='doSearch_Epd();']"}}
👀 Observation: Successfully clicked element 'input[value='Search...'][onclick='doSearch_Epd();']'.
--------------------------------------------------

--------------------------------------------------
🤖 Scraper Agent - Calling Tool: wait_loading
   Inputs: {'kwargs': {'css_selector': '#dvSearchResults', 'timeout': 30}}
👀 Observation: Error: Element '#dvSearchResults' did not disappear within 30 seconds.
--------------------------------------------------

--------------------------------------------------
🤖 Scraper Agent - Calling Tool: get_body_content
   Inputs: {'kwargs': {'css_selector': '#dvSearchResults'}}
👀 Observation: <div id="dvSearchResults" style="width: 100%; min-width: 650px; text-align: center; display: block;"...
--------------------------------------------------

--------------------------------------------------
🤖 Scraper Agent - Calling Tool: wait_loading
   Inputs: {'kwargs': {'css_selector': '#dvSearchResults', 'timeout': 30}}
👀 Observation: Error: Element '#dvSearchResults' did not disappear within 30 seconds.
--------------------------------------------------

--------------------------------------------------
🤖 Scraper Agent - Calling Tool: get_body_content
   Inputs: {'kwargs': {'css_selector': '#dvSearchResults'}}
👀 Observation: <div id="dvSearchResults" style="width: 100%; min-width: 650px; text-align: center; display: block;"...
--------------------------------------------------

--------------------------------------------------
🤖 Scraper Agent - Calling Tool: _store_and_finish
   Inputs: {'kwargs': {'css_selector': '#dvSearchResults'}}
Storing final HTML content...
👀 Observation: Successfully retrieved and stored the HTML content from selector '#dvSearchResults'. The task is com...
--------------------------------------------------

Extracting final data...
Stopping scraper...
Scraper stopped successfully.
Answer: header=['Reg # Tattoo Name', 'CED', 'BW', 'WW', 'YW', 'MK', 'TM', 'CEM', 'ST', 'YG', 'CW', 'REA', 'FAT', 'MB', '$CEZ', '$BMI', '$CPI', '$F'] data=[['AR4397149 JSF 84N JSF MISS ME 84N', '2', '5.7', '95', '139', '19', '66', '2', '15', '-0.3', '31', '0.63', '-0.08', '0.03', '-6.49', '148.61', '132.11', '70.61'], ['AR4294554 501G UI EXCHANGE 501G', '4', '7.3', '94', '144', '27', '74', '2', '5', '-0.08', '67', '0.87', '-0.02', '0.51', '-0.03', '151.55', '123.75', '86.03'], ['AR4294560 538G UI DENALI 538G', '12', '2.2', '90', '151', '22', '66', '7', '12', '-0.19', '52', '0.71', '-0.05', '0.57', '23.31', '155.18', '167.13', '83.01'], ['AR4375666 212L HOFF MISS 1872 SH 212L', '9', '2.5', '89', '149', '29', '73', '7', '11', '-0.12', '71', '0.84', '-0.04', '0.44', '15.57', '151.36', '156.79', '85.43'],...]]

Dumping results into result/result_2932aede-a21e-4ba7-9ac1-38468fa95136.json...
Successfully saved results to result_2932aede-a21e-4ba7-9ac1-38468fa95136.json!
```

## Personal Takeaways
I've done my fair share of website scraping, but scraping in an agentic fashion is a totally different beast. The difficulties I faced in building this project is how I would manage the waiting time of the agent. In my previous tries, the agent would always fail to wait for the data to correctly fetch and just return empty outputs on the resulting header and row data. The fix to this was enforcing better prompt rules to the scraper agent's DSPy signature for it to actually retry the waiting process again. Another problem would be the rate limit error for the model's capabilities. Since I'm using Google's Free Tier, I only used model from the Gemini families (but don't worry, DSPy works with most OpenAI API compatible models) especially Gemini 2.0 Flash. Even with its one million tokens per minute usage, I sometimes still hit a truncation warning. Due to this, I found out about splitting the task of both scraping or processing the website to locate the results, and then extracting the result into data in header and row format.

Challenges will always be tough, but I still do take enjoyment in doing something like this where I could always learn new things in the engineering sphere. I hope that my solution will be sufficient to go to the next round! 😁🙌