from collections import Counter
from statistics import mean
import psycopg2
import wiki_db as wdb

with open("../stopwords/english.txt") as f:
    stopWords = f.read().splitlines()

with open("../words/en.txt") as f:
    wordsList = f.read().splitlines()


class QuoteScore:
    def __init__(self, text):
        self.corpus = text
        self.inQuote = []
        self.nonQuote = []
        self.frequencyDict = {}
        self.dataCleaning()

    def dataCleaning(self):
        self.removePunctuationNum()
        self.quoteDetection()
        self.quoteCleaning()

    def quoteCleaning(self):
        newInQuote = []
        for word_ele in self.inQuote:
            # Remove words that are stopwords, is a proper noun (by cap), or not in the wordList of NLTK
            if (
                word_ele.lower() in stopWords
                or len(word_ele) == 0
                or word_ele[0].isupper()
                or word_ele.lower() not in wordsList
            ):
                continue
            else:
                newInQuote.append(word_ele.lower())
        self.inQuote = newInQuote

        newNonQuote = []
        for word_ele in self.nonQuote:
            # print(word_ele)
            if (
                word_ele.lower() in stopWords
                or len(word_ele) == 0
                or word_ele[0].isupper()
                or word_ele.lower() not in wordsList
            ):
                continue
            else:
                newNonQuote.append(word_ele.lower())
        self.nonQuote = newNonQuote

    def removePunctuationNum(self):
        punc = """!()-[]{};:\,<>./?@#$%^&*_~"""
        for character in self.corpus:
            if character in punc:
                self.corpus = self.corpus.replace(character, "")
            if ord(character) >= 128:
                self.corpus = self.corpus.replace(character, "")

        for i in range(9):
            self.corpus = self.corpus.replace(str(i), "")

    def quoteDetection(self):
        quotationMark = "\"'"
        all_words = self.corpus.split(" ")
        quoteStack = []
        openQuote = False
        for word in all_words:
            if "'" not in word and '"' not in word:
                if openQuote:
                    quoteStack.append(word)
                else:
                    self.nonQuote.append(word)
            # If the quotation is in first letter of a word, open quotes
            # if the quotation is the last letter of word, close quote
            else:
                # Open Quote
                if word[0] in quotationMark:
                    stripped_word = word.replace('"', "")
                    stripped_word = stripped_word.replace("'", "")
                    if not openQuote:
                        openQuote = True
                    # If we have already seen an open quote before, everything in stack is nonQuote
                    elif openQuote:
                        self.nonQuote.extend(quoteStack)
                    quoteStack = []
                    if len(stripped_word) > 0:
                        quoteStack.append(stripped_word)
                # Close quotes
                if word[-1] in quotationMark:
                    stripped_word = word.replace('"', "")
                    stripped_word = stripped_word.replace("'", "")
                    if openQuote:
                        if len(stripped_word) > 0 and quoteStack[-1] != stripped_word:
                            quoteStack.append(stripped_word)
                        self.inQuote.extend(quoteStack)
                        quoteStack = []
                        openQuote = False
                    elif not openQuote:
                        if len(stripped_word) > 0:
                            self.nonQuote.append(stripped_word)
                # If there is a random quotation in the middle of string
                if word[-1] not in quotationMark and word[0] not in quotationMark:
                    stripped_word = word.replace('"', "")
                    stripped_word = stripped_word.replace("'", "")
                    if openQuote:
                        quoteStack.append(stripped_word)
                    if not openQuote:
                        self.nonQuote.append(stripped_word)

    def quoteScore(self):
        # print(self.inQuote)
        # print(self.nonQuote)
        frequencyDict = Counter(self.inQuote + self.nonQuote)
        frequencyDictInQuote = Counter(self.inQuote)
        frequencyDictNonQuote = Counter(self.nonQuote)
        newFrequencyDict = {}
        for word in frequencyDict:
            if frequencyDict[word] >= 2:
                newFrequencyDict[word] = frequencyDict[word]
        frequencyDict = newFrequencyDict
        inQuoteAverageScoreList = []
        nonQuoteAverageScoreList = []

        for quoteWord in frequencyDict:
            if quoteWord in frequencyDictInQuote:
                inQuoteAverageScoreList.append(frequencyDictInQuote[quoteWord]/frequencyDict[quoteWord])
            if quoteWord in frequencyDictNonQuote:
                nonQuoteAverageScoreList.append(frequencyDictNonQuote[quoteWord]/frequencyDict[quoteWord])

        inQuoteAverage = 0
        nonQuoteAverage = 0

        if len(inQuoteAverageScoreList) > 0:
            inQuoteAverage = mean(inQuoteAverageScoreList)
        if len(nonQuoteAverageScoreList) > 0:
            nonQuoteAverage = mean(nonQuoteAverageScoreList)

        return (inQuoteAverage, nonQuoteAverage)


testing = wdb.DatabaseAccess()
# query = f"""select text from "revisionHistory" where article_id = 1;"""
query = f"""select distinct(id) from "article" limit 5;"""

row = testing.freeDatabaseAccess(query)
print(row)
# newQuote = QuoteScore(row[0][0])
# print(newQuote.quoteScore())

#select distinct(id) from "article" limit 5;

# newQuote = QuoteScore("""positive number, the number of documents to select; when used with by, the number to select from each group or a vector equal in length to the number of groups defining the samples to be chosen in each category of by. By defining a size larger than the number of documents, it is possible to oversample when""")
# print(newQuote.quoteScore())


# print(newQuote.quoteScore())
