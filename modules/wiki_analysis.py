from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
#import textstat
import wikireq as wr


class WikipediaArticle:
    article_id: int
    name: str = ""
    url: str = ""
    cid: int = -1  # current id
    pid: int = -1  # parent id
    revisions: dict[int, WikipediaRevision] = {}

    def __init__(self, article_id: int):
        self.article_id = article_id
        rvs, self.cid, self.pid = wr.get_article_properties(self.article_id)

        for rv in rvs:
            self.revisions[rv] = WikipediaRevision(self, rv)

    def get_current_revision(self) -> WikipediaRevision:
        current_revision = self.revisions.get(self.current_revision_id)
        if current_revision:
            return current_revision
        return None

    def get_parent_revision(self) -> WikipediaRevision:
        parent_revision = self.revisions.get(self.parent_revision_id)
        if parent_revision:
            return parent_revision
        return None


class WikipediaRevision:
    article: WikipediaArticle
    revision_id: int
    date: date = date(1970, 1, 1)
    static_url: str = ""
    scores: dict[str, float] = {}
    sections: dict[str, WikipediaSection] = {}
    summary: WikipediaSummary = None

    def __init__(self, article: WikipediaArticle, revision_id: int):
        self.article = article
        self.revision_id = revision_id
        self.date = wr.get_revision_date(revision_id, self.article.article_id)

        return None

    def get_score(self, score_name: str) -> float:
        score = self.sections.get(score_name)
        if score:
            return score
        return None

    def get_section(self, section_name: str) -> WikipediaSection:
        section = self.sections.get(section_name)
        if section:
            return section
        return None

    def get_summary(self) -> WikipediaSummary:
        summary = self.sections.get("Summary")
        if summary:
            return summary
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


class WikipediaSection:
    revision: WikipediaRevision
    section_name: str
    scores: dict[str, float] = field(default_factory=dict)

    def __init__(self, revision: WikipediaRevision, section_name: str):
        self.revision = revision
        self.section_name = section_name
        # TODO: init all scores


class WikipediaSummary(WikipediaSection):
    revision: WikipediaRevision
    section_name: str = "Summary"
    summary_scores: dict[str, float] = field(default_factory=dict)

    def __init__(self, revision: WikipediaRevision):
        self.revision = revision
        # TODO: init all scores
