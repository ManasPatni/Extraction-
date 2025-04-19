import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from io import BytesIO

st.set_page_config(page_title="Event Host Scraper", layout="wide")
st.title("🔍 Event Host & LinkedIn Scraper")
st.markdown("Scrape event details from [START by BHIVE](https://lu.ma/START_by_BHIVE)")

st.info("Click the button below to start scraping all events, hosts, and LinkedIn URLs.", icon="ℹ️")

# Function to scrape data
@st.cache_data(show_spinner=True)
def scrape_events():
    base_url = "https://lu.ma/START_by_BHIVE"
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    events_data = []

    # Extract all event cards (You may need to inspect and tweak the selector)
    event_links = soup.find_all('a', href=True)

    for link in event_links:
        href = link['href']
        if href.startswith("/event/"):
            event_url = urljoin("https://lu.ma", href)
            event_name = link.get_text(strip=True)

            # Visit event detail page
            event_detail = requests.get(event_url)
            event_soup = BeautifulSoup(event_detail.content, 'html.parser')

            # Try to find hosted-by section
            host_section = event_soup.find_all('a', href=True)
            for a in host_section:
                profile_link = a['href']
                if profile_link.startswith("/p/"):
                    host_url = urljoin("https://lu.ma", profile_link)

                    # Visit host page
                    host_detail = requests.get(host_url)
                    host_soup = BeautifulSoup(host_detail.content, 'html.parser')

                    host_name = host_soup.find('h1').get_text(strip=True) if host_soup.find('h1') else "N/A"
                    linkedin_url = ""
                    for a_tag in host_soup.find_all('a', href=True):
                        if "linkedin.com" in a_tag['href']:
                            linkedin_url = a_tag['href']
                            break

                    events_data.append({
                        "Event Name": event_name,
                        "Host Name": host_name,
                        "LinkedIn Profile URL": linkedin_url
                    })

    return pd.DataFrame(events_data)

# Button to start scraping
if st.button("🚀 Start Scraping"):
    with st.spinner("Scraping event and host data..."):
        df = scrape_events()
        st.success("Scraping Complete!")
        st.dataframe(df, use_container_width=True)

        # Download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name='event_hosts.csv',
            mime='text/csv'
        )
