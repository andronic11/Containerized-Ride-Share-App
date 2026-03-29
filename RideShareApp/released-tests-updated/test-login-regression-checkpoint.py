import requests
import json
import os

try:
	
	URLCREATEUSER = "http://127.0.0.1:9000/create_user"
	URLLOGIN = "http://127.0.0.1:9000/login"
	URLGET = "http://127.0.0.1:9000/"
	#URLRATE = "http://127.0.0.1:9000/rate"
	#URLAVAILABILITY = "http://127.0.0.1:9001/listing"
	#URLAVAILABILITYSEARCH = "http://127.0.0.1:9001/search"
	#URLRESERVE = "http://127.0.0.1:9002/reserve"
	#URLRESERVEVIEW = "http://127.0.0.1:9002/view"
	#URLPAYMENTADD = "http://127.0.0.1:9003/add"
	#URLVIEWBALANCE = "http://127.0.0.1:9003/view"

	URLUSERclear = "http://127.0.0.1:9000/clear"
	URLAVAILABILITYclear = "http://127.0.0.1:9001/clear"
	URLRESERVEclear = "http://127.0.0.1:9002/clear"
	URLPAYMENTclear = "http://127.0.0.1:9003/clear"
	r_clear = requests.get(url = URLUSERclear)
	r_clear = requests.get(url = URLAVAILABILITYclear)
	r_clear = requests.get(url = URLRESERVEclear)
	r_clear = requests.get(url = URLPAYMENTclear)


	PARAMS = {'first_name': 'james', 'last_name': 'mariani', 'username': 'jmm', 'email_address': 'j@a.com', 'password': 'Examplepassword1', 'driver': True,'deposit': '1.00','salt': 'FE8x1gO+7z0B'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		print('1')
		quit()
	
	PARAMS = {'first_name': 'griffin', 'last_name': 'klever', 'username': 'griffin', 'email_address': 'a@a.com', 'password': 'Examplepassword1', 'driver': False, 'deposit': '10.00', 'salt': 'K8ENdhu#nxe3'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		print('2')
		quit()

	PARAMS = {'first_name': 'guy', 'last_name': 'fieri', 'username': 'fieri', 'email_address': 'g@g.com', 'password': 'Examplepassword1', 'driver': True, 'deposit': '5.50', 'salt': 'xaxkRSzNPnP4'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		print('3')
		quit()

	LOGINPARAMS = {'username': 'jmm', 'password': 'Examplepassword1'}
	r_login = requests.post(url = URLLOGIN, data = LOGINPARAMS)
	login_data = r_login.json()

	solution = {"status": 1, "jwt": 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'}
	for key in solution:
		if solution[key] != login_data[key]:
			print('4')
			print(login_data)
			quit()
	
	LOGINPARAMS = {'username': 'griffin', 'password': 'Examplepassword1'}
	r_login = requests.post(url = URLLOGIN, data = LOGINPARAMS)
	login_data = r_login.json()

	solution = {"status": 1, "jwt": 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJncmlmZmluIn0=.803e985bbf6d4da2b9f42d0de4f33539396ecf4d82b2bffde2d29adf7d36aedb'}
	for key in solution:
		if solution[key] != login_data[key]:
			print('5')
			quit()

	LOGINPARAMS = {'username': 'fieri', 'password': 'Examplepassword1'}
	r_login = requests.post(url = URLLOGIN, data = LOGINPARAMS)
	login_data = r_login.json()

	solution = {"status": 1, "jwt": 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJmaWVyaSJ9.2388b903ac10c4217a82cbed5e8d4a0b985646aa6ceda028245acdd50ee0d558'}
	for key in solution:
		if solution[key] != login_data[key]:
			print('6')
			quit()

	print('Test Passed')

except:
	print('Test Failed')

