import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time

# Define multiple RSS feeds for each politician
NEWS_SOURCES = {
    "Alma Adams": [
        "https://news.google.com/rss/search?q=Alma+Adams+North+Carolina",
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
        "https://www.politico.com/rss/politics.xml",  # Politico added
        "https://www.charlotteobserver.com/news/politics-government/?widgetName=rssfeed&widgetContentId=71255950"
    ],
    "Don Davis": [
        "https://news.google.com/rss/search?q=Don+Davis+North+Carolina",
        "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml",
        "https://www.politico.com/rss/politics.xml",  # Politico added
        "https://www.wral.com/politics/?rss=1"
    ]
}

DEFAULT_IMAGE = "https://via.placeholder.com/150/3498db/ffffff?text=News"  # Default thumbnail

def fetch_rss_news(feed_urls, keyword="", limit=5):
    """Fetch news articles from multiple RSS feeds with improved timeout handling."""
    articles = []
    for url in feed_urls:
        try:
            response = requests.get(url, timeout=10)  # ✅ Increased timeout to 10 sec
            soup = BeautifulSoup(response.content, "xml")
            
            for item in soup.find_all("item")[:limit]:  # Limit articles per feed
                title = item.title.text
                link = item.link.text
                pub_date = item.pubDate.text if item.pubDate else "Unknown Date"

                # Apply keyword filter
                if keyword and keyword.lower() not in title.lower():
                    continue

                articles.append({
                    "Title": title,
                    "Link": link,
                    "Published": pub_date,
                    "Image": DEFAULT_IMAGE
                })

        except requests.exceptions.Timeout:
            st.warning(f"⚠️ Timeout error fetching data from {url}. Retrying...")
            time.sleep(2)  # ✅ Retry after a short wait
            try:
                response = requests.get(url, timeout=10)  # Second attempt
                soup = BeautifulSoup(response.content, "xml")
                for item in soup.find_all("item")[:limit]:  
                    title = item.title.text
                    link = item.link.text
                    pub_date = item.pubDate.text if item.pubDate else "Unknown Date"

                    if keyword and keyword.lower() not in title.lower():
                        continue

                    articles.append({
                        "Title": title,
                        "Link": link,
                        "Published": pub_date,
                        "Image": DEFAULT_IMAGE
                    })
            except Exception:
                st.error(f"❌ Failed to retrieve data from {url} after retrying.")
        
        except requests.exceptions.RequestException as e:
            st.warning(f"⚠️ Error fetching data from {url}: {e}")

    # Sort articles by published date (if available)
    articles = sorted(articles, key=lambda x: x["Published"], reverse=True)[:limit]
    return articles

# Function to save emails
def save_email(email):
    """Save email to CSV for future newsletters."""
    with open("subscribers.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([email])
    return True

# Streamlit UI Configuration
st.set_page_config(page_title="NC Political News Tracker", page_icon="🗳️", layout="wide")

# Custom CSS for better styling and readability
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        
        body { 
            font-family: 'Inter', sans-serif;
            background-color: #f8f9fa;
        }
        .news-container {
            padding: 15px;
            border-radius: 12px;
            background-color: white;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        .news-title {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        .news-meta {
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 8px;
        }
        .news-link {
            font-size: 16px;
            color: #2980b9;
            font-weight: bold;
            text-decoration: none;
        }
        .news-link:hover {
            text-decoration: underline;
        }
        .sidebar-title {
            font-size: 18px;
            font-weight: bold;
            color: #34495e;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
st.sidebar.markdown("## 🔍 Filter News")
selected_politicians = st.sidebar.multiselect(
    "Select Politician(s)", list(NEWS_SOURCES.keys()), default=list(NEWS_SOURCES.keys())
)
keyword = st.sidebar.text_input("Search for a topic (optional):")
news_limit = st.sidebar.slider("Number of Articles", min_value=1, max_value=15, value=5)

# Email Subscription Section
st.sidebar.markdown("## 📩 Subscribe for Daily News")
email = st.sidebar.text_input("Enter your email for daily updates")
if st.sidebar.button("Subscribe"):
    if email:
        save_email(email)
        st.sidebar.success("✅ Subscribed! You’ll receive daily updates.")
    else:
        st.sidebar.warning("⚠️ Please enter a valid email.")

# Main Page Title
st.title("🗳️ NC Political News Tracker")
st.markdown("#### Get the latest news on North Carolina politics, featuring **Alma Adams** and **Don Davis**.")

# Display News in Sections
if selected_politicians:
    for person in selected_politicians:
        news_articles = fetch_rss_news(NEWS_SOURCES[person], keyword=keyword, limit=news_limit)
        
        if news_articles:
            st.markdown(f"## 📰 Latest News on {person}")
            
            for article in news_articles:
                col1, col2 = st.columns([1, 3])  # Image on left, text on right
                with col1:
                    st.image(article["Image"], use_container_width=True)
                with col2:
                    st.markdown(f"### {article['Title']}")
                    st.markdown(f"🕒 {article['Published']}")
                    st.markdown(f"[🔗 Read More]({article['Link']})")
        else:
            st.warning(f"No recent news found for {person}.")
else:
    st.info("Please select at least one politician to see news.")

