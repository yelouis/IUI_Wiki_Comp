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
conn.commit()

# inserts = wiki_dump.parse_n_pages(amount)
#
# for article in inserts.values():
#     cur.execute(f"""INSERT INTO public."article" VALUES ({article.id}, '{article.title}', {article.current_id})""")
# conn.commit()
cur.execute("""SELECT * FROM public.article""")

rows = cur.fetchall()
print(rows)
