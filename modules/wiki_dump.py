
from typing import Iterable, Tuple, Any, Optional, IO

import bz2
from datetime import datetime
import xml.etree.ElementTree as etree

import wiki_analysis as wa

NUM_ARTICLES = 100
IGNORE_TITLES = ["User:", "Talk:", "User talk:", "Wikipedia:"]

class XMLDumpParser:
    xml_context: Iterable[Tuple[str, Any]]
    bz2_dump: Optional[IO[bytes]] = None

    # gets XML context for <filename>
    # decoding if it's stored as bz2
    def __init__(self, filename):
        if filename[-3:] == "bz2":
            self.bz2_dump = bz2.BZ2File(filename, 'rb')
            self.xml_context = etree.iterparse(self.bz2_dump, events=('start', 'end'))
        elif filename[-3:] == "xml":
            self.xml_context = etree.iterparse(filename, events=('start', 'end'))

    def cleanup(self):
        if self.bz2_dump is not None:
            self.bz2_dump.close()

    # iterates the XML context once from <page>
    # to </page> producing a single article object
    # SIDE EFFECT: iterates xml_context
    def parse_single_page(self):
        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]

            if event == "start" and tag == "page":
                return self._parse_page()

    # iterates xml until it finds a page tag
    # then parses that page via _parse_page()
    # returns a dict of pages once n pages are collected
    # SIDE EFFECT: iterates xml_context
    def parse_n_pages(self, n: int):
        articles = {}

        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]

            if event == "start" and tag == "page":
                article = self._parse_page()
                if article:
                    articles[article.id] = article

            if len(articles) == n:
                return articles

    # continues xml_context and parses a single <page> tag
    # if it encounters a <revision> tag, calls parse_revision()
    # SIDE EFFECT: iterates xml_context
    def _parse_page(self) -> Optional[wa.WikipediaArticle]:
        article = wa.WikipediaArticle()
        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]
            if event == "start":
                if tag == "title":
                    # ignore certain pages (i.e. user pages / talk pages)
                    for it in IGNORE_TITLES:
                        if str(elem.text).startswith(it):
                            self.iterate_to_page_end()
                            return None
                    article.title = elem.text

                elif tag == "ns":
                    if elem.text: article.ns = int(elem.text)

                elif tag == "id":
                    if elem.text: article.id = int(elem.text)

                elif tag == "revision":
                    revision = self._parse_revision(article)
                    if revision:
                        article.revisions[revision.id] = revision 

            elif tag == "page" and event == "end":
                return article

        return None

    # continues xml_context and parses the remainder
    # of a <page> tag, ignoring all the data
    # SIDE EFFECT: iterates xml_context
    def iterate_to_page_end(self):
        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]
            if tag == "page" and event == "end":
                return True
        
        return False

    # continues xml_context and parses a single <revision> tag
    # if it encounters a <contributor> tag, calls parse_author()
    # SIDE EFFECT: iterates xml_context
    def _parse_revision(self, article: wa.WikipediaArticle) -> Optional[wa.WikipediaRevision]:
        revision = wa.WikipediaRevision()
        revision.article = article
        
        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]
            if event == "start":
                if tag == "id":
                    if elem.text:
                        revision.id = int(elem.text)
                    if len(article.revisions) == 0:
                        # first revision -> newest
                        article.current_id = revision.id

                elif tag == "parentid":
                    if len(article.revisions) == 0 and elem.text:
                        # first revision -> newest
                        article.parent_id = int(elem.text)

                elif tag == "timestamp":
                    if elem.text:
                        revision.date = datetime.strptime(elem.text, "%Y-%m-%dT%H:%M:%SZ")

                elif tag == "contributor":
                    revision.author_name, revision.author_id = self._parse_author()

                elif tag == "text":
                    revision.text = elem.text

            elif tag == "revision" and event == "end":
                return revision
        
        return None

    # continues xml context and parses a single <contributor> tag
    # SIDE EFFECT: iterates xml_context
    def _parse_author(self) -> Tuple[str, int]:
        username, id = "", -1

        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]
            if event == "start":
                if tag == "username":
                    username = elem.text

                elif tag == "id":
                    id = elem.text

            elif tag == "contributor" and event == "end":
                return username, id
        
        return username, id

def main():
    DUMP_FILE = '../dumps/simplewiki-20211001-pages-meta-current.xml.bz2'

    parser = XMLDumpParser(DUMP_FILE)

    article = parser.parse_single_page()

    print(article.title)

    articles = parser.parse_n_pages(100)

    print([article.title for article in articles.values()])

if __name__ == "__main__":
    main()