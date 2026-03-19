import requests

API_KEY = "your_serpapi_key_here"

def google_search(query):
    url = "https://serpapi.com/search.json"

    params = {
        "q": query,
        "api_key": API_KEY,
        "engine": "google",
        "num": 5
    }

    response = requests.get(url, params=params)
    data = response.json()

    articles = []

    if "organic_results" in data:
        for item in data["organic_results"][:5]:
            articles.append({
                "title": item.get("title"),
                "description": item.get("snippet"),
                "url": item.get("link")
            })

    return articles