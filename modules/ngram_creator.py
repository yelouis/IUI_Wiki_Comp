class ngram_creator:

    # Work through tokens to create ngrams of a certain order
    def create(self, order, transitions):
        frequencyDict = {}
        key = ""
        counter = 0
        a = 0
        for word in self.tokenList:
            # Generating initial key in this if statement
            if counter < self.order:
                if counter < self.order:
                    counter += 1
                    if counter != self.order:
                        key = key + word + " "
                    else:
                        key = key + word

            # Now that we have a key, we check it against the next word
            else:
                totalNumWords = 0
                # Check if this is a new key
                if key in self.transitions.keys():
                    tupleList = self.transitions.get(key)
                else:
                    tempTranList = [(word, (0.0, 1.0))]
                    self.transitions[key] = tempTranList
                    tupleList = self.transitions.get(key)

                # Check if the key is in frequencyDict
                if key in frequencyDict.keys():
                    frequencyList = frequencyDict.get(key)
                    found = 0
                    totalNumWords = 0
                    # Find the word in frequencyDict and add 1 to frequency
                    for i in range(len(frequencyList)):
                        if frequencyList[i][0] == word:
                            newTuple = (word, frequencyList[i][1] + 1)
                            frequencyList[i] = newTuple
                            found = 1
                        # Keep track of the total frequency
                        totalNumWords += frequencyList[i][1]
                    # If word is not in frequencyDict then add it
                    if found == 0:
                        frequencyList.append((word, 1))
                        totalNumWords += 1
                else:
                    totalNumWords = 1
                    tempFreqList = [(word, 1)]
                    frequencyDict[key] = tempFreqList
                    frequencyList = frequencyDict.get(key)

                # Calculate the weight of 1 frequency
                fracPerWord = 1 / totalNumWords

                tupleCounter = 0
                start = 0.0
                end = 0.0

                # for each tuple in frequency list, assign a start and end value based on their frequency
                if len(frequencyList) == len(tupleList):
                    for tuple in frequencyList:
                        end += tuple[1] * fracPerWord
                        probTuple = (start, end)
                        newTuple = (tuple[0], probTuple)
                        tupleList[tupleCounter] = newTuple
                        start = end
                        tupleCounter += 1
                else:
                    for j in range(len(tupleList)):
                        end += frequencyList[j][1] * fracPerWord
                        probTuple = (start, end)
                        newTuple = (frequencyList[j][0], probTuple)
                        tupleList[tupleCounter] = newTuple
                        tupleCounter += 1
                        start = end
                    end += frequencyList[-1][1] * fracPerWord
                    probTuple = (start, end)
                    newTuple = (word, probTuple)
                    tupleList.append(newTuple)

                self.transitions[key] = tupleList

                # Remove the first word from the key and add the word we just checked
                if self.order != 1:
                    keySplit = key.split(" ")
                    keySplit.pop(0)
                    key = " ".join(keySplit) + " " + word
                else:
                    key = key[1:] + word

    # Tokenizes the input corpus
    def tokenize(self, corpus):
        for line in corpus:
            for word in line.split():
                self.tokenList.append(word)

    def __init__(self, corpus, order):
        self.order = order
        self.transitions = {}
        self.corpus = open(corpus, "r")
        self.tokenList = []
        self.tokenize(self.corpus)
