from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
#import textstat
import wiki_req as wr


class WikipediaArticle:
    pageid: int
    title: str = ""
    current_id: int = -1 
    parent_id: int = -1  # parent id
    ns: int = -1   # namespace
    revisions: dict[int, WikipediaRevision] = {}

    def __init__(self, pageid: int = None):
        if pageid is not None:
            self.pageid = pageid
            rvs, self.current_id, self.parent_id = wr.get_article_properties(self.pageid)

            for rv in rvs:
                self.revisions[rv] = WikipediaRevision(self, rv)

    def get_current_revision(self) -> WikipediaRevision:
        current_revision = self.revisions.get(self.current_id)
        if current_revision:
            return current_revision
        return None

    def get_parent_revision(self) -> WikipediaRevision:
        parent_revision = self.revisions.get(self.parent_id)
        if parent_revision:
            return parent_revision
        return None


class WikipediaRevision:
    article: WikipediaArticle
    id: int
    date: date = date(1970, 1, 1)
    scores: dict[str, float] = {}
    author_name: str = ""
    author_id: int = -1
    text: str = ""

    def __init__(self, article: WikipediaArticle = None, id: int = None):
        if article is not None:
            self.article = article
            self.id = id
            self.date = wr.get_revision_date(id, self.article.pageid)

    def get_score(self, score_name: str) -> float:
        score = self.sections.get(score_name)
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