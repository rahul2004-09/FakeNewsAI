import requests
from bs4 import BeautifulSoup

def search_news(query):

    url = f"https://news.google.com/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    articles = []

    for item in soup.select("article")[:5]:
        title = item.text
        link = "https://news.google.com" + item.find("a")["href"][1:]

        articles.append({
            "title": title,
            "description": "Google News result",
            "url": link
        })

    return articles