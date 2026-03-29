import requests
import json
import os

try:
	
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


	PARAMS = {'first_name': 'james', 'last_name': 'mariani', 'username': 'jmm', 'email_address': 'j@a.com', 'password': 'Examplepassword1', 'driver': True,'deposit': '1.00','salt': 'FE8x1gO+7z0B'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		print('01')
		quit()
	
	PARAMS = {'first_name': 'griffin', 'last_name': 'klever', 'username': 'griffin', 'email_address': 'a@a.com', 'password': 'Examplepassword1', 'driver': False, 'deposit': '10.00', 'salt': 'K8ENdhu#nxe3'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		print('02')
		quit()

	PARAMS = {'first_name': 'guy', 'last_name': 'fieri', 'username': 'fieri', 'email_address': 'g@g.com', 'password': 'Examplepassword1', 'driver': True, 'deposit': '5.50', 'salt': 'xaxkRSzNPnP4'}
	r = requests.post(url = URLCREATEUSER, data = PARAMS)
	data = r.json()
	if data['status'] != 1:
		print('03')
		quit()

	print('Creating Availabilities')
	ADDAVAILABILITYPARAMS = {'day': 'Monday', 'price': '4.00', 'listingid': 123}
	r_create_availability = requests.post(url = URLAVAILABILITY, data = ADDAVAILABILITYPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'})
	create_availability_data = r_create_availability.json()

	ADDAVAILABILITYPARAMS = {'day': 'Tuesday', 'price': '4.50', 'listingid': 234}
	r_create_availability = requests.post(url = URLAVAILABILITY, data = ADDAVAILABILITYPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'})
	create_availability_data = r_create_availability.json()

	ADDAVAILABILITYPARAMS = {'day': 'Monday', 'price': '15.00', 'listingid': 345}
	r_create_availability = requests.post(url = URLAVAILABILITY, data = ADDAVAILABILITYPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'})
	create_availability_data = r_create_availability.json()

	RESERVATIONPARAMS = {'listingid': 123}
	r_reservation = requests.post(url = URLRESERVE, data = RESERVATIONPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJncmlmZmluIn0=.803e985bbf6d4da2b9f42d0de4f33539396ecf4d82b2bffde2d29adf7d36aedb'})
	reservation_data = r_reservation.json()

	RATINGPARAMS = {'username': 'jmm', 'rating': 3}
	r_rate = requests.post(url = URLRATE, data = RATINGPARAMS, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJncmlmZmluIn0=.803e985bbf6d4da2b9f42d0de4f33539396ecf4d82b2bffde2d29adf7d36aedb'})
	reservation_data = r_reservation.json()

	print('Viewing Reservations')
	r_view = requests.get(url = URLRESERVEVIEW, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJncmlmZmluIn0=.803e985bbf6d4da2b9f42d0de4f33539396ecf4d82b2bffde2d29adf7d36aedb'})
	view_data = r_view.json()
	print('View Reservation Response:', view_data)
	expected_dict = {'status': 1, 'data': {'listingid': 123, 'price': '4.00', 'user': 'jmm', 'rating': '3.00'}}
	print(view_data)
	if len(expected_dict['data']) != len(view_data['data']):
		print('04')
		quit()
	if (expected_dict['data']['listingid'] != view_data['data']['listingid']) or (expected_dict['data']['price'] != view_data['data']['price']) or (expected_dict['data']['user'] != view_data['data']['user']) or (expected_dict['data']['rating'] != view_data['data']['rating']):
		print('05')
		quit()
	print('Passed first view')
	print('Viewing Reservations for another user')

	r_view = requests.get(url = URLRESERVEVIEW, headers={'Authorization': 'eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f'})
	view_data = r_view.json()
	print('View Reservation Response:', view_data)
	expected_dict = {'status': 1, 'data': {'listingid': 123, 'price': '4.00', 'user': 'griffin', 'rating': '0.00'}}

	if len(expected_dict['data']) != len(view_data['data']):
		print('06')
		quit()
	if (expected_dict['data']['listingid'] != view_data['data']['listingid']) or (expected_dict['data']['price'] != view_data['data']['price']) or (expected_dict['data']['user'] != view_data['data']['user']) or (expected_dict['data']['rating'] != view_data['data']['rating']):
		print('07')
		quit()


	print('Test Passed')

except:
	print('Test Failed')

