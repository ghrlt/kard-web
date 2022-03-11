from flask import Flask, request, render_template, redirect, abort, url_for, Response
from functools import wraps
import requests as req

from kardapi import KardCustomApi


app = Flask("KardWeb")


USERS = {}



def get_user(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		uuid = request.headers.get('k-device-uuid')
		if not uuid:
			return abort(403)

		if not uuid in USERS:
			USERS[uuid] = KardCustomApi("KardWeb github.com/ghrlt", uuid)

		return f(*args, **kwargs, u=USERS[uuid])

	return wrapper

def get_logged_user(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		uuid = request.headers.get('k-device-uuid')
		token = request.headers.get('k-authorization-token')
		if not uuid or not token:
			return abort(401)

		if not uuid in USERS:
			USERS[uuid] = KardCustomApi("KardWeb github.com/ghrlt", uuid, token)

		return f(*args, **kwargs, u=USERS[uuid])

	return wrapper

@app.route("/")
def home():
	return render_template("index.html")

@app.route("/dashboard")
def dashboard():
	return render_template("dashboard.html")

@app.route("/login/<action>", methods=['POST'])
@get_user
def login(action, u):
	phone = request.values.get('tel')
	otp = request.values.get('otp')
	pin = request.values.get('pin')

	if not phone:
		return {"status": -1, "error": "Invalid request. Phone Number is missing!"}


	if action == "request-otp":
		r = u.login(phone)
		return r

	elif action == "confirm-otp":
		if not otp:
			return {"status": -1, "error": "Invalid request. OTP is missing!"}

		r = u.login(phone, otp=otp)
		return r

	elif action == "confirm-pin":
		if not pin:
			return {"status": -1, "error": "Invalid request. PIN is missing!"}

		r = u.login(phone, pin=pin)
		return r


	return abort(404)

@app.route("/kard-api/fetch/<data>", methods=['GET'])
@get_logged_user
def fetch(data, u):
	""" fetch SHALL AND CAN ONLY BE USED TO GET ONE INFO AT A TIME """
	r = u.fetch(data)
	return r

@app.route("/kard-api/<f>")
@get_logged_user
def execFunction(f, u):
	dic = request.values.get('args')
	if dic:
		argsV = ', '.join( list(dic.values()) )
		if argsV:
			argsV = '"' + argsV + '"'

		if argsV:
			for i,key in enumerate(list(dic.keys())):
				x = argsV.split(", ")
				x[i] = f"{key}={x[i]}"

				argsV = ', '.join( x )
	else:
		argsV = ''.join([])	

	try:
		r = eval(f"u.{f}({argsV})")
		#if f == "getLimits": print(r)
		return r
	except Exception as e:
		return {"status": -1, "error": str(e), "data": None}




if __name__ == "__main__":
	app.run(port=80, debug=True)