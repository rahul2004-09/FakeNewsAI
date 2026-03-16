from services.news_fetcher import search_news

query = "Iran war"

articles = search_news(query)

print("\nLatest News Results:\n")

for article in articles:
    print("Title:", article["title"])
    print("Description:", article["description"])
    print("Link:", article["url"])
    print("-" * 60)