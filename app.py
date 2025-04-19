import streamlit as st
import requests
from bs4 import BeautifulSoup

def extract_event_data_from_url(url):
    """Extracts event data (Event Name, Host Name, LinkedIn URL) from the given URL."""
    try:
        # Sending a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Parse HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Initialize a list to store event data
        events_data = []

        # Find all event containers (this will depend on the actual HTML structure)
        events = soup.find_all('div', class_='event-container')  # Update with actual HTML structure

        for event in events:
            event_name = event.find('h2', class_='event-name').get_text(strip=True) if event.find('h2', class_='event-name') else 'N/A'
            host_name = event.find('p', class_='host-name').get_text(strip=True) if event.find('p', class_='host-name') else 'N/A'
            linkedin_url = event.find('a', href=True, text='LinkedIn')
            linkedin_url = linkedin_url['href'] if linkedin_url else 'N/A'

            # Append the extracted data to the events_data list
            events_data.append({
                'Event Name': event_name,
                'Host Name': host_name,
                'LinkedIn Profile URL': linkedin_url
            })

        return events_data
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

# Streamlit UI setup
st.title("Event Data Extraction")
st.write("Enter a URL to extract event details:")

# URL input from the user
url = st.text_input("Enter URL:")

if url:
    # Extract event data from the URL
    events_data = extract_event_data_from_url(url)

    if isinstance(events_data, list):
        if events_data:
            # Display the extracted data directly
            st.write("Extracted Event Data:")
            for event in events_data:
                st.write(f"**Event Name:** {event['Event Name']}")
                st.write(f"**Host Name:** {event['Host Name']}")
                st.write(f"**LinkedIn Profile URL:** {event['LinkedIn Profile URL']}")
                st.write("---")  # Separator for each event
        else:
            st.write("No events found on the page.")
    else:
        st.write(events_data)  # If there's an error message
