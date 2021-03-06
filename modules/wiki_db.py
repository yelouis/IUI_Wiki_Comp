from __future__ import annotations
import psycopg2
from typing import Optional
import time
import wiki_dump as wd

# Data structure that enables easy access
# to our PSQL database
# Methods are self-explanatory
class DatabaseAccess:
    conn: Optional[psycopg2.connection] = None
    cursor: Optional[psycopg2.cursor] = None

    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                "dbname='wikipedia' user='mathcsadmin' host='127.0.0.1' password='corgiPower!'"
            )
            self.cursor = self.conn.cursor()
        except:
            print("Connection failed.")

    def pullArticleByID(self, chosenID):
        query = f"""SELECT * FROM "article" WHERE id = {chosenID}"""
        chosenArticle = self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def pullRevisionByID(self, chosenID):
        query = f"""SELECT * FROM "revisionHistory" WHERE revision_id = {chosenID}"""
        chosenRevision = self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def foreignKeyJoinByID(self, chosenID):
        query = f"""SELECT * FROM "article" INNER JOIN
        "revisionHistory" ON "article".id = "revisionHistory".article_id
        WHERE "article".id = {chosenID}"""
        chosenQuery = self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def article_id_join_search(self, chosenID):
        query = f"""SELECT * FROM "article" INNER JOIN
        "revisionHistory" ON "article".id = "revisionHistory".article_id
        WHERE "article".id = {chosenID}"""
        chosenQuery = self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def title_join_search(self, title):
        query = f"""SELECT * FROM "article" NATURAL JOIN "revisionHistory" WHERE title = '{title}'"""
        chosenQuery = self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def addColumnToTable(self, columnName, columnType, tableName):
        query = f"""ALTER TABLE "{tableName}" ADD {columnName} {columnType}"""
        chosenQuery = self.cursor.execute(query)
        self.conn.commit()
        return chosenQuery

    def dropColumn(self, columnName, tableName):
        query = f"""ALTER TABLE "{tableName}" DROP COLUMN {columnName}"""
        chosenQuery = self.cursor.execute(query)
        self.conn.commit()
        return chosenQuery

    def getArticleAuthors(self, ID):
        authors = set()
        revisions = self.article_id_join_search(ID)
        for revision in revisions:
            if(revision[11] is not None): # we may be referencing the wrong columns here
                authors.add(revision[11]) # we think 11 is for a_name
            elif(revision[12] is not None):
                authors.add(revision[12]) # we think 12 is for a_ID
            else:
                authors.add(revision[13]) # we think 13 is for a_IP

    def freeDatabaseAccess(self, query):
        chosenQuery = self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def freeCommitDatabaseAccess(self, query):
        chosenQuery = self.cursor.execute(query)
        self.conn.commit()
        return chosenQuery

def add_columns():
    testing = DatabaseAccess()

    cur = testing.cursor
    conn = testing.conn

    wiki_dump = wd.XMLDumpParser(
        "../dumps/simplewiki-latest-pages-meta-history.xml.bz2"
    )

    amount = 10
    num_commits = 0

    inserts = {1}  # dummy dict for while loop start

    # parse pages from the XML dump 
    # retrieving author name, id, and IP
    # which were not all initially retrieved
    while len(inserts) > 0:
        parse_start = time.perf_counter()
        inserts = wiki_dump.parse_n_pages(amount)
        for article in inserts.values():

            if article.id != -1:
                for revision in article.revisions:
                    revision_id = article.revisions[revision].id
                    author_name = article.revisions[revision].author_name

                    author_name = author_name.replace("$", "")

                    author_id = article.revisions[revision].author_id
                    author_ip = article.revisions[revision].author_ip

                    if revision_id != -1:
                        try:
                            cur.execute(
                                f"""UPDATE public."revisionHistory" SET a_name = $${author_name}$$, a_id = {author_id}, a_ip = $${author_ip}$$ WHERE revision_id = {revision_id}"""
                            )
                        except psycopg2.Error as e:
                            print(e)
                            quit()
        parse_end = time.perf_counter()
        conn.commit()
        commit_end = time.perf_counter()
        num_commits += 1
        print(f"Committed for the {num_commits}th time!")
        print(f"Parse Time: {(parse_end - parse_start):.3f}s")
        print(f"Commit Time: {(commit_end - parse_end):.3f}s")

    conn.commit()


def populate():
    testing = DatabaseAccess()

    cur = testing.cursor
    conn = testing.conn

    wiki_dump = wd.XMLDumpParser(
        "../dumps/simplewiki-latest-pages-meta-history.xml.bz2"
    )

    amount = 10
    num_commits = 0

    inserts = {1}  # dummy dict for while loop start

    # Parse pages from XML dump and populate PSQL database with results
    while len(inserts) > 0:
        parse_start = time.perf_counter()
        inserts = wiki_dump.parse_n_pages(amount)
        for article in inserts.values():
            # retrieve article level scores
            num_edits = article.get_score("num_edits")
            num_unique_authors = article.get_score("num_unique_authors")
            author_diversity = article.get_score("author_diversity")
            age = article.get_score("age")
            currency = article.get_score("currency")

            if article.id != -1:
                try:
                    cur.execute(
                        f"""INSERT INTO public."article" VALUES ({article.id}, $${article.title}$$,
                                {article.current_id}, {num_edits}, {num_unique_authors}, {author_diversity}, {age}, {currency})"""
                    )
                except:
                    print(f"Error adding: {article.title}")

                # populate revision history with revision level scores
                for revision in article.revisions:
                    text = article.revisions[revision].text
                    article_length = len(text)
                    # compressedArtText = zlib.compress(articleText.encode())
                    flesch = article.revisions[revision].get_score("flesch")
                    kincaid = article.revisions[revision].get_score("kincaid")
                    num_internal_links = article.revisions[revision].get_score(
                        "num_internal_links"
                    )
                    num_external_links = article.revisions[revision].get_score(
                        "num_external_links"
                    )
                    num_images = article.revisions[revision].get_score("num_images")
                    average_sentence_length = article.revisions[revision].get_score(
                        "average_sentence_length"
                    )

                    # ensure the revision is well-formatted before committing
                    if article.revisions[revision].id != -1:
                        try:
                            cur.execute(
                                f"""INSERT INTO public."revisionHistory" VALUES (
                                {article.revisions[revision].id},
                                $${article.title}$$, {num_internal_links}, {num_external_links},
                                {article_length}, {article.id}, {flesch}, {kincaid}, {num_images},
                                {average_sentence_length},
                                TIMESTAMP '{article.revisions[revision].date}', $${text}$$) """
                            )
                        except:
                            # print(f"Error adding: {article.title}: {revision=}")
                            pass
        parse_end = time.perf_counter()
        conn.commit()
        commit_end = time.perf_counter()
        num_commits += 1
        print(f"Committed for the {num_commits}th time!")
        print(f"Parse Time: {(parse_end - parse_start):.3f}s")
        print(f"Commit Time: {(commit_end - parse_end):.3f}s")

    conn.commit()

    cur.execute("""SELECT * FROM public.article""")
    rows = cur.fetchall()
    print(rows)


if __name__ == "__main__":
    add_columns()
