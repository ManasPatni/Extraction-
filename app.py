import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

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

st.markdown("## 📅 Lu.ma Event Scraper")
st.markdown("Paste the URL of any Lu.ma listing page (e.g., [https://lu.ma/START_by_BHIVE](https://lu.ma/START_by_BHIVE))")

listing_url = st.text_input("Paste the url:", value="https://lu.ma/START_by_BHIVE")

# --- Scraping Function using Selenium ---
@st.cache_data(show_spinner=True)
def scrape_luma_events_selenium(base_url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(base_url)
    time.sleep(3)  # Let JS load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    events_data = []

    event_links = soup.find_all('a', href=True)
    seen = set()

    for link in event_links:
        href = link['href']
        if href.startswith("/event/") and href not in seen:
            seen.add(href)
            event_url = urljoin("https://lu.ma", href)
            event_name = link.get_text(strip=True)

            driver.get(event_url)
            time.sleep(2)
            event_soup = BeautifulSoup(driver.page_source, 'html.parser')

            host_links = event_soup.find_all('a', href=True)
            for a in host_links:
                profile_href = a['href']
                if profile_href.startswith("/p/"):
                    host_url = urljoin("https://lu.ma", profile_href)

                    driver.get(host_url)
                    time.sleep(2)
                    host_soup = BeautifulSoup(driver.page_source, 'html.parser')

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

    driver.quit()
    return pd.DataFrame(events_data)

# --- Main Logic ---
if st.button("🚀 Start Scraping"):
    if listing_url.strip() == "":
        st.warning("Please enter a valid Lu.ma listing URL.")
    else:
        with st.spinner("Scraping event and host data..."):
            try:
                df = scrape_luma_events_selenium(listing_url)
                if not df.empty:
                    st.success("✅ Scraping Complete!")
                    st.dataframe(df, use_container_width=True)

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
