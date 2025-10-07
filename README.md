# AI Web Content Analyzer & Summarizer
A Python-based AI Web Content Analyzer and Summarizer application built with Streamlit and the Gemini API. This tool efficiently scrapes web pages, uses Generative AI (Gemini) to produce concise summaries of the text content, and intelligently extracts and displays structured HTML tables as-is, ensuring all data types are presented appropriately.

This project is a powerful web application designed to streamline content consumption. It combines robust web scraping with Google's Gemini model to analyze content from any public URL, providing both a concise, multi-paragraph summary of the main article text and a direct, structured display of any data tables found on the page.

⚙️ Technical Overview
The application is structured into three primary components:
Web Scraping & Parsing (requests, BeautifulSoup4, pandas).
Utilizes the requests library to fetch the raw HTML content.
Employs BeautifulSoup4 for targeted extraction of main text elements (h1, h2, p, li) to isolate meaningful content from boilerplate (navigation, ads, etc.).
Leverages pandas with the lxml parser to identify and structure HTML <table> elements into a clean, displayable DataFrame, bypassing summarization for tabular data.

Generative AI Summarization (google-genai):
The scraped text content is passed to the Gemini 2.5 Flash model.
A carefully engineered prompt guides the model to produce a concise, three-paragraph summary of key points and takeaways.

Interface (Streamlit):
Provides an interactive, low-code web interface for users to input URLs.
Manages the application state, displays loading spinners for better UX, and renders both the Markdown-formatted summary and the interactive data tables (st.dataframe).

Configure the Gemini API Key:
Get your API key from Google AI Studio.
Create a file named .env in the project root directory.
Add your API key to the file:
  GEMINI_API_KEY="YOUR_API_KEY_HERE"

How to Run:
Execute the Streamlit command from the project root:
  streamlit run app.py

🏗️ Code Structure Highlights:

app.py	--- The main Streamlit script containing all interface logic and function calls.

scrape_website(url)	--- Performs HTTP request, separates content into text and table components, and handles error checks.

summarize_text(client, content)	--- Encapsulates the call to the Gemini API using a specific prompt for concise summarization.

df.index = df.index + 1 ---	Critical line to adjust the pandas DataFrame index from 0-based to 1-based for human-readable table display.
