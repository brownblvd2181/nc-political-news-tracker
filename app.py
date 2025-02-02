import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import time
from streamlit_autorefresh import st_autorefresh  # For auto-refresh on the News page

# Define single-source Google News RSS for each politician
URLS = {
    "Alma Adams": "https://news.google.com/rss/search?q=Alma+Adams+North+Carolina",
    "Don Davis": "https://news.google.com/rss/search?q=Don+Davis+North+Carolina",
    "Mayor Vi Lyles": "https://news.google.com/rss/search?q=Mayor+Vi+Lyles+Charlotte",
    "Mayor Karen Bass": "https://news.google.com/rss/search?q=Mayor+Karen+Bass"
}

DEFAULT_IMAGE = "https://via.placeholder.com/150/3498db/ffffff?text=News"  # Default thumbnail

def get_news(person, keyword="", limit=5):
    """
    Fetch the top news articles for the given person from Google News (RSS).
    Uses 'lxml-xml' to avoid bs4.FeatureNotFound.
    """
    feed_url = URLS.get(person)
    if not feed_url:
        return []
    
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        st.warning(f"Error fetching data from {feed_url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "lxml-xml")

    articles = []
    for item in soup.find_all("item")[:limit]:
        title = item.title.text if item.title else "No Title"
        pub_date = item.pubDate.text if item.pubDate else "Unknown Date"

        if keyword and keyword.lower() not in title.lower():
            continue

        articles.append({
            "Title": title,
            "Link": item.link.text if item.link else "",
            "Published": pub_date,
            "Image": DEFAULT_IMAGE
        })
    return articles

def save_email(email):
    """Save an email address to a CSV file for daily newsletter subscriptions."""
    with open("subscribers.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([email])
    return True

# Streamlit page config
st.set_page_config(page_title="NC Political News Tracker", page_icon="🗳️", layout="wide")

# Custom CSS for styling
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

# Page selection: News or Videos
page = st.sidebar.radio("Select Page:", ["News", "Videos"])

if page == "News":
    # Auto-refresh the News page every 60 seconds (up to 100 times)
    st_autorefresh(interval=60000, limit=100, key="news_refresh")

    # Sidebar for News
    st.sidebar.markdown("## 🔍 Filter News")
    selected_politicians = st.sidebar.multiselect(
        "Select Politician(s)", list(URLS.keys()), default=list(URLS.keys())
    )
    keyword = st.sidebar.text_input("Search for a topic (optional):")
    news_limit = st.sidebar.slider("Number of Articles", min_value=1, max_value=15, value=5)

    st.sidebar.markdown("## 📩 Subscribe for Daily News")
    email = st.sidebar.text_input("Enter your email for daily updates")
    if st.sidebar.button("Subscribe"):
        if email:
            save_email(email)
            st.sidebar.success("✅ Subscribed! You’ll receive daily updates.")
        else:
            st.sidebar.warning("⚠️ Please enter a valid email.")

    # Main News Page
    st.title("🗳️ NC Political News Tracker - News")
    st.markdown("""
    #### Get the latest news on North Carolina politics, featuring:
    **Alma Adams**, **Don Davis**, **Mayor Vi Lyles**, and **Mayor Karen Bass**.
    """)

    if selected_politicians:
        for person in selected_politicians:
            news_articles = get_news(person, keyword=keyword, limit=news_limit)
            if news_articles:
                st.markdown(f"## 📰 Latest News on {person}")
                for article in news_articles:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(article["Image"], use_container_width=True)
                    with col2:
                        st.markdown(f"### {article['Title']}")
                        st.markdown(f"🕒 {article['Published']}")
                        if article["Link"]:
                            st.markdown(f"[🔗 Read More]({article['Link']})")
                        else:
                            st.markdown("No link available")
            else:
                st.warning(f"No recent news found for {person}.")
    else:
        st.info("Please select at least one politician to see news.")

elif page == "Videos":
    st.title("🎥 Politician Videos")
    st.markdown("""
    Learn more about the featured politicians through curated videos and brief biographies.
    Replace these example YouTube links with actual relevant interviews or speeches.
    """)

    # Alma Adams
    st.markdown("### Alma Adams")
    st.markdown("Alma Adams is a U.S. Representative for North Carolina's 12th District, focusing on civil rights and education.")
    st.video("https://www.youtube.com/watch?v=jVroqC_OGmo")  # Example relevant link

    # Don Davis
    st.markdown("### Don Davis")
    st.markdown("Don Davis is a U.S. Representative for North Carolina's 1st District, emphasizing community issues and development.")
    st.video("https://www.youtube.com/watch?v=MJBvd1TPbg4")  # Example relevant link

    # Mayor Vi Lyles
    st.markdown("### Mayor Vi Lyles")
    st.markdown("Mayor Vi Lyles leads Charlotte, NC, known for driving innovation and economic growth in the city.")
    st.video("https://www.youtube.com/watch?v=vSYfYzh4rZ8")  # Example relevant link

    # Mayor Karen Bass
    st.markdown("### Mayor Karen Bass")
    st.markdown("Mayor Karen Bass serves Los Angeles, focusing on social justice and public service.")
    st.video("https://www.youtube.com/watch?v=WcOvTx1d05M")  # Example relevant link


