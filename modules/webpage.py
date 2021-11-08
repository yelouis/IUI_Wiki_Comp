from flask import Flask

import testFlask as tf

app = Flask(__name__)

@app.route("/")
def home():
	return "hello <h1>world!<h1>" + tf.testFlask()

if __name__ == "__main__":
	app.run()