from services.news_fetcher import search_news

query = "Iran war"

print("Searching news for:", query)

articles = search_news(query)

print("Number of articles found:", len(articles))

for article in articles:
    print("\nTitle:", article["title"])
    print("Description:", article["description"])
    print("Link:", article["url"])
    print("-" * 60)