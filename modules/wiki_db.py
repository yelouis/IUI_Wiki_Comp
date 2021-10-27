import psycopg2

# import wiki_dump as wd

try:
    conn = psycopg2.connect("dbname='wikipedia' user='mathcsadmin' host='127.0.0.1' password='corgiPower!'")
except:
    print("I am unable to connect to the database")

cur = conn.cursor()
cur.execute("""INSERT INTO public."article" VALUES (1, 'test1', 'testURL1', 'testText1')""")
conn.commit()
cur.execute("""SELECT * FROM public.article""")

rows = cur.fetchall()
print(rows)
