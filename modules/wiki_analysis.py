from __future__ import annotations
from typing import Optional
from datetime import date

import wiki_req as wr


class WikipediaArticle:
    id: int = -1
    title: str = "N/A"
    current_id: int = -1 
    parent_id: int = -1  # parent id
    ns: int = -1   # namespace
    revisions: dict[int, WikipediaRevision]
    notext: int = 0 # number of revisions with no text

    def __init__(self, id: int = None):
        self.revisions = {}
        if id is not None:
            self.id = id
            rvs, self.current_id, self.parent_id = wr.get_article_properties(self.id)

            for rv in rvs:
                self.revisions[rv] = WikipediaRevision(self, rv)

    def __repr__(self):
        return f"Article(id={self.id}, title={self.title}, num_revisions={len(self.revisions)}, num_notext={self.notext})"

    def __str__(self):
        return f"{self.id}, {self.title}, {self.current_id}, {self.parent_id}, {len(self.revisions)}, {self.notext},\n"

    def get_current_revision(self) -> Optional[WikipediaRevision]:
        current_revision = self.revisions.get(self.current_id)
        if current_revision:
            return current_revision
        return None

    def get_parent_revision(self) -> Optional[WikipediaRevision]:
        parent_revision = self.revisions.get(self.parent_id)
        if parent_revision:
            return parent_revision
        return None


class WikipediaRevision:
    id: int = -1
    date: date = date(1970, 1, 1)
    scores: dict[str, float]
    author_name: str = "N/A"
    author_id: int = -1
    text: str = "N/A"

    def __init__(self, article: WikipediaArticle = None, id: int = None):
        self.scores = {}
        if article is not None and id is not None:
            self.article = article
            self.id = id
            self.date = wr.get_revision_date(id, self.article.id)

    def __str__(self):
        # TODO: Add self.text to the end, add all the scores to the end
        return f"{self.id}, {self.date}, {self.author_name}, {self.author_id},\n"

    def get_score(self, score_name: str) -> Optional[float]:
        score = self.scores.get(score_name)
        if score:
            return score
        return None

    def author_metrics(self, id):
        # get num unique editors, how diverse they are and admin proportions
        pass

    def internal_links(self, id):
        # Gets number of internal links article has
        pass

    def external_links(self, id):
        # Gets number of external links article has
        pass

    def article_age(self, id):
        # get article age and currency
        pass

    def ASL(self, text):
        # Average sentence length computation (NOT DONE)
        numSentences = 0
        for item in text:
            if item == "." or item == "?" or item == "!":
                numSentences += 1
        pass

    def flesch_read(self, text):
        # Computes flesch readability for the article
        # not sure if take in text or the id
        avgSentenceLength = self.ASL(text)
        pass