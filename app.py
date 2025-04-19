import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

st.set_page_config(page_title="Lu.ma Event Scraper", page_icon="📅", layout="wide")

# Dark mode style
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stTextInput>div>div>input {
        background-color: #262730;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title and Input UI ---
st.markdown("## 📅 Lu.ma Event Scraper")
st.markdown("Paste the URL of any Lu.ma listing page (e.g., [https://lu.ma/START_by_BHIVE](https://lu.ma/START_by_BHIVE))")

listing_url = st.text_input("Lu.ma Event Listing URL:", value="https://lu.ma/START_by_BHIVE")

# --- Scraping Function ---
@st.cache_data(show_spinner=True)
def scrape_luma_events(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    events_data = []

    # Extract event URLs
    event_links = soup.find_all('a', href=True)
    seen = set()

    for link in event_links:
        href = link['href']
        if href.startswith("/event/") and href not in seen:
            seen.add(href)
            event_url = urljoin("https://lu.ma", href)
            event_name = link.get_text(strip=True)

            # Visit event detail page
            event_detail = requests.get(event_url)
            event_soup = BeautifulSoup(event_detail.content, 'html.parser')

            # Find host profile links
            host_links = event_soup.find_all('a', href=True)
            for a in host_links:
                profile_href = a['href']
                if profile_href.startswith("/p/"):
                    host_url = urljoin("https://lu.ma", profile_href)

                    host_detail = requests.get(host_url)
                    host_soup = BeautifulSoup(host_detail.content, 'html.parser')

                    host_name = host_soup.find('h1').get_text(strip=True) if host_soup.find('h1') else "N/A"

                    linkedin_url = ""
                    for tag in host_soup.find_all('a', href=True):
                        if "linkedin.com" in tag['href']:
                            linkedin_url = tag['href']
                            break

                    events_data.append({
                        "Event Name": event_name,
                        "Host Name": host_name,
                        "LinkedIn Profile URL": linkedin_url
                    })

    return pd.DataFrame(events_data)

# --- Main Logic ---
if st.button("🚀 Start Scraping"):
    if listing_url.strip() == "":
        st.warning("Please enter a valid Lu.ma listing URL.")
    else:
        with st.spinner("Scraping event and host data..."):
            try:
                df = scrape_luma_events(listing_url)
                if not df.empty:
                    st.success("✅ Scraping Complete!")
                    st.dataframe(df, use_container_width=True)

                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name='event_hosts.csv',
                        mime='text/csv'
                    )
                else:
                    st.warning("No data found. Please check the page structure or try again later.")
            except Exception as e:
                st.error(f"Error occurred: {e}")
