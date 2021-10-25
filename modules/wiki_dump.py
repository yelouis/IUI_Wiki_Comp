import xml.etree.ElementTree as etree
import bz2

from datetime import datetime

import wiki_analysis as wa

NUM_ARTICLES = 100

# opens <filename> as bz2, decodes bz2 into xml,
# and creates an xml iterator, calls parse_wiki_xml
def load_from_bz2(filename: str, n: int = NUM_ARTICLES):
    with bz2.BZ2File(filename, 'rb') as bz2_dump:

        xml_context = etree.iterparse(bz2_dump, events=('start', 'end'))

        return parse_wiki_xml(xml_context, n)

# opens <filename> as xml, and creates an xml iterator, 
# calls parse_wiki_xml
def load_from_xml(filename: str, n: int = NUM_ARTICLES):
    xml_context = etree.iterparse(filename, events=('start', 'end'))
    
    return parse_wiki_xml(xml_context, n)

# iterates xml until it finds a page tag
# SIDE EFFECT: iterates xml_context
def parse_wiki_xml(xml_context: etree, n: int):
    articles = {}

    for event, elem in xml_context:
            tag = elem.tag.split("}")[1]

            if event == "start" and tag == "page":
                article = parse_page(xml_context)
                articles[article.id] = article

            if len(articles) == n:
                return articles

# continues xml_context and parses a single <page> tag
# if it encounters a <revision> tag, calls parse_revision()
# SIDE EFFECT: iterates xml_context
def parse_page(xml_context: etree) -> wa.WikipediaArticle:
    article = wa.WikipediaArticle()
    for event, elem in xml_context:
        tag = elem.tag.split("}")[1]
        if event == "start":
            if tag == "title":
                article.title = elem.text

            elif tag == "ns":
                if elem.text: article.ns = int(elem.text)

            elif tag == "id":
                if elem.text: article.id = int(elem.text)

            elif tag == "revision":
                revision = parse_revision(xml_context, article)
                article.revisions[revision.id] = revision 

        elif tag == "page" and event == "end":
            return article

# continues xml_context and parses a single <revision> tag
# if it encounters a <contributor> tag, calls parse_author()
# SIDE EFFECT: iterates xml_context
def parse_revision(xml_context: etree, article: wa.WikipediaArticle) -> wa.WikipediaRevision:
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

# continues xml context and parses a single <contributor> tag
# SIDE EFFECT: iterates xml_context
def parse_author(xml_context: etree):
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

    articles = load_from_bz2(DUMP_FILE, 10)

    print([a.title for a in articles.values()])


if __name__ == "__main__":
    main()