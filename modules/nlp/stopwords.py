from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


#word_tokens = word_tokenize(example_sent)

# filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]

# filtered_sentence = []

# for w in word_tokens:
#     if w not in stop_words:
#         filtered_sentence.append(w)

def remove_stopwords(text):
    filtered = []
    stop_words = set(stopwords.words('english'))
    for word in text:
        lower_word = word.lower()
        if lower_word not in stop_words:
            filtered.append(lower_word)
