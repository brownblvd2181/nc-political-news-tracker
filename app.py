import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Define Google News RSS feeds for each politician
URLS = {
    "Alma Adams": "https://news.google.com/rss/search?q=Alma+Adams+North+Carolina",
    "Don Davis": "https://news.google.com/rss/search?q=Don+Davis+North+Carolina"
}

def get_news(person, limit=5):
    """Fetch the top news articles for the given person from Google News RSS."""
    feed_url = URLS.get(person)
    if not feed_url:
        return []
    
    response = requests.get(feed_url)
    soup = BeautifulSoup(response.content, "xml")
    
    articles = []
    for item in soup.find_all("item")[:limit]:  # Get top 'limit' articles
        articles.append({
            "Title": item.title.text,
            "Link": f'<a href="{item.link.text}" target="_blank">Read More</a>',
            "Published": item.pubDate.text
        })
    
    return articles

# Streamlit UI
st.set_page_config(page_title="NC Political News Tracker", page_icon="🗳️")

st.title("🗳️ NC Political News Tracker")
st.subheader("Get the latest news on Alma Adams & Don Davis")

# Multi-select widget to choose politicians
selected_politicians = st.multiselect("Select Politician(s)", list(URLS.keys()), default=list(URLS.keys()))

# Fetch and display news
if selected_politicians:
    for person in selected_politicians:
        news_articles = get_news(person)
        if news_articles:
            df = pd.DataFrame(news_articles)
            st.write(f"### 📰 Latest News on {person} ({len(df)} articles)")
            st.write(df.to_html(escape=False), unsafe_allow_html=True)  # Display with clickable links
        else:
            st.warning(f"No recent news found for {person}.")
else:
    st.info("Please select at least one politician to see news.")
