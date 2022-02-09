import psycopg2

with open("../stopwords/english.txt") as f:
    stopWords = f.read().splitlines()

with open("../words/en.txt") as f:
    wordsList = f.read().splitlines()


class QuoteScore:
    def __init__(self, text):
        self.corpus = text
        self.inQuote = []
        self.nonQuote = []

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
                or word_ele[0].isupper()
                or word_ele.lower() not in wordsList
            ):
                continue
            else:
                newInQuote.append(word_ele.lower())
        self.inQuote = newInQuote

        newNonQuote = []
        for word_ele in self.nonQuote:
            if (
                word_ele.lower() in stopWords
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


newQuote = QuoteScore(
    "[I]n corpus linguistics quantitative and qualitative methods are extensively used in combination. It is also characteristic of corpus linguistics to begin with quantitative findings, and work toward qualitative ones. But...the procedure may have cyclic elements. Generally it is desirable to subject quantitative results to qualitative scrutiny—attempting to explain why a particular frequency pattern occurs, for example. But on the other hand, qualitative analysis (making use of the investigator's ability to interpret samples of language in context) may be the means for classifying examples in a particular corpus by their meanings; and this qualitative analysis may then be the input to a further quantitative analysis, one based on meaning...."
)
newQuote.dataCleaning()
print(newQuote.inQuote)
print(newQuote.nonQuote)
