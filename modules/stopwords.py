from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Removes stopwords from text and stems words into their root counterparts
# For example - The quick brown fox jumped over the laziest dog
#Becomes: ["quick", "brown", "fox", "jump", "over", "lazy", "dog"]


def remove_stopwords(text):
    ps = PorterStemmer()
    filtered = []
    stop_words = set(stopwords.words('english'))
    for word in text.split():
        lower_word = word.lower()
        lower_word = ps.stem(lower_word)
        if lower_word not in stop_words:
            filtered.append(lower_word)
    return filtered
