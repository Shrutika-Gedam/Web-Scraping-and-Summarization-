import streamlit as st
import requests
from bs4 import BeautifulSoup
from google import genai
import os
from dotenv import load_dotenv
import pandas as pd # Import pandas for handling tables
import io

# --- Core Functions ---

def scrape_website(url):
    """
    Fetches content from a URL and extracts both text and the first table (if any).
    Returns a dictionary: {'text_content': str, 'table_df': pd.DataFrame or None, 'error': str or None}
    """
    results = {'text_content': None, 'table_df': None, 'error': None}
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=15, headers=headers)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        results['error'] = f"Error fetching URL: {e}"
        return results

    # 1. Table Extraction (Try using pandas)
    try:
        dataframes = pd.read_html(io.StringIO(response.text))
        if dataframes:
            # Successfully extracted at least one table
            df = dataframes[0]
            
            # === THE CHANGE IS HERE ===
            # Increment the DataFrame's index by 1 so it starts at 1 instead of 0
            df.index = df.index + 1 
            # ==========================
            
            results['table_df'] = df # Store the modified DataFrame
            st.success("A data table was successfully extracted from the page.")
    except ImportError:
        st.error("Missing optional dependency 'lxml' or 'html5lib' for table parsing. Run `pip install lxml`.")
    except Exception as e:
        st.info(f"No structured tables found or could not parse table with pandas. Proceeding with text summary.")

    # 2. Text Extraction Strategy
    soup = BeautifulSoup(response.content, 'html.parser')
    
    main_content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
    
    text_content = ' '.join([tag.get_text(strip=True) for tag in main_content_tags if len(tag.get_text(strip=True)) > 20])
    
    if len(text_content.strip()) < 100 and results['table_df'] is None:
        results['error'] = "Content too short or unavailable to summarize."
    else:
        results['text_content'] = text_content
        
    return results

# Initialize Gemini Client (outside the function)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY environment variable not set. Please check your .env file.")
    st.stop()
    
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    st.error(f"Error initializing Gemini Client: {e}")
    st.stop()


def summarize_text(client: genai.Client, text_content: str):
    """Generates a concise summary of the text using the Gemini API."""
    prompt = (
        "Summarize the following text content concisely, providing the main "
        "points and key takeaways in no more than three paragraphs. "
        "Ensure the summary is easy to read.\n\n"
        f"TEXT TO SUMMARIZE:\n\n{text_content}"
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {e}"


# --- Streamlit Interface ---

st.title("🌐 AI Web Content Summarizer & Table Extractor")
st.markdown("Enter a URL. The app will summarize the main text content and display any detected data tables as-is.")

# 1. User Input
user_url = st.text_input("Enter the Website URL:", value=" ")

# 2. Action Button
if st.button("Analyze Content"):
    if not user_url:
        st.warning("Please enter a valid URL.")
    else:
        # --- Step 1: Scraping ---
        with st.spinner(f"Scraping and analyzing content from {user_url}..."):
            scrape_result = scrape_website(user_url)

        # Handle Errors
        if scrape_result['error']:
            st.error(scrape_result['error'])
            st.stop()
        
        # --- Step 2: Display Table (if found) ---
        if scrape_result['table_df'] is not None:
            st.subheader("📊 Detected Data Table")
            st.info("The following table was extracted from the page and is displayed directly:")
            # Use st.dataframe to display the table
            st.dataframe(scrape_result['table_df'])
            st.markdown("---") # Separator
        else:
            st.info("No primary data table was detected on this page.")
        
        # --- Step 3: Summarize Text Content ---
        text_to_summarize = scrape_result['text_content']
        
        if text_to_summarize and len(text_to_summarize.strip()) > 100:
            st.success(f"Scraped {len(text_to_summarize):,} characters of text. Now summarizing...")
            
            with st.spinner("Calling Gemini API for summarization..."):
                summary = summarize_text(client, text_to_summarize)
            
            # 4. Display Summary Result
            st.subheader("✨ Page Text Summary")
            st.markdown(summary)
            
            st.markdown("---")
            with st.expander("View Full Scraped Text (for reference)"):
                 st.code(text_to_summarize[:2000] + "..." if len(text_to_summarize) > 2000 else text_to_summarize)
        
        else:
            st.warning("Not enough text content available for summarization.")