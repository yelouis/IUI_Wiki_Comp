# https://www.heatonresearch.com/2017/03/03/python-basic-wikipedia-parsing.html

import wiki_dump as wd

def main():
    DUMP_FILE = 'simplewiki-20211001-pages-meta-current.xml.bz2'

    articles = wd.load_from_bz2(DUMP_FILE)


if __name__ == "__main__":
    main()