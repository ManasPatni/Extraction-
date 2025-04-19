import requests
from bs4 import BeautifulSoup
import streamlit as st

# Function to extract the event details
def extract_event_details(event_url):
    """Extract event details including the event name, host name, and LinkedIn profile URL."""
    try:
        # Make a request to the event detail page
        response = requests.get(event_url)
        response.raise_for_status()
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract event name
        event_name = soup.find('h1', class_='event-title').text.strip()

        # Extract the host name and LinkedIn URL
        host_section = soup.find('section', class_='host-section')
        host_name = host_section.find('span', class_='host-name').text.strip()
        linkedin_url = host_section.find('a', class_='linkedin-link')['href']
        
        return event_name, host_name, linkedin_url
    except Exception as e:
        return None, None, f"Error: {str(e)}"

# Function to scrape the event listing page
def scrape_event_listing(listing_url):
    """Scrape event listing page for all event details."""
    try:
        # Send a request to the event listing page
        response = requests.get(listing_url)
        response.raise_for_status()
        
        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all event links on the listing page
        event_links = []
        for event in soup.find_all('a', class_='event-link'):
            event_links.append(event['href'])
        
        # Extract details for each event
        events = []
        for event_url in event_links:
            event_name, host_name, linkedin_url = extract_event_details(event_url)
            if event_name and host_name:
                events.append((event_name, host_name, linkedin_url))
        
        return events
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize Streamlit app
st.set_page_config(page_title="Event Details Scraper", layout="wide")
st.title("Event Details Scraper")
st.markdown("This app extracts event information including the event name, host name, and LinkedIn profile URL for each event.")

# Start the scraping process
listing_url = "https://lu.ma/START_by_BHIVE"  # Listing page URL

# Scrape events
events = scrape_event_listing(listing_url)

if isinstance(events, list) and events:
    # Display the event information in Streamlit
    for event_name, host_name, linkedin_url in events:
        st.markdown(f"### {event_name}")
        st.markdown(f"**Host Name**: {host_name}")
        st.markdown(f"[LinkedIn Profile]({linkedin_url})")
        st.markdown("---")
else:
    st.error(f"Error scraping events: {events}")
