import streamlit as st
import requests
from bs4 import BeautifulSoup

# Fetch news from Inshorts
url = "https://www.inshorts.com/en/read"
r = requests.get(url)
content = r.content
soup = BeautifulSoup(content, 'html.parser')
all_news = soup.find_all('div', {'class': 'news-card z-depth-1'})

# Since words.txt is empty, we just use an empty list
common_words = []

# Extract and process news
news_data = []
for news in all_news:
    try:
        headline = news.find('span', {'itemprop': 'headline'}).text.strip()
        author = news.find('span', {'class': 'author'}).text.strip()
        body = news.find('div', {'itemprop': 'articleBody'}).text.strip()
        anchor = news.find('a', {'class': 'source'})
        source_url = anchor.get('href') if anchor else ''
        image_div = news.find('div', {'class': 'news-card-image'})
        image_url = image_div.get('style')[23:-3] if image_div else ''

        # Extract keyword (now all words are considered)
        headline_words = headline.replace('.', '').replace(',', '').split()
        body_words = body.replace('.', ' ').replace(',', '').split()
        word_counts = [
            body_words.count(word)
            for word in headline_words
        ]
        keyword = headline_words[word_counts.index(max(word_counts))] if word_counts else ""

        news_data.append({
            "Headline": headline,
            "Author": author,
            "Body": body,
            "Source URL": source_url,
            "Image": image_url,
            "Keyword": keyword
        })
    except Exception as e:
        continue

# Streamlit UI
st.set_page_config(page_title="Inshorts News", layout="wide")
st.title("🗞️ Inshorts News Summary")
st.write("News fetched live from [Inshorts](https://www.inshorts.com/en/read).")

for item in news_data:
    with st.container():
        st.markdown(f"### {item['Headline']}")
        cols = st.columns([1, 3])
        with cols[0]:
            if item['Image']:
                st.image(item['Image'], width=200)
        with cols[1]:
            st.write(f"**Author**: {item['Author']}")
            st.write(item['Body'])
            if item['Source URL']:
                st.markdown(f"[🔗 Read more]({item['Source URL']})")
            st.markdown(f"**Keyword**: `#{item['Keyword']}`")
        st.markdown("---")
