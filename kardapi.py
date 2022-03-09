import requests
import json

class KardCustomApi:
	API_URL = "https://api.kard.eu/graphql"
	
	def __init__(self, user_agent: str, client_uuid: str, token: str=""):
		# Client specific
		self.USERAGENT = user_agent
		self.UUID = client_uuid
		self.AUTH_TOKEN = token
	
		# General
		self.s = requests.Session()
		self.payloads = {
			"fetch": {
				"firstname": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { firstName }}","variables":{},"extensions":{}},
				"lastname": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { lastName }}","variables":{},"extensions":{}}
			}
		}

		self.LOGIN_HEADERS = {
			'content-type': "application/json",
			'content-length': "666",
			'host': "api.kard.eu",
			'connection': "Keep-Alive",
			'accept-encoding': "gzip",
			'user-agent': self.USERAGENT,
			'vendoridentifier': self.UUID,
			'accept-language': "en"
		}

		self.LOGGED_HEADERS = {
			"content-type": "application/json",
			"content-length": "666",
			"host": "api.kard.eu",
			"connection": "Keep-Alive",
			"accept-encoding": "gzip",
			'user-agent': self.USERAGENT,
			'vendoridentifier': self.UUID,
			"authorization": "Bearer " + self.AUTH_TOKEN,
			"accept-language": "en"
		}


		if self.AUTH_TOKEN:
			self.force_login()

	def force_login(self):
		self.s.headers = self.LOGGED_HEADERS


	def login(self, phone_number: str, otp: str=None, pin: str=None) -> dict:
		if not otp and not pin:
			payload = {
				"query": "mutation androidInitSession($createUser: Boolean, $phoneNumber: PhoneNumber!, $platform: DevicePlatform, $vendorIdentifier: String!) { initSession(input: {createUser: $createUser, phoneNumber: $phoneNumber, platform: $platform, vendorIdentifier: $vendorIdentifier}) { challenge expiresAt errors { path message } }}",
				"variables": {
					"platform": "ANDROID", "createUser": True,
					"phoneNumber": phone_number, "vendorIdentifier": self.UUID
				},
				"extensions": {}
			}

			data = self.s.post(self.API_URL, json=payload, headers=self.LOGIN_HEADERS).json()

			if data.get('errors'):
				return {"status": -1, "error": data['errors'][0]['extensions']['problems'][0]['explanation']}

			if data['data']['initSession']['challenge'] == "OTP":
				# First login on UUID
				return {"status": 0, "error": None, "data": {"msg": "OTP requested", "pin": False}}

			elif data['data']['initSession']['challenge'] == "PASSCODE":
				# User PIN needed
				return {"status": 0, "error": None, "data": {"msg": "PIN requested", "pin": True}}

			else:
				# What?
				return {"status": -1, "error": "unknown", "data": data}

		elif otp:
			payload = {
				"query": "mutation androidVerifyOTP($authenticationProvider: AuthenticationProviderInput, $code: String!, $phoneNumber: PhoneNumber!, $vendorIdentifier: String!) { verifyOtp(input: {authenticationProvider: $authenticationProvider, code: $code, phoneNumber: $phoneNumber, vendorIdentifier: $vendorIdentifier}) { challenge accessToken refreshToken errors { path message } }}",
				"variables": {"phoneNumber": phone_number,"vendorIdentifier": self.UUID, "code": otp},
				"extensions": {}
			}

			data = self.s.post(self.API_URL, json=payload, headers=self.LOGIN_HEADERS).json()

			try: err = data['data']['verifyOtp'].get('errors')
			except: err = data.get('errors')
			if err:
				return {"status": -1, "error": err[0]['message'], "data": None}

			return {"status": 0, "error": None, "data": {"msg": "PASSCODE requested"}, "test": data}

		elif pin:
			payload = {
				"query": "mutation androidSignIn($authenticationProvider: AuthenticationProviderInput,$passcode: String!, $phoneNumber: PhoneNumber!, $vendorIdentifier: String!) { signIn(input: {authenticationProvider: $authenticationProvider,passcode: $passcode, phoneNumber: $phoneNumber, vendorIdentifier: $vendorIdentifier}) { accessToken refreshToken errors { path message } }}",
				"variables": {"passcode": pin, "phoneNumber": phone_number, "vendorIdentifier": self.UUID},
				"extensions": {}
			}

			data = self.s.post(self.API_URL, json=payload, headers=self.LOGIN_HEADERS).json()

			try: err = data['data']['signIn'].get('errors')
			except: err = data.get('errors')
			if err:
				return {"status": -1, "error": err[0]['message'], "data": None}

			self.AUTH_TOKEN = data['data']['signIn']['accessToken']
			self.LOGGED_HEADERS['authorization'] = f"Bearer {self.AUTH_TOKEN}"
			self.s.headers = self.LOGGED_HEADERS
			return {"status": 0, "error": None, "data": {"token": self.AUTH_TOKEN}}


	def fetch(self, data_to_fetch):
		payload = self.payloads['fetch'][data_to_fetch]
		data = self.s.post(self.API_URL, json=payload).json()['data']

		return {"status": 0, "error": None, "data": {"fetched": data['me']['profile']['firstName']}}

# TODO: refacto of https://github.com/ghrlt/kard-private-api


