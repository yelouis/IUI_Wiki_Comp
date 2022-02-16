import stopwords as sw

# Revisions is expected to be an array of revision texts where the 0th entry is the oldest revision
# and the nth entry is the latest revision


def create_doc_word_mtx(revisions):
    unique_words = []
    processed_revisions = []
    doc_word_mtx = []
    # Generate unique wordlist
    for revision in revisions:
        processed_revision = sw.remove_stopwords(revision)
        processed_revisions.append(processed_revision)
        for word in processed_revision:
            if word not in unique_words:
                unique_words.append(word)

    # Initialize doc_word to 0
    for i in len(processed_revisions):
        for j in len(unique_words):
            doc_word_mtx[i][j] = 0

    doc_counter = 0
    for processed_revision in processed_revisions:
        word_counter = 0
        for unique in unique_words:
            for word in processed_revision:
                if word == unique:
                    doc_word_mtx[doc_counter][word_counter] += 1
            word_counter += 1

    return doc_word_mtx


# Calculate the difference between two document rows
def calculate_adjacent_score(doc1, doc2):
    total_diff = 0
    for i in len(doc1):
        total_diff += abs(doc1[i] - doc2[i])

    return total_diff


# Calculate the total differential from n to the first revision using theta to weight time
def calculate_score_from_nth(doc_word_mtx, theta, n):
    if n == 1:
        first = doc_word_mtx[0]
        curr = doc_word_mtx[1]
        return calculate_adjacent_score(first, curr) * theta
    else:
        current_revision = doc_word_mtx[n]
        next_revision = doc_word_mtx[n-1]
        new_score = calculate_adjacent_score(
            current_revision, next_revision) * theta
        return new_score + calculate_score_from_nth(doc_word_mtx, theta * theta, n-1)


def find_largest_change(doc_word_mtx):
    curr = len(doc_word_mtx)-1
    next = curr-1
    max = 0
    greatest_change = None
    while next != 0:
        curr_revision = doc_word_mtx[curr]
        next_revision = doc_word_mtx[next]
        differential = calculate_adjacent_score(curr_revision, next_revision)
        if differential > max:
            max = differential
            greatest_change = (curr, next)
        curr -= 1
        next -= 1
    return greatest_change
