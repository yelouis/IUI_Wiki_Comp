import psycopg2


class QuoteScore:

    def __init__(self, text):
        self.corpus = text
        self.inQuote = []
        self.nonQuote = []



    # def dataCleaning(self):
    #     self.removePunctuation()
    #
    #
    #     self.removeNumber()
    #     self.removeProperNouns()
    #     self.removeStopWords()
    #     self.validateWithNLTK()

    def removePunctuation(self):
        punc = '''!()-[]{};:\,<>./?@#$%^&*_~'''
        for character in self.corpus:
            if character in punc:
                self.corpus = self.corpus.replace(character, "")

    def quoteDetection(self):
        quotationMark = "\"\'"
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

newQuote = QuoteScore("Hi my name is 'Louis asdfa'sdf sad$%^'gasdf'!")
newQuote.removePunctuation()
newQuote.quoteDetection()
print(newQuote.inQuote)
print(newQuote.nonQuote)
