from __future__ import annotations
from typing import Optional, Union
from datetime import datetime
import mwparserfromhell as mw
import re

import wiki_req as wr

SYMBOL_REGEX = "[\[\]\(\)',`~=\n\*\+\\\/]"

IMAGE_REGEX = "\[\[.*\]\]"

CATEGORY_REGEX = "Category:"

LINK_REGEX = "((http|https)?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)"

class WikipediaArticle:
    id: int = -1
    title: str = "N/A"
    current_id: int = -1
    parent_id: int = -1  # parent id
    ns: int = -1   # namespace
    revisions: dict[int, WikipediaRevision]
    notext: int = 0 # number of revisions with no text
    scores: dict[str, Union[int, float]]

    def __init__(self, id: int = None):
        self.revisions = {}
        self.scores = {}

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

    def get_score(self, score_name: str) -> Optional[Union[int, float]]:
        score = self.scores.get(score_name)
        if score:
            return score
        return None

    def calculate_scores(self):
        self.author_scores()
        self.article_age()
        
    def author_scores(self):
        authors = set()
        for revision in self.revisions.values():
            authors.add(revision.author_id)
        self.scores["num_unique_authors"] = len(authors)
        self.scores["author_diversity"] = len(authors) / len(self.revisions)

    def article_age(self):
        # get article age and currency
        current_revision = self.get_current_revision()
        if current_revision.date != datetime(1970, 1, 1):
            diff = datetime.now() - current_revision.date
            self.scores["currency"] = abs(diff.days)

class WikipediaRevision:
    id: int = -1
    date: datetime = datetime(1970, 1, 1)
    scores: dict[str, float]
    author_name: str = "N/A"
    author_id: int = -1
    raw_text: str = "N/A"
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

    def process_text(self):
        # TODO: turn wikipedia article mumbo into just text
        wikicode = mw.parse(self.raw_text)
        stripped1 = wikicode.strip_code() # removes [[page | word]] pairs and [[words]]
        stripped2 = re.sub(IMAGE_REGEX, '', stripped1) #removes [[Image:.*]]
        stripped3 = re.sub(LINK_REGEX, '', stripped2) #removes links
        stripped4 = re.sub(SYMBOL_REGEX, '', stripped3) # removes all the bad symbols (but not essential punctuation)
        stripped5 = re.sub("(?<=[a-z\.:?!0-9])(?=[A-Z])", " ", stripped4) # puts space in CacciaMagazineOttobre2020 Caccia Magazine Ottobre 2020
        self.text = re.sub(CATEGORY_REGEX, ' ', stripped5) # removes Category:

    def get_score(self, score_name: str) -> Optional[float]:
        score = self.scores.get(score_name)
        if score:
            return score
        return None

    def calculate_scores(self):
        self.internal_links()
        self.external_links()

    def internal_links(self):
        i_links = re.findall("\[\[.+|.+\]\]", self.raw_text)
        self.scores["num_internal_links"] = len(i_links)
        
        
    def external_links(self):
        i_links = re.findall(LINK_REGEX, self.raw_text)
        self.scores["num_external_links"] = len(i_links)

    def ASL(self, text):
        # TODO
        pass

    def flesch_read(self, text):
        # TODO
        pass
