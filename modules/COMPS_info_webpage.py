from flask import Flask, request, render_template

app = Flask(__name__)

@app.route("/")
def home():
	return render_template("info_webpage_home.html")

if __name__ == "__main__":
	app.run()
