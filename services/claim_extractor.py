import re

def extract_claim(text):
    # remove extra spaces
    text = text.strip()

    # split article into sentences
    sentences = re.split(r'[.!?]', text)

    # return the first meaningful sentence
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) > 20:
            return sentence

    return sentences[0]