from __future__ import annotations
import psycopg2
from typing import Optional
import time
import wiki_dump as wd

class DatabaseAccess:
	conn: Optional[psycopg2.connection] = None
	cursors: Optional[psycopg2.cursor] = None

	def __init__(self):
		try:
			self.conn = psycopg2.connect("dbname='wikipedia' user='mathcsadmin' host='127.0.0.1' password='corgiPower!'")
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


def main():
	testing = DatabaseAccess()
	print(testing.title_join_search("April"))
	quit()

	try:
		conn = psycopg2.connect("dbname='wikipedia' user='mathcsadmin' host='127.0.0.1' password='corgiPower!'")
	except:
		print("I am unable to connect to the database")

	cur = conn.cursor()

	wiki_dump = wd.XMLDumpParser("../dumps/simplewiki-latest-pages-meta-history.xml.bz2")

	# ITERATE TO LATEST ARTICLE ADDED, PROBABLY GEA
	parse_start = time.time()
	count = wiki_dump.iterate_past_page("GEA")
	parse_end = time.time()
	print(f"{parse_end - parse_start} seconds to iterate past {count} articles.")

	amount = 10
	num_commits = 0

	inserts = {1} # dummy dict for while loop start

	while len(inserts) > 0:
		parse_start = time.time()
		inserts = wiki_dump.parse_n_pages(amount)
		for article in inserts.values():
			num_edits = article.get_score("num_edits")
			num_unique_authors = article.get_score("num_unique_authors")
			author_diversity = article.get_score("author_diversity")
			age = article.get_score("age")
			currency = article.get_score("currency")

			if article.id != -1:
				try:
					cur.execute(f"""INSERT INTO public."article" VALUES ({article.id}, $${article.title}$$,
								{article.current_id}, {num_edits}, {num_unique_authors}, {author_diversity}, {age}, {currency})""")
				except:
					print(f"Error adding: {article.title}")
				for revision in article.revisions:
					text = article.revisions[revision].text
					article_length = len(text)
					# compressedArtText = zlib.compress(articleText.encode())
					flesch = article.revisions[revision].get_score("flesch")
					kincaid = article.revisions[revision].get_score("kincaid")
					num_internal_links = article.revisions[revision].get_score("num_internal_links")
					num_external_links = article.revisions[revision].get_score("num_external_links")
					num_images = article.revisions[revision].get_score("num_images")
					average_sentence_length = article.revisions[revision].get_score("average_sentence_length")

					if article.revisions[revision].id != -1:
						try:
							cur.execute(f"""INSERT INTO public."revisionHistory" VALUES (
								{article.revisions[revision].id},
								$${article.title}$$, {num_internal_links}, {num_external_links},
								{article_length}, {article.id}, {flesch}, {kincaid}, {num_images},
								{average_sentence_length},
								TIMESTAMP '{article.revisions[revision].date}', $${text}$$) """)
						except:
							# print(f"Error adding: {article.title}: {revision=}")
							pass
		parse_end = time.time()
		conn.commit()
		commit_end = time.time()
		num_commits += 1
		print(f"Committed for the {num_commits}th time!")
		print(f"Parse Time: {(parse_end - parse_start):.3f}s")
		print(f"Commit Time: {(commit_end - parse_end):.3f}s")

	conn.commit()


	# inserts = wiki_dump.parse_n_pages(amount)
	#
	# for article in inserts.values():
	#     cur.execute(f"""INSERT INTO public."article" VALUES ({article.id}, '{article.title}', {article.current_id})""")
	# conn.commit()
	cur.execute("""SELECT * FROM public.article""")

	# SELECT * FROM public."revisionHistory" WHERE id = 2130;

	rows = cur.fetchall()
	print(rows)

if __name__=="__main__":
	main()
