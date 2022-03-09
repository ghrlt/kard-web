from flask import Flask, request, render_template, redirect, abort, url_for, Response
import requests as req

from kardapi import KardCustomApi


app = Flask("KardWeb")
Kard = KardCustomApi()


@app.route("/")
def home():
	return render_template("index.html")

if __name__ == "__main__":
	app.run(port=80, debug=True)