from __future__ import annotations
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
            self.bz2_dump = bz2.BZ2File(filename, "rb")
            self.xml_context = etree.iterparse(self.bz2_dump, events=("start", "end"))
        elif filename[-3:] == "xml":
            self.xml_context = etree.iterparse(filename, events=("start", "end"))
        else:
            print(f"Unknown file encoding for {filename}")

    def cleanup(self):
        if self.bz2_dump is not None:
            self.bz2_dump.close()

    # iterates the XML context until a <page>
    # object with the corresponding `page_title` is found
    # SIDE EFFECT: iterates xml_context
    def iterate_past_page(self, page_title: str) -> int:
        count = 0
        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]

            if event == "start" and tag == "page":
                count += 1
                if count % 100 == 0:
                    print(f"== {count} articles skipped! == ")

            if event == "start" and tag == "title":
                if elem.text == page_title:
                    elem.clear()
                    break

            elem.clear()

        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]

            if event == "end" and tag == "page":
                elem.clear()
                return count

            elem.clear()

        return -1

    # parses n pages 
    # outputs the information to CSV
    # SIDE EFFECT: iterates xml context
    def write_n_pages_to_csv(self, r_folder: str, filename: str, n: int) -> bool:
        articles = self.parse_n_pages(n)
        try:
            with open(filename, "w") as out:
                out.write(
                    "pageId, name, currentId, parentId, numRevisions, numNoText\n"
                )
                for a in articles.values():
                    out.write(str(a))
                    r_fname = f"{r_folder}{a.id}_revisions.csv"
                    with open(r_fname, "w") as r_out:
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
    def parse_single_page(self) -> Optional[wa.WikipediaArticle]:
        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]

            if event == "start" and tag == "page":
                elem.clear()
                return self._parse_page()

            elem.clear()

        return None

    # iterates xml until it finds a page tag
    # then parses that page via _parse_page()
    # returns a dict of pages once n pages are collected
    # SIDE EFFECT: iterates xml_context
    def parse_n_pages(self, n: int) -> dict[int, wa.WikipediaArticle]:
        articles = {}

        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]

            if event == "start" and tag == "page":
                article = self._parse_page()
                if article:
                    articles[article.id] = article
                    if (
                        PRINT_PROGRESS
                        and n >= 10
                        and (len(articles) % int(n / 10)) == 0
                    ):
                        print(f"== {len(articles)} processed ==")

            if len(articles) == n:
                elem.clear()
                return articles

            elem.clear()

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
                            elem.clear()
                            return None

                elif tag == "id":
                    if elem.text:
                        article.id = int(elem.text)

                elif tag == "revision":
                    revision = self._parse_revision(article)
                    if revision:
                        article.revisions[revision.id] = revision

            elif tag == "page" and event == "end":
                if len(article.revisions) > 0:
                    sorted_keys = [
                        k
                        for k, v in sorted(
                            article.revisions.items(), key=lambda item: item[1].date
                        )
                    ]
                    article.current_id = sorted_keys[0]
                    article.first_id = sorted_keys[-1]
                article.calculate_scores()
                elem.clear()
                return article

            elem.clear()

        return None

    # continues xml_context and parses the remainder
    # of a <page> tag, ignoring all the data
    # SIDE EFFECT: iterates xml_context
    def _iterate_to_page_end(self) -> bool:
        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]
            if tag == "page" and event == "end":
                elem.clear()
                return True
            elem.clear()

        return False

    # continues xml_context and parses a single <revision> tag
    # if it encounters a <contributor> tag, calls parse_author()
    # SIDE EFFECT: iterates xml_context
    def _parse_revision(
        self, article: wa.WikipediaArticle
    ) -> Optional[wa.WikipediaRevision]:
        revision = wa.WikipediaRevision()

        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]
            if event == "start":
                if tag == "id":
                    if elem.text:
                        revision.id = int(elem.text)

                elif tag == "timestamp":
                    if elem.text:
                        revision.date = datetime.strptime(
                            elem.text, "%Y-%m-%dT%H:%M:%SZ"
                        )

                elif tag == "contributor":
                    author_name, author_id, author_ip = self._parse_author()
                    if author_name:
                        revision.author_name = author_name

                    if author_id:
                        revision.author_id = author_id

                    if author_ip:
                        revision.author_ip = author_ip

                elif tag == "text":
                    if not elem.text:
                        article.notext += 1
                        if not INCLUDE_NO_TEXT:
                            self._iterate_to_revision_end()
                            elem.clear()
                            return None

                    revision.raw_text = elem.text
                    revision.process_text()

            elif tag == "revision" and event == "end":
                elem.clear()
                return revision

            elem.clear()

        return None

    # continues xml_context and parses the remainder
    # of a <revision> tag, ignoring all the data
    # SIDE EFFECT: iterates xml_context
    def _iterate_to_revision_end(self) -> bool:
        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]
            if tag == "revision" and event == "end":
                elem.clear()
                return True

            elem.clear()

        return False

    # continues xml context and parses a single <contributor> tag
    # SIDE EFFECT: iterates xml_context
    def _parse_author(self) -> Tuple[str, int]:
        username, id, ip = "", -1, ""

        for event, elem in self.xml_context:
            tag = elem.tag.split("}")[1]
            if event == "start":
                if tag == "username":
                    username = elem.text

                elif tag == "id":
                    id = elem.text

                elif tag == "ip":
                    ip = elem.text

            elif tag == "contributor" and event == "end":
                elem.clear()
                return username, id, ip

            elem.clear()

        return username, id, ip

# test parse 10 pages from XML
def main():
    DUMP_FILE = "../dumps/simplewiki-latest-pages-meta-history.xml.bz2"

    parser = XMLDumpParser(DUMP_FILE)

    articles = parser.parse_n_pages(10)
    for a in articles.values():
        a.calculate_scores()
        for r in a.revisions.values():
            print(r.scores)
        print(repr(a))
        print(a.scores)


if __name__ == "__main__":
    main()
