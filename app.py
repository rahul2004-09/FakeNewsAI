import streamlit as st
import pickle

# Load trained model
model = pickle.load(open("model/model.pkl","rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl","rb"))

st.title("Fake News Detection AI")

st.write("Paste a news article below to check if it is real or fake.")

news = st.text_area("Enter News Article")

if st.button("Check News"):
    
    news_vector = vectorizer.transform([news])
    prediction = model.predict(news_vector)

    if prediction[0] == 0:
        st.error("This news is FAKE")
    else:
        st.success("This news is REAL")