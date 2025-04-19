import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Streamlit App Config
st.set_page_config(page_title="START by BHIVE Events Scraper", layout="wide")
st.title("🔍 START by BHIVE Live Event Scraper")

# Function to scrape event data
def scrape_luma_events():
    url = "https://lu.ma/START_by_BHIVE"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        events = []
        event_cards = soup.find_all('div', class_='event-card')  # Update this selector based on actual page structure
        
        for card in event_cards:
            try:
                name = card.find('h3').text.strip()
                hosts = ", ".join([host.text.strip() for host in card.select('.host-names')])  # Update selector
                events.append({
                    "Event Name": name,
                    "Host Names": hosts if hosts else "Not provided",
                    "Date": card.find('time')['datetime'] if card.find('time') else "Not specified",
                    "LinkedIn Profiles": "Not provided"  # Will need additional logic to find these
                })
            except Exception as e:
                st.warning(f"Error parsing one event: {str(e)}")
                continue
        
        return pd.DataFrame(events)
    
    except Exception as e:
        st.error(f"Failed to scrape data: {str(e)}")
        return pd.DataFrame()

# Main App
with st.spinner("🔍 Scraping latest events from START by BHIVE..."):
    df = scrape_luma_events()

if not df.empty:
    st.success(f"✅ Found {len(df)} events (as of {datetime.now().strftime('%Y-%m-%d %H:%M')})")
    
    # Search and Filter
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input("Search events or hosts", help="Type to filter results")
    with col2:
        date_filter = st.selectbox("Filter by date", ["All dates"] + sorted(df['Date'].unique().tolist()))
    
    # Apply filters
    if search_term:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]
    if date_filter != "All dates":
        df = df[df['Date'] == date_filter]

    # Display results
    st.dataframe(
        df,
        column_config={
            "Event Name": st.column_config.TextColumn("Event", width="large"),
            "Host Names": st.column_config.TextColumn("Hosts"),
            "Date": st.column_config.DateColumn("Date"),
            "LinkedIn Profiles": st.column_config.LinkColumn("LinkedIn", disabled=True)
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Download
    st.download_button(
        label="📥 Download as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name=f"bhive_events_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
else:
    st.warning("No events found. The website structure may have changed.")

st.markdown("---")
st.caption("ℹ️ Note: This app scrapes data live from https://lu.ma/START_by_BHIVE. LinkedIn profiles require manual lookup.")
