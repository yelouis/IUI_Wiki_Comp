from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
import requests

@dataclass
class WikipediaArticle:
    article_id: int
    name: str = ""
    url: str = ""
    current_revision_id: int = -1
    parent_revision_id: int = -1
    revisions: dict[int, WikipediaRevision] = field(default_factory=dict)

    def __init__(self, article_id: int):
        self.article_id = article_id     
        self.init_article()
        self.init_revisions()

    def init_article(self):
        # TODO: API call to get standard info from wikipage
        pass

    def init_revisions(self):
        # TODO: init all revisions from API calls
        pass

    def get_current_revision(self) -> WikipediaRevision:
        current_revision = self.revisions.get(self.current_revision_id)
        if current_revision: return current_revision
        return None

    def get_parent_revision(self) -> WikipediaRevision:
        parent_revision = self.revisions.get(self.parent_revision_id)
        if parent_revision: return parent_revision
        return None

@dataclass
class WikipediaRevision:
    article: WikipediaArticle
    revision_id: int
    date: date = date(1970, 1, 1)
    static_url: str = ""
    scores: dict[str, float] = field(default_factory=dict)
    sections: dict[str, WikipediaSection] = field(default_factory=dict)
    summary: WikipediaSummary = None

    def __init__(self, article: WikipediaArticle, revision_id: int):
        self.article = article
        self.revision_id = revision_id
        # TODO: init all scores, init all sections, init summary

    def get_score(self, score_name: str) -> float:
        score = self.sections.get(score_name)
        if score: return score
        return None

    def get_section(self, section_name: str) -> WikipediaSection:
        section = self.sections.get(section_name)
        if section: return section
        return None

    def get_summary(self) -> WikipediaSummary:
        summary = self.sections.get("Summary")
        if summary: return summary
        return None

@dataclass
class WikipediaSection:
    revision: WikipediaRevision
    section_name: str
    scores: dict[str, float] = field(default_factory=dict)

    def __init__(self, revision: WikipediaRevision, section_name: str):
        self.revision = revision
        self.section_name = section_name
        # TODO: init all scores

@dataclass
class WikipediaSummary(WikipediaSection):
    revision: WikipediaRevision
    section_name: str = "Summary"
    summary_scores: dict[str, float] = field(default_factory=dict)

    def __init__(self, revision: WikipediaRevision):
        self.revision = revision
        # TODO: init all scores