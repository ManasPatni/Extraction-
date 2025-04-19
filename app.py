import streamlit as st
import requests
from bs4 import BeautifulSoup

def extract_event_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        return [], [], []

    soup = BeautifulSoup(response.text, 'html.parser')

    events = soup.find_all('div', class_='event-preview')
    data = []

    for event in events:
        # Event Name
        event_name_tag = event.find('a', class_='event-title')
        event_name = event_name_tag.text.strip() if event_name_tag else "Not found"

        # Host Name
        host_name_tag = event.find('div', class_='event-hosts')
        host_names = host_name_tag.text.strip() if host_name_tag else "Not found"

        # LinkedIn URLs (if available)
        linkedin_urls = []
        for link in event.find_all('a', href=True):
            if "linkedin.com" in link['href']:
                linkedin_urls.append(link['href'])

        data.append({
            'event_name': event_name,
            'host_names': host_names,
            'linkedin_urls': linkedin_urls or ["Not available"]
        })

    return data

st.set_page_config(page_title="Luma Event Scraper", layout="centered")
st.title("🔍 Luma Event Info Extractor")

url = st.text_input("Paste the Luma event page URL:")

if url:
    with st.spinner("Extracting data..."):
        try:
            results = extract_event_data(url)
            if results:
                for idx, event in enumerate(results, 1):
                    st.subheader(f"Event {idx}: {event['event_name']}")
                    st.write(f"**Host(s):** {event['host_names']}")
                    st.write("**LinkedIn Profiles:**")
                    for link in event['linkedin_urls']:
                        st.write(f"- {link}")
            else:
                st.warning("No events found or page structure has changed.")
        except Exception as e:
            st.error(f"Error: {e}")
