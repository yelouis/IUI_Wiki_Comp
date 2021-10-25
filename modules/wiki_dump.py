
from typing import Iterable, Tuple, Any, Optional

import bz2
from datetime import datetime
import xml.etree.ElementTree as etree

import wiki_analysis as wa

NUM_ARTICLES = 100
IGNORE_TITLES = ["User:", "Talk:", "User talk:", "Wikipedia:"]

# opens <filename> as bz2, decodes bz2 into xml,
# and creates an xml iterator, calls parse_wiki_xml
def load_from_bz2(filename: str, n: int = NUM_ARTICLES):
    with bz2.BZ2File(filename, 'rb') as bz2_dump:

        xml_context = etree.iterparse(bz2_dump, events=('start', 'end'))
        print(type(xml_context))

        return parse_wiki_xml(xml_context, n)

# opens <filename> as xml, and creates an xml iterator, 
# calls parse_wiki_xml
def load_from_xml(filename: str, n: int = NUM_ARTICLES):
    xml_context = etree.iterparse(filename, events=('start', 'end'))
    
    return parse_wiki_xml(xml_context, n)

# iterates xml until it finds a page tag
# SIDE EFFECT: iterates xml_context
def parse_wiki_xml(xml_context: Iterable[Tuple[str, Any]], n: int):
    articles = {}

    for event, elem in xml_context:
            tag = elem.tag.split("}")[1]

            if event == "start" and tag == "page":
                article = parse_page(xml_context)
                if article:
                    articles[article.id] = article

            if len(articles) == n:
                return articles

# continues xml_context and parses a single <page> tag
# if it encounters a <revision> tag, calls parse_revision()
# SIDE EFFECT: iterates xml_context
def parse_page(xml_context: Iterable[Tuple[str, Any]]) -> Optional[wa.WikipediaArticle]:
    article = wa.WikipediaArticle()
    for event, elem in xml_context:
        tag = elem.tag.split("}")[1]
        if event == "start":
            if tag == "title":
                # ignore certain pages (i.e. user pages / talk pages)
                for it in IGNORE_TITLES:
                    if str(elem.text).startswith(it):
                        iterate_to_page_end(xml_context)
                        return None
                article.title = elem.text

            elif tag == "ns":
                if elem.text: article.ns = int(elem.text)

            elif tag == "id":
                if elem.text: article.id = int(elem.text)

            elif tag == "revision":
                revision = parse_revision(xml_context, article)
                if revision:
                    article.revisions[revision.id] = revision 

        elif tag == "page" and event == "end":
            return article

    return None

# continues xml_context and parses the remainder
# of a <page> tag, ignoring all the data
# SIDE EFFECT: iterates xml_context
def iterate_to_page_end(xml_context: Iterable[Tuple[str, Any]]):
    for event, elem in xml_context:
        tag = elem.tag.split("}")[1]
        if tag == "page" and event == "end":
            return True
    
    return False

# continues xml_context and parses a single <revision> tag
# if it encounters a <contributor> tag, calls parse_author()
# SIDE EFFECT: iterates xml_context
def parse_revision(xml_context: Iterable[Tuple[str, Any]], article: wa.WikipediaArticle) -> Optional[wa.WikipediaRevision]:
    revision = wa.WikipediaRevision()
    revision.article = article
    
    for event, elem in xml_context:
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
                revision.author_name, revision.author_id = parse_author(xml_context)

            elif tag == "text":
                revision.text = elem.text

        elif tag == "revision" and event == "end":
            return revision
    
    return None

# continues xml context and parses a single <contributor> tag
# SIDE EFFECT: iterates xml_context
def parse_author(xml_context: Iterable[Tuple[str, Any]]):
    username, id = "", -1

    for event, elem in xml_context:
        tag = elem.tag.split("}")[1]
        if event == "start":
            if tag == "username":
                username = elem.text

            elif tag == "id":
                id = elem.text

        elif tag == "contributor" and event == "end":
            return username, id

def main():
    DUMP_FILE = '../dumps/simplewiki-20211001-pages-meta-current.xml.bz2'

    articles = load_from_bz2(DUMP_FILE, 100)

    print([article.title for article in articles.values()])

    print(len(articles))


if __name__ == "__main__":
    main()