import requests
import json
import os

try:
	print('Starting Test')
	URLCREATEUSER = "http://127.0.0.1:9000/create_user"
	URLLOGIN = "http://127.0.0.1:9000/login"
	URLRATE = "http://127.0.0.1:9000/rate"
	URLAVAILABILITY = "http://127.0.0.1:9001/listing"
	URLAVAILABILITYSEARCH = "http://127.0.0.1:9001/search"
	URLRESERVE = "http://127.0.0.1:9002/reserve"
	URLRESERVEVIEW = "http://127.0.0.1:9002/view"
	URLPAYMENTADD = "http://127.0.0.1:9003/add"
	URLVIEWBALANCE = "http://127.0.0.1:9003/view"

	URLUSERclear = "http://127.0.0.1:9000/clear"
	URLAVAILABILITYclear = "http://127.0.0.1:9001/clear"
	URLRESERVEclear = "http://127.0.0.1:9002/clear"
	URLPAYMENTclear = "http://127.0.0.1:9003/clear"
	r_clear = requests.get(url = URLUSERclear)
	r_clear = requests.get(url = URLAVAILABILITYclear)
	r_clear = requests.get(url = URLRESERVEclear)
	r_clear = requests.get(url = URLPAYMENTclear)

	print('Creating Users')
	PARAMS = {'first_name': 'james', 'last_name': 'mariani', 'username': 'jmm', 'email_address': 'j@a.com', 'password': 'Examplepassword1', 'driver': True,'deposit': '1.00','salt': 'FE8x1gO+7z0B'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	print('Create User Response:', data)
	if data['status'] != 1:
		print(0)
		quit()
	
	PARAMS = {'first_name': 'griffin', 'last_name': 'klever', 'username': 'griffin', 'email_address': 'a@a.com', 'password': 'Examplepassword1', 'driver': False, 'deposit': '10.00', 'salt': 'K8ENdhu#nxe3'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	print('Create User Response:', data)
	if data['status'] != 1:
		print('01')
		quit()

	PARAMS = {'first_name': 'guy', 'last_name': 'fieri', 'username': 'fieri', 'email_address': 'g@g.com', 'password': 'Examplepassword1', 'driver': True, 'deposit': '5.50', 'salt': 'xaxkRSzNPnP4'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	print('Create User Response:', data)
	if data['status'] != 1:
		print('02')
		quit()

	print('Creating Availabilities')
	ADDAVAILABILITYPARAMS = {'day': 'Monday', 'price': '4.00', 'listingid': 123}
	r_create_availability = requests.post(url = URLAVAILABILITY, data = ADDAVAILABILITYPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'})
	create_availability_data = r_create_availability.json()
	print('Create Availability Response:', create_availability_data)
	ADDAVAILABILITYPARAMS = {'day': 'Tuesday', 'price': '4.50', 'listingid': 234}
	r_create_availability = requests.post(url = URLAVAILABILITY, data = ADDAVAILABILITYPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'})
	create_availability_data = r_create_availability.json()
	print('Create Availability Response:', create_availability_data)
	ADDAVAILABILITYPARAMS = {'day': 'Monday', 'price': '5.00', 'listingid': 345}
	r_create_availability = requests.post(url = URLAVAILABILITY, data = ADDAVAILABILITYPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'})
	create_availability_data = r_create_availability.json()
	print('Create Availability Response:', create_availability_data)

	SEARCHPARAMS = {'day': 'Monday'}
	r_search_availability = requests.get(url = URLAVAILABILITYSEARCH, params = SEARCHPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJncmlmZmluIn0=.803e985bbf6d4da2b9f42d0de4f33539396ecf4d82b2bffde2d29adf7d36aedb'})
	search_availability_data = r_search_availability.json()
	
	expected_dict = {'status': 1, 'data': [{'listingid': 345, 'price': '5.00', 'driver': 'jmm', 'rating': '0.00'}, {'listingid': 123, 'price': '4.00', 'driver': 'jmm', 'rating': '0.00'}]}
	print('Expected:', expected_dict)
	print('Received:', search_availability_data)

	if len(expected_dict['data']) != len(search_availability_data['data']):
		print(1)
		quit()
	for x in expected_dict['data']:
		found = False
		for y in search_availability_data['data']:
			if len(x) != len(y):
				print(2)
				quit()
			if (y['listingid'] == x['listingid']) and (y['price'] == x['price']) and (y['driver'] == x['driver']) and (y['rating'] == x['rating']):
				found = True
				print('Found match:', y)
				break
		if not found:
			print(3)
			quit()

	print('Test Passed')

except:
	print('Test Failed')

