import streamlit as st
import pickle
import re

# Import services
from services.claim_extractor import extract_claim
from services.news_fetcher import search_news
from services.similarity_checker import check_similarity

# ================================
# Smart Query Builder (FIXED)
# ================================
def build_search_query(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)

    words = text.split()

    stopwords = {
        "is","are","was","were","the","a","an",
        "and","or","to","of","in","on","at","after",
        "due","have","has","had","will","been"
    }

    keywords = [w for w in words if w not in stopwords]

    important = []
    important_words = [
        "india","lpg","protest","shortage","fuel",
        "airport","drone","war","price"
    ]

    for word in keywords:
        if word in important_words:
            important.append(word)

    if not important:
        important = keywords[:4]

    return " ".join(important) + " news"


# Load model
model = pickle.load(open("model/model.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

# UI
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
            # Step 1 — Extract Claim
            claim = extract_claim(news)

            st.subheader("🧠 Extracted Claim")
            st.info(claim)

            # Step 2 — Build Query + Fetch News
            st.subheader("🌍 Real News Analysis (Primary)")

            query = build_search_query(claim)
            st.write(f"🔎 Search Query Used: {query}")

            articles = search_news(query)

            if len(articles) == 0:
                st.warning("⚠️ No strong evidence found from news sources.")
                st.info("This may be a new or developing story.")

            else:
                # Show Articles
                for article in articles:
                    st.write("### 📰", article["title"])
                    st.write(article["description"])
                    st.markdown(f"[Read Full Article]({article['url']})")
                    st.write("---")

                # Step 3 — Similarity
                scores = check_similarity(claim, articles)

                st.subheader("🔍 Similarity Scores")

                for i, score in enumerate(scores):
                    st.write(f"Article {i+1}: {round(score, 2)}")

                avg_score = sum(scores) / len(scores)

                st.write(f"📈 Average Similarity Score: {round(avg_score, 2)}")

                # Step 4 — Final Verdict (PRIMARY)
                st.subheader("📊 Final Fact-Check Result")

                if avg_score > 0.4:
                    st.success(f"✅ VERIFIED REAL (Confidence: {round(avg_score*100,2)}%)")
                    st.info("Supported by multiple trusted news sources.")
                elif avg_score > 0.2:
                    st.warning(f"⚠️ PARTIALLY VERIFIED (Confidence: {round(avg_score*100,2)}%)")
                    st.info("Some sources match but not strongly confirmed.")
                else:
                    st.error(f"❌ NOT VERIFIED (Confidence: {round((1-avg_score)*100,2)}%)")
                    st.info("No strong supporting evidence found.")

            # Step 5 — AI Model (SECONDARY)
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