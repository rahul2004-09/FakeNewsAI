import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

fake = pd.read_csv("dataset/Fake.csv")
real = pd.read_csv("dataset/True.csv")

fake["label"] = 0
real["label"] = 1

# combine and shuffle dataset
data = pd.concat([fake, real]).sample(frac=1).reset_index(drop=True)

print("Dataset size:", data.shape)

X = data["text"]
y = data["label"]

vectorizer = TfidfVectorizer(stop_words="english", max_df=0.7)

X_vector = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_vector, y, test_size=0.2, random_state=42
)

model = LogisticRegression(max_iter=1000)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("Model Accuracy:", accuracy)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model trained successfully!")