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


def main():
	try:
		conn = psycopg2.connect("dbname='wikipedia' user='mathcsadmin' host='127.0.0.1' password='corgiPower!'")
	except:
		print("I am unable to connect to the database")

	cur = conn.cursor()

	wiki_dump = wd.XMLDumpParser("../dumps/simplewiki-latest-pages-meta-history.xml.bz2")

	amount = 10
	inserts = wiki_dump.parse_n_pages(amount)
	commitTime = 0


	while len(inserts) > 0:
		parse_start = time.time()
		for article in inserts.values():
			num_edits = article.get_score("num_edits")
			num_unique_authors = article.get_score("num_unique_authors")
			author_diversity = article.get_score("author_diversity")
			age = article.get_score("age")
			currency = article.get_score("currency")

			if article.id != -1:
				cur.execute(f"""INSERT INTO public."article" VALUES ({article.id}, $${article.title}$$,
				{article.current_id}, {num_edits}, {num_unique_authors}, {author_diversity}, {age}, {currency})""")
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
						cur.execute(f"""INSERT INTO public."revisionHistory" VALUES (
							{article.revisions[revision].id},
							$${article.title}$$, {num_internal_links}, {num_external_links},
							{article_length}, {article.id}, {flesch}, {kincaid}, {num_images},
							{average_sentence_length},
							TIMESTAMP '{article.revisions[revision].date}', $${text}$$) """)
		parse_end = time.time()
		conn.commit()
		commit_end = time.time()
		commitTime += 1
		print("Committed" + str(commitTime))
		print("Parse Time: " + str(parse_end - parse_start))
		print("Commit Time: " + str(commit_end - parse_end))
		inserts = wiki_dump.parse_n_pages(amount)


	# for article in inserts.values():
	#     try:
	#         cur.execute(f"""INSERT INTO public."article" VALUES ({article.id}, '{article.title}', {article.current_id})""")
	#     except:
	#         print("pageID already exists")

		# for revision in article.revisions:
		# 	try:
		#      cur.execute(f"""INSERT INTO public."revisionHistory" VALUES (
		#      	{revision.id},
		#      	'{revision.title}',
		#      	{revision.date},
		#      	{revision.author_metrics(revision.id)},
		#      	{revision.num_edits},
		#      	{revision.num_edits_regis},
		#      	{revision.num_edits_anom},
		#      	{revision.internal_links(revision.id)},
		#      	{revision.external_links(revision.id)},
		#      	{len(revision.text)},
		#      	{revision.author_metrics(revision.id)},
		#      	{revision.admin_edits_prop},
		#      	{revision.article_age(revision.id)},
		#      	{article.revisions.values().index(revision)},
		#      	{revision.mean_revision_time},
		#      	{article.id}, )""")
		#      # info we cannot get yet:
		#      # title
		#      # num_edits
		#      # num_edits_regis
		#      # num_edits_anom
		#      # art_length - depending on what this is asking. Right now I am just getting text length
		#      # author_diversity - this comes from author_metrics(revision.id)? What is the return type of this function?
		#      # admin_edits_prop
		#      # mean_revision_time
		#  except:
		#      print("id already exists")

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
