import requests
import json
from flask import send_file

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
				"id": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { id }","variables":{},"extensions":{}},
				"username": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { username }}","variables":{},"extensions":{}},
				"firstname": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { firstName }}","variables":{},"extensions":{}},
				"lastname": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { lastName }}","variables":{},"extensions":{}},
				"age": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { age }}","variables":{},"extensions":{}},
				"birth-date": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { birthday }}","variables":{},"extensions":{}},
				"birth-place": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { placeOfBirth }}","variables":{},"extensions":{}},
				"adress": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { shippingAddress { fullAddress } }}","variables":{},"extensions":{}},
				"email": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { email }","variables":{},"extensions":{}},
				"tel": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { phoneNumber }","variables":{},"extensions":{}},
				"acc-type": {"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { type }","variables": {},"extensions": {}},
				"subscription-status": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { subscription { status } }","variables":{},"extensions":{}},
				"subscription-price": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { subscription { plan { price { value }} } }","variables":{},"extensions":{}},
				"balance": {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { bankAccount { balance { value } }}","variables":{},"extensions":{}}
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
			"accept-language": "fr"
		}


		if self.AUTH_TOKEN:
			self.force_login()

	def force_login(self) -> None:
		self.s.headers = self.LOGGED_HEADERS

		self.user_id = self.fetch('id')['data']['fetched']


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

			self.user_id = self.fetch('id')['data']['fetched']

			return {"status": 0, "error": None, "data": {"token": self.AUTH_TOKEN}}


	def fetch(self, data_to_fetch: str) -> dict:
		payload = self.payloads['fetch'][data_to_fetch]
		data = self.s.post(self.API_URL, json=payload).json()

		# More elegant solution
		# than parsing the payload to know which key we requested?
		def flatten(dict_, base=()):
			for k in dict_:
				if isinstance(dict_[k], dict):
					return flatten(dict_[k], base+(k,))
				else:
					return (base + (k, dict_[k]))

		return {"status": 0, "error": None, "data": {"fetched": flatten(data)[-1]}}



	def postReq(self, payload, json=True):
		r = self.s.post(self.API_URL, json=payload)
		if json:
			return r.json()
		return r

	def getFullName(self):
		payload = {"query": "query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { profile { firstName lastName }}","variables":{},"extensions":{}}
		r = self.postReq(payload)

		f,l = r['data']['me']['profile'].values()

		return {"status": 0, "data": f+' '+l}

	def getVaults(self):
		payload = {"query":"query androidListVault { me { vaults { ... Vault_VaultParts } }}\n\nfragment Vault_VaultParts on Vault { id name emoji { name unicode } color goal { value } balance { value } }","variables":{},"extensions":{}}
		r = self.postReq(payload)

		# ordering by amount
		vaults = sorted(r['data']['me']['vaults'], key=lambda d: d['balance']['value']) 

		return {"status": 0, "data": {"vaults": vaults}}

	def getTransactions(self, maxi: str|int=100, cursor: str=None):
		if maxi:
			try: maxi = int(maxi)
			except ValueError: return {"status": -1, "error": "Wrong value supplied for \"maxi\" argument."}

		# TODO: cursor implementation

		payload = {"query":"query androidTransactions($first: Int, $after: String) { me { typedTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title status visibility amount { value currency { symbol } } category { name color image { url } } processedAt ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } } } typedFriendsTransactions(first: $first, after: $after) { pageInfo { endCursor hasNextPage } nodes { __typename id title category { name image { url } } processedAt user { id firstName lastName username avatar { url } } ...on P2pTransaction { triggeredBy { id firstName lastName username avatar { url } } reason } ...on ClosingAccountTransaction { moneyAccount { ... Vault_VaultMiniParts } } ...on InternalTransferTransaction { moneyAccount { ... Vault_VaultMiniParts } } ... on MoneyLinkTransaction { from message } } } }}\n\nfragment Vault_VaultMiniParts on Vault { name color emoji { name unicode }}","variables":{"numberOfComments": 5,"first": maxi, "after": cursor},"extensions":{}}
		r = self.postReq(payload)

		return {"status": 0, "error": None, "data": r['data']['me']['typedTransactions']['nodes']}
	
	def getLimits(self):

		p1 = {"query": "query androidGetSpendingLimit { me { family { memberships { member { id transactionLimits { id amount { value currency { symbol } } recurrence transactionType } } } } }}","variables": {},"extensions": {}}
		p2 = {"query": "query androidGetTransactionAuthorization { me { family { memberships { member { id transactionAuthorizations { authorizationType isAuthorized } } } } }}","variables": {},"extensions": {}}
		p3 = {"query": "query androidGetSpendingLimit { me { family { memberships { member { id currentSpendings { monthlyPos { value } weeklyPos { value } weeklyAtm { value } monthlyAtm { value } } } } } }}","variables": {},"extensions": {}}
		p4 = {"query": "query androidGetLegalSpendingLimit { me { family { memberships { member { id legalSpendingLimits { monthlyPos { value } weeklyPos { value } weeklyAtm { value } monthlyAtm { value } } } } } }}","variables": {},"extensions": {}}

		# Tried to make them fit in one request, unable to do so I guess?
		r1 = self.postReq(p1)['data']
		r2 = self.postReq(p2)['data']
		r3 = self.postReq(p3)['data']
		r4 = self.postReq(p4)['data']


		r = {
			"authorization": r2['me']['family']['memberships'],
			"spendable": r1['me']['family']['memberships'],
			"spent": r3['me']['family']['memberships'],
			"legal": r4['me']['family']['memberships']
		}

		r['me'] = [r['authorization'][i] for i in range(len(r['authorization'])) if r['authorization'][i]['member']['id'] == self.user_id]
		r['me'] += [r['spendable'][i] for i in range(len(r['spendable'])) if r['spendable'][i]['member']['id'] == self.user_id]
		r['me'] += [r['spent'][i] for i in range(len(r['spent'])) if r['spent'][i]['member']['id'] == self.user_id]
		r['me'] += [r['legal'][i] for i in range(len(r['legal'])) if r['legal'][i]['member']['id'] == self.user_id]

		r = r['me'][0]['member'] | r['me'][1]['member'] | r['me'][2]['member'] | r['me'][3]['member']

		return {"status": 0, "error": None, "data": r}

	def getMastercardInfos(self):
		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts }}}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}","variables":{},"extensions":{}}
		r = self.postReq(payload)

		for card in r['data']['me']['cards']['nodes']:
			if card['__typename'] == "PhysicalCard":
				break

		return {"status": 0, "error": None, "data": card}

	def getMastercardPin(self, card_id: str):
		payload = {"query": "query androidUrlToGetPin($cardId: ID!) { urlToGetPin(cardId: $cardId) { url }}","variables": {"cardId": card_id},"extensions": {}}
		r = self.postReq(payload)

		r = self.s.get(r['data']['urlToGetPin']['url']).json()

		return {"status": 0, "error": None, "data": {"pin": r['card_pin']}}
	
	def getVisaInfos(self):
		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { cards { nodes { ... Card_CardParts }}}\n\nfragment Card_CardParts on Card { __typename id activatedAt customText name visibleNumber blocked ... on PhysicalCard { atm contactless swipe online design }}","variables":{},"extensions":{}}
		r = self.postReq(payload)

		for card in r['data']['me']['cards']['nodes']:
			if card['__typename'] == "VirtualCard":
				break


		payload = {
			"query": "query androidUrlToGetPan($cardId: ID!) { urlToGetPan(cardId: $cardId) { url }}",
			"variables": {
			    "cardId": card['id']
  			},
  			"extensions": {}
		}
		r = self.postReq(payload)
		
		headers = self.s.headers
		try: del headers['content-length'] #THIS is the headers that made the request goes infinite
		except: pass
		r = self.s.get(r['data']['urlToGetPan']['url'], headers=headers).json()

		x = r['card_pan']
		card['card_number'] = ' '.join([x[0:4],x[4:8],x[8:12],x[12:16]])
		card['cvv'] = r['card_cvc2']
		card['expiration_date'] = '/'.join(reversed([x[-2:] for x in r['card_exp_date'].split('-')[:2]]))

		return {"status": 0, "error": None, "data": card}

	def getRibInfos(self):
		payload = {"query":"query androidMe { me { ... Me_MeParts }}\n\nfragment Me_MeParts on Me { bankAccount { id iban bic user { firstName lastName } }}","variables":{},"extensions":{}}
		r = self.postReq(payload)

		r['data']['me']['bankAccount']['download_pdf'] = f"https://api.kard.eu/bank_account_details/{r['data']['me']['bankAccount']['id']}.pdf"
		return {"status": 0, "error": None, "data": r['data']['me']['bankAccount']}

	def downloadRib(self):
		headers = self.s.headers
		try: del headers['content-length'] #THIS is the headers that made the request goes infinite
		except: pass
		return self.s.get(self.getRibInfos()['data']['download_pdf'], headers=headers).content


	def getKycStatus(self):
		payload = ""
		r = self.postReq(payload)




	def createVault(self, name: str, goal: str|int):
		payload = {
			"query": "mutation androidCreateVault($goal: AmountInput!, $name: Name!) { createVault(input: {goal: $goal, name: $name}) { errors { message path } vault { id } }}",
			"variables": {"goal": {"value": float(str(goal)), "currency": "EUR"}, "name": name},
			"extensions":{}
		}
		r = self.postReq(payload)


		return {"status": 0, "error": None, "data": r}





# TODO: refacto of https://github.com/ghrlt/kard-private-api


