import requests

# 🔑 Your NewsData API Key
NEWSDATA_API_KEY = "pub_d9b6e9818b164ba5b0ed591f12638718"


# =========================
# GDELT SEARCH
# =========================
def search_gdelt(query):
    url = "https://api.gdeltproject.org/api/v2/doc/doc"

    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": 5,
        "format": "json",
        "sort": "HybridRel",
        "timespan": "1d"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])

        return [
            {
                "title": a.get("title"),
                "description": a.get("seendate"),
                "url": a.get("url")
            }
            for a in articles
        ]

    except Exception as e:
        print("GDELT Error:", e)
        return []


# =========================
# NEWSDATA API SEARCH
# =========================
def search_newsdata(query):
    url = "https://newsdata.io/api/1/latest"

    params = {
        "apikey": NEWSDATA_API_KEY,
        "q": query,
        "language": "en"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        articles = data.get("results", [])

        return [
            {
                "title": a.get("title"),
                "description": a.get("description"),
                "url": a.get("link")
            }
            for a in articles
        ]

    except Exception as e:
        print("NewsData Error:", e)
        return []


# =========================
# MAIN FUNCTION (HYBRID)
# =========================
def search_news(query):

    gdelt_results = search_gdelt(query)
    newsdata_results = search_newsdata(query)

    # 🔥 Merge results
    all_articles = gdelt_results + newsdata_results

    # 🔥 Remove duplicates
    seen = set()
    unique_articles = []

    for article in all_articles:
        title = article.get("title")

        if title and title not in seen:
            seen.add(title)
            unique_articles.append(article)

    return unique_articles[:5]