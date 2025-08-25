"""
This is a  script to fetch news articles from NewsAPI based on user configured relevant and irrelevant topics (stored in config.json), summarise them and send them to a Telegram bot.
"""

import requests

NEWS_API_KEY = 'your_news_api_key' # move to config later

def fetch_news(topics_include, topics_exclude):
    url = f'https://newsapi.org/v2/everything?q={" OR ".join(topics_include)}&excludeDomains={" OR ".join(topics_exclude)}&apiKey={NEWS_API_KEY}'
    response = requests.get(url)
    data = response.json().get('articles', [])
    return data.get('articles', [])
