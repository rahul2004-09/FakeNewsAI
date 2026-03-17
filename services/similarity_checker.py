from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def check_similarity(claim, articles):

    if not articles:
        return []

    texts = []

    for article in articles:
        content = (article["title"] or "") + " " + (article["description"] or "")
        texts.append(content)

    # Convert to embeddings
    claim_embedding = model.encode([claim])
    article_embeddings = model.encode(texts)

    # Compute similarity
    similarities = cosine_similarity(claim_embedding, article_embeddings)

    return similarities[0]