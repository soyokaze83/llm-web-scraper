# LLM Web Scraper

1. The user will input the website's URL and add natural language input e.g. "Get the table for cows from Alabama with weight more than 50 pounds".

2. A python script receives these inputs, and first requests the content of the website URL.

3. The content of the requested or scraped URL is passed to an LLM as well as the natural language input from the user.

4. The LLM acts as an agent to finds out the appropriate tool call based on the URL content and user natural language command. Example, if the user inputs "Get the table for cows from Alabama", then the LLM calls the agentic tool to do dynamic filling of the input from the URL.

5. The form input tool then gets back the requested content with valid data after inputting the forms in the webiste URL.

6. The LLM then extracts the valid data based on response content obtained after filling the inputs based on user natural language input.