import requests

# Your NewsAPI key
API_KEY = "045e447cd58147ed9d2ff2dfb628f8e0"

def search_news(query):

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 5,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data["status"] != "ok":
            print("Error fetching news:", data)
            return []

        articles = data["articles"]

        results = []

        for article in articles:
            results.append({
                "title": article["title"],
                "description": article["description"],
                "url": article["url"]
            })

        return results

    except Exception as e:
        print("Error:", e)
        return []