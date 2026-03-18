import streamlit as st
import pickle
import re

# Import services
from services.claim_extractor import extract_claim
from services.news_fetcher import search_news
from services.similarity_checker import check_similarity

# ================================
# Smart Keyword Extraction (NO spaCy)
# ================================
def extract_keywords(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    words = text.split()

    stopwords = {
        "is","are","was","were","the","a","an","and","or",
        "to","of","in","on","at","after","due","have","has",
        "had","will","been","this","that","with","from","by"
    }

    keywords = [w for w in words if w not in stopwords]

    # keep meaningful words (length filter helps)
    keywords = [w for w in keywords if len(w) > 3]

    return " ".join(keywords[:6])


# ================================
# Multi Query Builder
# ================================
def build_search_queries(text):
    base = extract_keywords(text)

    queries = [
        base,
        base + " news",
        base + " latest",
        " ".join(base.split()[:3]),  # shorter query
        text[:60]  # fallback full sentence
    ]

    return list(set(queries))  # remove duplicates


# Load ML model
model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

# ================================
# UI
# ================================
st.set_page_config(page_title="Fake News Detection AI", layout="centered")

st.title("📰 Fake News Detection & Fact-Checking AI")
st.write("Paste a news article to verify it using real-time sources + AI model.")

news = st.text_area("Enter News Article")

# ================================
# MAIN LOGIC
# ================================
if st.button("Analyze News"):

    if news.strip() == "":
        st.warning("Please enter some text.")
    
    else:
        try:
            # ================================
            # Step 1 — Extract Claim
            # ================================
            claim = extract_claim(news)

            st.subheader("🧠 Extracted Claim")
            st.info(claim)

            # ================================
            # Step 2 — Search News
            # ================================
            st.subheader("🌍 Real News Analysis (Primary)")

            queries = build_search_queries(claim)

            all_articles = []

            for q in queries:
                st.write(f"🔎 Trying Query: {q}")
                results = search_news(q)
                all_articles.extend(results)

            # Remove duplicates
            unique_articles = {a["url"]: a for a in all_articles if a.get("url")}
            articles = list(unique_articles.values())[:5]

            if len(articles) == 0:
                st.warning("⚠️ No reliable sources found.")
                st.info("This may be breaking news or not widely reported yet.")

            else:
                # ================================
                # Step 3 — Similarity Analysis
                # ================================
                scores = check_similarity(claim, articles)

                # Filter irrelevant articles
                filtered_articles = []
                filtered_scores = []

                for article, score in zip(articles, scores):
                    if score > 0.2:
                        filtered_articles.append(article)
                        filtered_scores.append(score)

                articles = filtered_articles
                scores = filtered_scores

                if len(articles) == 0:
                    st.warning("⚠️ No relevant news found.")
                    st.info("The claim may be unverified or not widely reported.")

                else:
                    # Show Articles
                    for article in articles:
                        st.write("### 📰", article["title"])
                        st.write(article["description"])
                        st.markdown(f"[Read Full Article]({article['url']})")
                        st.write("---")

                    st.subheader("🔍 Similarity Scores")

                    for i, score in enumerate(scores):
                        st.write(f"Article {i+1}: {round(score, 2)}")

                    avg_score = sum(scores) / len(scores)

                    st.info(f"📈 Average Similarity Score: {round(avg_score, 2)}")

                    # ================================
                    # Step 4 — Final Verdict
                    # ================================
                    st.subheader("📊 Final Fact-Check Result")

                    if avg_score > 0.4:
                        st.success(f"✅ VERIFIED REAL (Confidence: {round(avg_score*100,2)}%)")
                        st.info("Supported by multiple trusted news sources.")

                    elif avg_score > 0.2:
                        st.warning(f"⚠️ PARTIALLY VERIFIED (Confidence: {round(avg_score*100,2)}%)")
                        st.info("Some sources match but not strongly confirmed.")

                    else:
                        st.warning("⚠️ UNVERIFIED CLAIM")
                        st.info("No strong supporting evidence found.")

            # ================================
            # Step 5 — ML Model (Secondary)
            # ================================
            st.subheader("🤖 AI Model Opinion (Secondary)")

            news_vector = vectorizer.transform([news])
            prediction = model.predict(news_vector)
            probability = model.predict_proba(news_vector)

            confidence = max(probability[0]) * 100

            if prediction[0] == 0:
                st.error(f"Model Prediction: FAKE ({confidence:.2f}%)")
            else:
                st.success(f"Model Prediction: REAL ({confidence:.2f}%)")

        except Exception as e:
            st.error(f"Error occurred: {e}")