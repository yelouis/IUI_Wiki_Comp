from flask import Flask, request, render_template
import sys

sys.path.insert(1, '../modules')

import wiki_db as db
# import wiki_db as db

# access will allow us to make calls to the database
access = db.DatabaseAccess()

app = Flask(__name__)

# a_data and r_data is what is pulled from the DB and used to  populate the HTML for the user to view
a_data = []
r_data = []

@app.route("/")
def home():
	return render_template("index.html")

# This method is called when there is new user input on the HTML page home.html
@app.route('/', methods=['POST'])
def my_form_post():
	global a_data
	global r_data
	if request.form['submit_button'] == "Search Article":
		text = request.form['article_input']
		processed_text = text.upper()
		a_data = access.pullArticleByID(processed_text)
		# relaod the webpage with the updated information that was pulled from access
		return render_template("index.html", article_data=a_data, revision_data=r_data)

	elif request.form['submit_button'] == "Search Revision":
		text = request.form['revision_input']
		processed_text = text.upper()
		r_data = access.pullRevisionByID(processed_text)
		# relaod the webpage with the updated information that was pulled from access
		return render_template("index.html", article_data=a_data, revision_data=r_data)

	# relaod the webpage with no new information
	return render_template("home.html")

if __name__ == "__main__":
	app.run(debug=True)
