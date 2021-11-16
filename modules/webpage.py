import wiki_db as db
from flask import Flask, request, render_template

# access will allow us to make calls to the database
access = db.DatabaseAccess()

app = Flask(__name__)

# a_data and r_data is what is pulled from the DB and used to  populate the HTML for the user to view
a_data = []
r_data = []

@app.route("/")
def home():
	return render_template("home.html")

# This method is called when there is new user input on the HTML page home.html
@app.route('/', methods=['POST'])
def my_form_post():
	global a_data
	global r_data
	if request.form['submit_button'] == "Search Article":
		text = request.form['article']
		processed_text = text.upper()
		# when we pull article by title, do API disambiguation, then if there's
		# only 1 option, pass that as parameter to psycopg2, otherwise, pass first option?
		a_data = access.pullArticleByID(processed_text)
		return render_template("home.html", article_data=a_data, revision_data=r_data)

	elif request.form['submit_button'] == "Search Revision":
		text = request.form['revision']
		processed_text = text.upper()
		print(processed_text)

		r_data = access.pullRevisionByID(processed_text)
		return render_template("home.html", article_data=a_data, revision_data=r_data)

	return render_template("home.html")

if __name__ == "__main__":
	app.run()
