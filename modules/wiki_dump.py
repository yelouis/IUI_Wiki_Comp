
from typing import Iterable, Tuple, Any, Optional, IO

import bz2
from datetime import datetime
import xml.etree.ElementTree as etree

import wiki_analysis as wa

NUM_ARTICLES = 100
INCLUDE_NO_TEXT = False
PRINT_PROGRESS = False

class XMLDumpParser:
    xml_context: Iterable[Tuple[str, Any]]
    bz2_dump: Optional[IO[bytes]] = None

    # gets XML context for <filename>
    # decoding if it's stored as bz2
    def __init__(self, filename: str):
        if filename[-3:] == "bz2":
            self.bz2_dump = bz2.BZ2File(filename, 'rb')
            self.xml_context = etree.iterparse(self.bz2_dump, events=('start', 'end'))
        elif filename[-3:] == "xml":
            self.xml_context = etree.iterparse(filename, events=('start', 'end'))
        else:
            print(f"Unknown file encoding for {filename}")

    def cleanup(self):
        if self.bz2_dump is not None:
            self.bz2_dump.close()

    def write_n_pages_to_csv(self, filename: str, r_folder: str, n: int) -> bool:
        articles = self.parse_n_pages(n)
        try:
            with open(filename, 'w') as out:
                out.write("pageId, name, currentId, parentId, numRevisions, numNoText")
                for a in articles.values():
                    out.write(str(a))
                    r_fname = r_folder + f"{a.id}_revisions.csv"
                    with open(r_fname, 'w') as r_out:
                        for r in a.revisions.values():
                            r_out.write(str(r))

            return True
        except Exception as e:
            print(e)
            print("Error creating file.")
            return False

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
                    if PRINT_PROGRESS and n >= 10 and (len(articles) % int(n / 10)) == 0:
                        print(f"== {len(articles)} processed ==")

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
                    article.title = elem.text

                elif tag == "ns":
                    if elem.text:
                        # if namespace is 0, then it's a normal article
                        if int(elem.text) == 0:
                            article.ns = int(elem.text)
                        else:
                            self._iterate_to_page_end()
                            return None

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
    def _iterate_to_page_end(self):
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
                    a_name, a_id = self._parse_author()
                    if a_name:
                        revision.author_name = a_name

                    if a_id:
                        revision.author_id = a_id

                elif tag == "text":
                    if not elem.text:
                        article.notext += 1
                        if not INCLUDE_NO_TEXT:
                            self._iterate_to_revision_end()
                            return None

                    revision.text = elem.text

            elif tag == "revision" and event == "end":
                return revision

        return None

    # continues xml_context and parses the remainder
    # of a <revision> tag, ignoring all the data
    # SIDE EFFECT: iterates xml_context
    def _iterate_to_revision_end(self):
        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]
            if tag == "revision" and event == "end":
                return True

        return False

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
    DUMP_FILE = '../dumps/simplewiki-latest-pages-meta-history.xml.bz2'

    parser = XMLDumpParser(DUMP_FILE)

    print(parser.parse_n_pages(3))

    # parser.write_n_pages_to_csv("test.csv", "", 10)


if __name__ == "__main__":
    main()
