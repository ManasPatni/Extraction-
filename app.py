import streamlit as st
import requests
from bs4 import BeautifulSoup

def extract_data_from_url(url):
    """Extracts data from the given URL."""
    try:
        # Sending a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Check if the content is HTML
        if 'html' in response.headers['Content-Type']:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup.prettify()  # Prettified HTML content
        # If it's JSON (you can handle this differently if needed)
        elif 'json' in response.headers['Content-Type']:
            return response.json()  # Return JSON data
        else:
            return response.text  # Return raw text content
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

# Streamlit UI setup
st.title("Data Extraction from URL")
st.write("Enter a URL to extract data:")

# URL input from the user
url = st.text_input("Enter URL:")

if url:
    # Extract data from the URL
    data = extract_data_from_url(url)
    st.write("Extracted Data:")
    if isinstance(data, str):
        st.code(data)  # Display as code block
    else:
        st.json(data)  # Display as JSON if it's JSON data
