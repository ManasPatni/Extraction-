import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

# Optional: Groq API Integration
try:
    chat = ChatGroq(
        model_name="llama3-70b-8192", 
        temperature=0.7, 
        groq_api_key="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"
    )
except Exception as e:
    st.error(f"⚠️ Chat model initialization failed: {str(e)}")
    chat = None 

# App config
st.set_page_config(page_title="Lu.ma Event Scraper", layout="centered")
st.title("📅 Lu.ma Event Scraper with Host Info")
st.markdown("Scrape **Event Name**, **Host Name**, and **LinkedIn Profile URL** from [START by BHIVE](https://lu.ma/START_by_BHIVE)")

start_scraping = st.button("🚀 Start Scraping Events")

@st.cache_data
def fetch_event_links(main_url):
    res = requests.get(main_url)
    soup = BeautifulSoup(res.content, 'html.parser')
    event_links = []
    for a in soup.find_all("a", href=True):
        if '/event/' in a['href']:
            full_url = urljoin(main_url, a['href'])
            event_links.append(full_url)
    return list(set(event_links))

def summarize_with_groq(text):
    try:
        response = openai.ChatCompletion.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes event descriptions."},
                {"role": "user", "content": text}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Summary failed: {e}"

def extract_event_data(event_url):
    try:
        res = requests.get(event_url)
        soup = BeautifulSoup(res.content, 'html.parser')

        event_name_tag = soup.find('h1')
        event_name = event_name_tag.get_text(strip=True) if event_name_tag else "N/A"

        # Event description (optional Groq)
        description = soup.find('div', {'data-testid': 'event-description'})
        event_description = description.get_text(strip=True) if description else "No description available"

        summary = summarize_with_groq(event_description) if use_groq else "Not generated"

        host_data = []
        host_section = soup.find_all('a', href=True)
        for host in host_section:
            if "/u/" in host['href']:
                host_name = host.text.strip()
                host_profile_url = urljoin(event_url, host['href'])

                # Visit host profile
                host_res = requests.get(host_profile_url)
                host_soup = BeautifulSoup(host_res.content, 'html.parser')

                linkedin_tag = host_soup.find('a', href=True, string=lambda x: x and 'linkedin.com' in x)
                linkedin_url = linkedin_tag['href'] if linkedin_tag else "Not Found"

                host_data.append({
                    "Event Name": event_name,
                    "Host Name": host_name,
                    "LinkedIn Profile URL": linkedin_url,
                    "Event Summary (via Groq)" if use_groq else "Event Summary": summary
                })

        return host_data
    except Exception as e:
        st.warning(f"Failed to extract data from {event_url} due to {e}")
        return []

if start_scraping:
    main_url = "https://lu.ma/START_by_BHIVE"
    st.info("Fetching events from Lu.ma...")
    event_urls = fetch_event_links(main_url)

    st.success(f"Found {len(event_urls)} event pages!")
    scraped_data = []

    progress_bar = st.progress(0)

    for idx, event_url in enumerate(event_urls):
        st.write(f"🔍 Scraping: {event_url}")
        event_data = extract_event_data(event_url)
        scraped_data.extend(event_data)
        progress_bar.progress((idx + 1) / len(event_urls))
        time.sleep(1)

    if scraped_data:
        df = pd.DataFrame(scraped_data)
        st.success("✅ Scraping completed successfully!")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "event_data.csv", "text/csv")
    else:
        st.error("❌ No data extracted.")
