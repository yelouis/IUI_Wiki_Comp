from __future__ import annotations
from typing import Optional, Union
from datetime import datetime
import mwparserfromhell as mw
import re
import textstat

import wiki_req as wr

# Globals for parsing text

SYMBOL_REGEX = "[\[\]\(\)',`~=\n\*\+\\\/$%&\^\*]"

IMAGE_REGEX = "\[\[.*\]\]"

CATEGORY_REGEX = "Category:"

LINK_REGEX = "((http|https)?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)"

# Scores calculate per A-rticle/R-evision

A_SCORES = ["num_edits", "num_unique_authors",
            "author_diversity", "age", "currency"]
R_SCORES = [
    "num_internal_links",
    "num_external_links",
    "num_images",
    "flesch",
    "kincaid",
    "average_sentence_length",
]

# Data structure to hold essential article information from XML dump


class WikipediaArticle:
    id: int = -1  # article ID (different from revision IDs)
    title: str = "N/A"
    current_id: int = -1  # most recent revision ID
    first_id: int = -1  # least recent revision ID
    ns: int = -1  # namespace
    revisions: dict[int, WikipediaRevision]
    notext: int = 0  # number of revisions with no text
    scores: dict[str, Union[int, float]]

    def __init__(self, id: int = None):
        self.revisions = {}
        self.scores = {}

        if id is not None:
            self.id = id
            rvs, self.current_id, parent_id = wr.get_article_properties(
                self.id)

            for rv in rvs:
                self.revisions[rv] = WikipediaRevision(self, rv)

    def __repr__(self):
        return f"Article(id={self.id}, title={self.title}, num_revisions={len(self.revisions)}, num_notext={self.notext})"

    def __str__(self):
        return f"{self.id}, {self.title}, {self.current_id}, {len(self.revisions)}, {self.notext},\n"

    # Returns the WikipediaRevision object associated with the current_id
    def get_current_revision(self) -> Optional[WikipediaRevision]:
        current_revision = self.revisions.get(self.current_id)
        if current_revision:
            return current_revision
        return None

    # Returns the score (if any) associated with the given name
    def get_score(self, score_name: str) -> Optional[Union[int, float]]:
        score = self.scores.get(score_name)
        if score:
            return score
        return None

    # Can be called upon the article being propogated with data
    def calculate_scores(self):
        self.author_scores()
        self.article_age()
        self.scores["num_edits"] = len(self.revisions)

        for revision in self.revisions.values():
            revision.calculate_scores()

    # Calculate basic scores from revision history
    def author_scores(self):
        if len(self.revisions) > 0:
            authors = set()
            for revision in self.revisions.values():
                authors.add(revision.author_id)
            self.scores["num_unique_authors"] = len(authors)
            self.scores["author_diversity"] = len(
                authors) / len(self.revisions)

    # Calculate the article age from the most recent revision
    # to the least recent
    def article_age(self):
        if len(self.revisions) > 0:
            now = datetime.now()
            first_revision = self.revisions.get(self.first_id)
            current_revision = self.revisions.get(self.current_id)

            self.scores["age"] = (now - first_revision.date).days
            self.scores["currency"] = (now - current_revision.date).days

# Data structure to hold essential revision information from XML dump


class WikipediaRevision:
    id: int = -1  # revision ID (different from article ID)
    date: datetime = datetime(1970, 1, 1)  # date the revision was posted
    scores: dict[str, float]
    author_name: str = "N/A"
    author_id: int = -1
    author_ip: str = "N/A"
    raw_text: str = "N/A"  # raw unprocessed text of article
    text: str = "N/A"  # processed text

    def __init__(self, article: WikipediaArticle = None, id: int = None):
        self.scores = {}
        if article is not None and id is not None:
            self.article = article
            self.id = id
            self.date = wr.get_revision_date(id, self.article.id)

    def __str__(self):
        # TODO: Add self.text to the end, add all the scores to the end
        return f"{self.id}, {self.date}, {self.author_name}, {self.author_id},\n"

    # remove all the bad stuff that might be in wiki markup language
    def process_text(self):
        wikicode = mw.parse(self.raw_text)
        # removes [[page | word]] pairs and [[words]]
        stripped1 = wikicode.strip_code()
        stripped2 = re.sub(IMAGE_REGEX, "", stripped1)  # removes [[Image:.*]]
        stripped3 = re.sub(LINK_REGEX, "", stripped2)  # removes links
        stripped4 = re.sub(
            SYMBOL_REGEX, "", stripped3
        )  # removes all the bad symbols (but not essential punctuation)
        stripped5 = re.sub(
            "(?<=[a-z\.:?!0-9])(?=[A-Z])", " ", stripped4
        )  # puts space in CacciaMagazineOttobre2020 Caccia Magazine Ottobre 2020
        self.text = re.sub(CATEGORY_REGEX, " ", stripped5)  # removes Category:

    # Returns the score (if any) associated with the given name
    def get_score(self, score_name: str) -> Optional[float]:
        score = self.scores.get(score_name)
        if score:
            return score
        return -1

    # Can be called upon the revision being propogated with data
    def calculate_scores(self):
        self.internal_links()
        self.external_links()
        self.num_images()
        self.textstat_scores()

    # Based on the structure of links in WML
    # identifies all internal links (to other Wikipedia articles)
    def internal_links(self):
        if self.raw_text != "N/A":
            i_links = re.findall("\[\[.+|.+\]\]", self.raw_text)
            self.scores["num_internal_links"] = len(i_links)

    # Identifies any actual links
    def external_links(self):
        if self.raw_text != "N/A":
            i_links = re.findall(LINK_REGEX, self.raw_text)
            self.scores["num_external_links"] = len(i_links)

    # Based on structure of images in WML
    # identifies all images
    def num_images(self):
        if self.raw_text != "N/A":
            images = re.findall("\[\[Image:.*\]\]", self.raw_text)
            self.scores["num_images"] = len(images)

    # Calculate basic text scores from the processed text
    def textstat_scores(self):
        if self.text != "N/A":
            self.scores["flesch"] = textstat.flesch_reading_ease(self.text)
            self.scores["kincaid"] = textstat.flesch_kincaid_grade(self.text)
            self.scores["average_sentence_length"] = textstat.avg_sentence_length(
                self.text
            )
