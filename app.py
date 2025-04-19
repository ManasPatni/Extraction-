import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import time

st.set_page_config(page_title="Event Scraper", layout="wide")
st.title("🎯 Event & Host LinkedIn Scraper")
st.markdown("Scrapes event data from [START_by_BHIVE](https://lu.ma/START_by_BHIVE)")

# Button to start scraping
if st.button("Start Scraping"):
    with st.spinner("Scraping event data, please wait..."):

        base_url = "https://lu.ma/START_by_BHIVE"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(base_url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")

        events_data = []

        # STEP 1: Find all event links
        events = soup.find_all("a", href=True)
        event_links = [urljoin(base_url, a["href"]) for a in events if "/event/" in a["href"]]

        unique_event_links = list(set(event_links))  # Remove duplicates

        for event_url in unique_event_links:
            try:
                event_page = requests.get(event_url, headers=headers)
                event_soup = BeautifulSoup(event_page.content, "html.parser")

                # Get Event Name
                title_tag = event_soup.find("h1")
                event_name = title_tag.text.strip() if title_tag else "N/A"

                # Hosts are in sidebar (look for 'Hosted by' section)
                hosted_by_section = event_soup.find_all("a", href=True)
                for host_tag in hosted_by_section:
                    if "/u/" in host_tag["href"]:  # Host profile links
                        host_name = host_tag.text.strip()
                        host_profile_url = urljoin("https://lu.ma", host_tag["href"])

                        # Go to host profile page to get LinkedIn
                        host_page = requests.get(host_profile_url, headers=headers)
                        host_soup = BeautifulSoup(host_page.content, "html.parser")

                        linkedin_url = "N/A"
                        for a_tag in host_soup.find_all("a", href=True):
                            if "linkedin.com/in" in a_tag["href"]:
                                linkedin_url = a_tag["href"]
                                break

                        events_data.append({
                            "Event Name": event_name,
                            "Host Name": host_name,
                            "LinkedIn Profile URL": linkedin_url
                        })

                time.sleep(1)  # To avoid rate limiting

            except Exception as e:
                st.warning(f"Failed to scrape {event_url}: {str(e)}")

        # Convert to DataFrame
        df = pd.DataFrame(events_data)

        if not df.empty:
            st.success(f"✅ Scraped {len(df)} host entries.")
            st.dataframe(df)

            # Download CSV
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="event_hosts_data.csv",
                mime="text/csv"
            )
        else:
            st.warning("No event data found.")
