import streamlit as st
import requests
from bs4 import BeautifulSoup
from groq import Groq

# Hardcoded Groq API key
GROQ_API_KEY = "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"

# Function to extract event data
def extract_event_data(url):
    response = requests.get(url)
    if response.status_code != 200:
        return []

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

# Function to enhance with Groq AI
def enhance_with_groq(data, api_key):
    client = Groq(api_key=api_key)
    enhanced_data = []

    for event in data:
        prompt = f"""
You are given details of an event:
Event Name: {event['event_name']}
Host Names: {event['host_names']}
LinkedIn URLs: {', '.join(event['linkedin_urls'])}

Your task is:
1. Provide a short, catchy summary of this event.
2. Make a guess about the kind of audience it targets.
3. Clean up the host name formatting.
4. Return it in a readable format.
"""
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192"
        )

        result = chat_completion.choices[0].message.content
        enhanced_data.append((event['event_name'], result))

    return enhanced_data

# Streamlit UI
st.set_page_config(page_title="Luma Event Scraper + Groq AI", layout="centered")
st.title("🤖 Luma Event Info Extractor + Groq AI")

url = st.text_input("Paste the Luma event page URL:")

if url:
    with st.spinner("Extracting and enhancing data..."):
        try:
            raw_data = extract_event_data(url)
            if raw_data:
                enhanced = enhance_with_groq(raw_data, GROQ_API_KEY)
                for idx, (event_name, enhanced_text) in enumerate(enhanced, 1):
                    st.subheader(f"Event {idx}: {event_name}")
                    st.markdown(enhanced_text)
            else:
                st.warning("No events found or page structure has changed.")
        except Exception as e:
            st.error(f"Error: {e}")
