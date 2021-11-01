import psycopg2

import wiki_dump as wd

try:
    conn = psycopg2.connect("dbname='wikipedia' user='mathcsadmin' host='127.0.0.1' password='corgiPower!'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()

wiki_dump = wd.XMLDumpParser("../dumps/simplewiki-latest-pages-meta-history.xml.bz2")

amount = 11
inserts = wiki_dump.parse_n_pages(amount)

for article in inserts.values():
    try:
        cur.execute(f"""INSERT INTO public."article" VALUES ({article.id}, '{article.title}', {article.current_id})""")
    except:
        print("pageID already exists")

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

rows = cur.fetchall()
print(rows)
