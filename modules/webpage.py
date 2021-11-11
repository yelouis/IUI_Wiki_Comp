import wiki_db as db
from flask import Flask, request, render_template

access = db.DatabaseAccess()

app = Flask(__name__)

def helper(article_id):
	print(article_id)

@app.route("/")
def home():
	return render_template("home.html")

@app.route('/', methods=['POST'])
def my_form_post():
	if request.form['submit_button'] == "Search Article":
		text = request.form['article']
		processed_text = text.upper()
		print(processed_text)
		# when we pull article by title, do API disambiguation, then if there's
		# only 1 option, pass that as parameter to psycopg2, otherwise, pass first option?
		listOfTuples = access.pullArticleByID(processed_text)
	elif request.form['submit_button'] == "Search Revision":
		text = request.form['revision']
		processed_text = text.upper()
		print(processed_text)
		listOfTuples = access.pullRevisionByID(processed_text)
	return render_template("home.html")

if __name__ == "__main__":
	app.run()
