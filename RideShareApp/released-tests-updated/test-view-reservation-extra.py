import requests
import json

# Base URLs
URLCREATEUSER = "http://127.0.0.1:9000/create_user"
URLUSERCLEAR = "http://127.0.0.1:9000/clear"

URLAVAILABILITY = "http://127.0.0.1:9001/listing"
URLAVAILABILITYCLEAR = "http://127.0.0.1:9001/clear"
URLGETLISTING = "http://127.0.0.1:9001/get_listing"

URLRESERVE = "http://127.0.0.1:9002/reserve"
URLRESERVECLEAR = "http://127.0.0.1:9002/clear"

URLPAYMENTADD = "http://127.0.0.1:9003/add"
URLPAYMENTCLEAR = "http://127.0.0.1:9003/clear"

# Same JWTs you used earlier in your tests (driver jmm, passenger griffin)
JMM_JWT = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f"
GRIFFIN_JWT = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJncmlmZmluIn0=.803e985bbf6d4da2b9f42d0de4f33539396ecf4d82b2bffde2d29adf7d36aedb"


def clear_all():
    requests.get(URLUSERCLEAR)
    requests.get(URLAVAILABILITYCLEAR)
    requests.get(URLRESERVECLEAR)
    requests.get(URLPAYMENTCLEAR)


try:
    # ============================
    # Test A: Single listing removed
    # ============================
    clear_all()

    # Create driver jmm
    PARAMS = {
        'first_name': 'james',
        'last_name': 'mariani',
        'username': 'jmm',
        'email_address': 'j@a.com',
        'password': 'Examplepassword1',
        'driver': True,
        'deposit': '50.00',
        'salt': 'FE8x1gO+7z0B'
    }
    r = requests.post(url=URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('A01 (create driver)')
        quit()

    # Create passenger griffin
    PARAMS = {
        'first_name': 'griffin',
        'last_name': 'klever',
        'username': 'griffin',
        'email_address': 'a@a.com',
        'password': 'Examplepassword1',
        'driver': False,
        'deposit': '50.00',
        'salt': 'K8ENdhu#nxe3'
    }
    r = requests.post(url=URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('A02 (create passenger)')
        quit()

    # Driver creates one availability listing (id 111)
    headers_driver = {'Authorization': JMM_JWT}
    ADDAVAILABILITYPARAMS = {'day': 'Monday', 'price': '5.00', 'listingid': 111}
    r_create = requests.post(url=URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('A03 (create availability 111)')
        quit()

    # Sanity check: listing 111 exists before reservation
    r_get = requests.get(url=URLGETLISTING, params={'listingid': 111})
    data = r_get.json()
    if data.get('status') != 1:
        print('A04 (listing 111 not found before reservation)')
        quit()

    # Passenger reserves listing 111
    headers_passenger = {'Authorization': GRIFFIN_JWT}
    RESERVATIONPARAMS = {'listingid': 111}
    r_res = requests.post(url=URLRESERVE, data=RESERVATIONPARAMS, headers=headers_passenger)
    if r_res.json().get('status') != 1:
        print('A05 (reserve 111 failed)')
        quit()

    # Now listing 111 should be gone from availability
    r_get = requests.get(url=URLGETLISTING, params={'listingid': 111})
    data = r_get.json()
    # We only know that "status != 1" means it’s not available anymore
    if data.get('status') == 1:
        print('A06 (listing 111 still available after reservation)')
        quit()

    print('Test A Passed (single listing removed after reservation)')

    # =========================================
    # Test B: Only reserved listing is removed
    # =========================================
    clear_all()

    # Create driver jmm again
    PARAMS = {
        'first_name': 'james',
        'last_name': 'mariani',
        'username': 'jmm',
        'email_address': 'j@a.com',
        'password': 'Examplepassword1',
        'driver': True,
        'deposit': '50.00',
        'salt': 'FE8x1gO+7z0B'
    }
    r = requests.post(url=URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('B01 (create driver)')
        quit()

    # Create passenger griffin again
    PARAMS = {
        'first_name': 'griffin',
        'last_name': 'klever',
        'username': 'griffin',
        'email_address': 'a@a.com',
        'password': 'Examplepassword1',
        'driver': False,
        'deposit': '50.00',
        'salt': 'K8ENdhu#nxe3'
    }
    r = requests.post(url=URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('B02 (create passenger)')
        quit()

    headers_driver = {'Authorization': JMM_JWT}
    headers_passenger = {'Authorization': GRIFFIN_JWT}

    # Two listings: 123 and 234
    ADDAVAILABILITYPARAMS = {'day': 'Monday', 'price': '4.00', 'listingid': 123}
    r_create = requests.post(url=URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('B03 (create availability 123)')
        quit()

    ADDAVAILABILITYPARAMS = {'day': 'Tuesday', 'price': '6.00', 'listingid': 234}
    r_create = requests.post(url=URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('B04 (create availability 234)')
        quit()

    # Sanity check both exist
    if requests.get(URLGETLISTING, params={'listingid': 123}).json().get('status') != 1:
        print('B05 (listing 123 missing before reservation)')
        quit()
    if requests.get(URLGETLISTING, params={'listingid': 234}).json().get('status') != 1:
        print('B06 (listing 234 missing before reservation)')
        quit()

    # Reserve only listing 123
    RESERVATIONPARAMS = {'listingid': 123}
    r_res = requests.post(url=URLRESERVE, data=RESERVATIONPARAMS, headers=headers_passenger)
    if r_res.json().get('status') != 1:
        print('B07 (reserve 123 failed)')
        quit()

    # After reservation: 123 should be gone...
    if requests.get(URLGETLISTING, params={'listingid': 123}).json().get('status') == 1:
        print('B08 (listing 123 still available after reservation)')
        quit()

    # ...but 234 should still be available
    if requests.get(URLGETLISTING, params={'listingid': 234}).json().get('status') != 1:
        print('B09 (listing 234 was incorrectly removed)')
        quit()

    print('Test B Passed (only reserved listing removed)')

    print('Availability removal tests passed')

except Exception as e:
    print('Test Failed with exception:', e)
