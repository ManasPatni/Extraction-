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

# Add a button to start the extraction
if st.button("Extract Data"):
    if url:
        # Display a loading spinner while fetching data
        with st.spinner("Fetching data from the URL..."):
            data = extract_data_from_url(url)
            st.success("Data extracted successfully!")
            
            # Display extracted data in a formatted way
            st.subheader("Extracted Data:")
            if isinstance(data, str):
                if len(data) > 2000:  # If the data is too large, display a snippet
                    st.write(f"Displaying first 2000 characters of the extracted data:")
                    st.code(data[:2000])  # Display as code block
                    if len(data) > 2000:
                        st.warning("Data is too long, showing only a snippet.")
                else:
                    st.code(data)  # Display as code block
            else:
                st.json(data)  # Display as JSON if it's JSON data
    else:
        st.error("Please enter a valid URL.")

# Add a description and instructions
st.markdown("""
This app extracts data from the provided URL. You can input a website link, and it will retrieve and display the raw HTML or JSON data.
- HTML content will be prettified.
- JSON content will be formatted for better readability.
- If the URL is not valid or the content is not fetched successfully, an error message will be displayed.
""")
