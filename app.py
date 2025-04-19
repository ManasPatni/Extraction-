import streamlit as st
import requests
from bs4 import BeautifulSoup

def extract_event_data(url):
    """Extracts Event Name, Host Name, and LinkedIn Profile URL from the given URL."""
    try:
        # Sending a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Check if the content is HTML
        if 'html' in response.headers['Content-Type']:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract Event Name (adjust the selector as per actual webpage structure)
            event_name = soup.find('h1', class_='event-title')  # Modify the class as needed
            event_name = event_name.text.strip() if event_name else "Event Name not found"

            # Extract Host Name (adjust the selector as per actual webpage structure)
            host_name = soup.find('div', class_='host-name')  # Modify the class as needed
            host_name = host_name.text.strip() if host_name else "Host Name not found"

            # Extract LinkedIn Profile URL (adjust the selector as per actual webpage structure)
            linkedin_url = soup.find('a', href=True, class_='linkedin-profile')  # Modify the class as needed
            linkedin_url = linkedin_url['href'] if linkedin_url else "LinkedIn Profile URL not found"

            return event_name, host_name, linkedin_url
        else:
            return "Error: The content is not HTML", None, None
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}", None, None

# Streamlit UI setup
st.title("Event Data Extraction")
st.write("Enter a URL to extract Event Details:")

# URL input from the user
url = st.text_input("Enter URL:")

# Add a button to start the extraction
if st.button("Extract Event Data"):
    if url:
        # Display a loading spinner while fetching data
        with st.spinner("Fetching event data from the URL..."):
            event_name, host_name, linkedin_url = extract_event_data(url)
            if event_name and host_name and linkedin_url:
                st.success("Data extracted successfully!")

                # Display extracted data
                st.subheader("Event Details:")
                st.write(f"**Event Name:** {event_name}")
                st.write(f"**Host Name:** {host_name}")
                st.write(f"**LinkedIn Profile URL of the Host:** [{linkedin_url}]({linkedin_url})")
            else:
                st.error("Error extracting event data.")
    else:
        st.error("Please enter a valid URL.")

# Add a description and instructions
st.markdown("""
This app extracts specific event details from the provided URL:
- **Event Name**
- **Host Name**
- **LinkedIn Profile URL of the Host**

Ensure the provided webpage contains the event data in the correct format. If the event details are not found, the app will return an error message.
""")
