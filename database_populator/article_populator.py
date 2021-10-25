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


def main():
    DUMP_FILE = '../dumps/simplewiki-20211001-pages-meta-current.xml.bz2'

    articles = load_from_bz2(DUMP_FILE, 10)

    print([a.title for a in articles.values()])


if __name__ == "__main__":
    main()
