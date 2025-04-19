import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def extract_past_event_data_from_url(url):
    """Extracts past event data (Event Name, Host Name, LinkedIn URL) from the given URL."""
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
            
            # Find the event date (this will depend on the actual HTML structure)
            event_date_str = event.find('span', class_='event-date').get_text(strip=True) if event.find('span', class_='event-date') else None

            # If the event date exists, convert it to a datetime object and check if it's a past event
            if event_date_str:
                # Format the date string (adjust the format to match the page's date format)
                try:
                    event_date = datetime.strptime(event_date_str, "%B %d, %Y")  # Adjust format as needed
                    if event_date < datetime.now():  # Past event
                        events_data.append({
                            'Event Name': event_name,
                            'Host Name': host_name,
                            'LinkedIn Profile URL': linkedin_url,
                            'Event Date': event_date_str
                        })
                except ValueError:
                    continue  # Skip if the date format is incorrect or parsing fails
            else:
                continue  # Skip if no event date is found

        return events_data
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

# Streamlit UI setup
st.title("Past Event Data Extraction")
st.write("Enter a URL to extract past event details:")

# URL input from the user
url = st.text_input("Enter URL:")

if url:
    # Extract past event data from the URL
    events_data = extract_past_event_data_from_url(url)

    if isinstance(events_data, list):
        if events_data:
            # Convert to DataFrame
            df = pd.DataFrame(events_data)

            # Save to CSV file
            csv_file = df.to_csv(index=False)

            # Provide download link for the CSV file
            st.write("Here is the extracted data for past events:")
            st.dataframe(df)  # Display the data in the app
            st.download_button(
                label="Download CSV",
                data=csv_file,
                file_name="past_event_data.csv",
                mime="text/csv"
            )
        else:
            st.write("No past events found on the page.")
    else:
        st.write(events_data)  # If there's an error message
