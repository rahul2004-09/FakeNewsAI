import streamlit as st
import pickle
import re
import requests

# Import services
from services.claim_extractor import extract_claim
from services.similarity_checker import check_similarity

# ================================
# 🔥 SERP API CONFIG (GOOGLE SEARCH)
# ================================
API_KEY = "b8a51003cf6cc1690d87b32db8e2f6d98d32184b838c5e058ba7b21ab8094a80"

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


# ================================
# Source Detection
# ================================
def get_source(url):
    url = url.lower()

    if "reuters" in url:
        return "Reuters (High Trust)"
    elif "bbc" in url:
        return "BBC (High Trust)"
    elif "ndtv" in url:
        return "NDTV (Medium Trust)"
    elif "cnn" in url:
        return "CNN (High Trust)"
    else:
        return "Unknown Source"


# ================================
# 🔥 SIMPLE QUERY BUILDER (FIXED)
# ================================
def build_search_queries(text):
    text = text.lower()
    clean_text = re.sub(r"[^\w\s]", "", text)

    words = clean_text.split()

    simple_query = " ".join(words[:2])  # 🔥 KEY FIX

    queries = [
        simple_query,
        simple_query + " news",
        clean_text,
        clean_text + " news",
    ]

    return list(set(queries))


# ================================
# Reasoning
# ================================
def generate_reasoning(claim, articles, avg_score):

    if len(articles) == 0:
        return "⚠️ No strong evidence found. Try using a more detailed sentence."

    if avg_score < 0.2:
        return "⚠️ Articles are not closely related to the claim."

    if avg_score < 0.4:
        return "⚠️ Some related information found, but not strongly confirmed."

    return "✅ Multiple sources support this claim."


# Load ML model
model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))


# ================================
# UI
# ================================
st.set_page_config(page_title="Fake News Detection AI", layout="centered")

st.title("📰 Fake News Detection & Fact-Checking AI")
st.write("Now powered by Google Search + AI")

news = st.text_area("Enter News Article")


# ================================
# MAIN LOGIC
# ================================
if st.button("Analyze News"):

    if news.strip() == "":
        st.warning("Please enter some text.")
    
    else:
        try:
            claim = extract_claim(news)

            st.subheader("🧠 Extracted Claim")
            st.info(claim)

            st.subheader("🌍 Real News Analysis (Google Powered)")

            queries = build_search_queries(claim)

            all_articles = []

            for q in queries:
                st.write(f"🔎 Searching: {q}")
                results = google_search(q)

                # 🔥 DEBUG (IMPORTANT)
                st.write(f"Results found: {len(results)}")

                all_articles.extend(results)

            # Remove duplicates
            unique_articles = {a["url"]: a for a in all_articles if a.get("url")}
            articles = list(unique_articles.values())[:5]

            if len(articles) == 0:
                avg_score = 0
                st.warning("⚠️ No results found. Try a different sentence.")

            else:
                scores = check_similarity(claim, articles)

                # 🔥 RELAXED FILTERING
                filtered_articles = []
                filtered_scores = []

                for article, score in zip(articles, scores):
                    if score > 0.15:
                        filtered_articles.append(article)
                        filtered_scores.append(score)

                articles = filtered_articles
                scores = filtered_scores

                if len(articles) == 0:
                    avg_score = 0
                    st.warning("⚠️ No relevant matches after filtering.")

                else:
                    best_idx = scores.index(max(scores))
                    best_article = articles[best_idx]

                    st.subheader("🏆 Top Matching Article")
                    st.write(best_article["title"])
                    st.write(f"📊 Similarity: {round(scores[best_idx],2)}")
                    st.write(f"📰 Source: {get_source(best_article['url'])}")
                    st.markdown(f"[Read Article]({best_article['url']})")

                    st.write("---")

                    st.subheader("📰 Related Articles")

                    for article in articles:
                        st.write("###", article["title"])
                        st.write(article["description"])
                        st.write(f"📰 Source: {get_source(article['url'])}")
                        st.markdown(f"[Read Full Article]({article['url']})")
                        st.write("---")

                    avg_score = sum(scores) / len(scores)

                    st.info(f"📈 Average Similarity Score: {round(avg_score, 2)}")

                    st.subheader("📊 Final Fact-Check Result")

                    if avg_score > 0.4:
                        st.success("✅ VERIFIED REAL")
                    elif avg_score > 0.2:
                        st.warning("⚠️ PARTIALLY VERIFIED")
                    else:
                        st.warning("⚠️ UNVERIFIED CLAIM")

            # Explanation
            reason = generate_reasoning(claim, articles, avg_score)

            st.subheader("🧠 Explanation")
            st.info(reason)

            # 🔥 FIX ML MODEL
            st.subheader("🤖 AI Model Opinion")

            if len(news.split()) < 8:
                st.warning("⚠️ Input too short for ML model.")
            else:
                news_vector = vectorizer.transform([news])
                prediction = model.predict(news_vector)
                probability = model.predict_proba(news_vector)

                confidence = max(probability[0]) * 100

                if prediction[0] == 0:
                    st.error(f"FAKE ({confidence:.2f}%)")
                else:
                    st.success(f"REAL ({confidence:.2f}%)")

        except Exception as e:
            st.error(f"Error occurred: {e}")