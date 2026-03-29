import requests
import json

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

# Same JWTs you used in your script (driver=jmm, passenger=griffin)
JMM_JWT = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f"
GRIFFIN_JWT = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJncmlmZmluIn0=.803e985bbf6d4da2b9f42d0de4f33539396ecf4d82b2bffde2d29adf7d36aedb"


def clear_all():
    requests.get(URLUSERclear)
    requests.get(URLAVAILABILITYclear)
    requests.get(URLRESERVEclear)
    requests.get(URLPAYMENTclear)

def test_passenger_gets_latest_reservation():
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
    data = r.json()
    if data['status'] != 1:
        print('T1-01 (create driver)')
        return

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
    data = r.json()
    if data['status'] != 1:
        print('T1-02 (create passenger)')
        return

    # Create two availabilities for jmm
    print('T1: Creating Availabilities')
    headers_driver = {'Authorization': JMM_JWT}

    # First listing
    ADDAVAILABILITYPARAMS = {'day': 'Monday', 'price': '4.00', 'listingid': 123}
    r_create = requests.post(url=URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('T1-03 (create availability 123)')
        return

    # Second listing (later reservation should be this one)
    ADDAVAILABILITYPARAMS = {'day': 'Tuesday', 'price': '7.50', 'listingid': 234}
    r_create = requests.post(url=URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('T1-04 (create availability 234)')
        return

    # Passenger reserves first listing (123)
    headers_passenger = {'Authorization': GRIFFIN_JWT}
    RESERVATIONPARAMS = {'listingid': 123}
    r_res = requests.post(url=URLRESERVE, data=RESERVATIONPARAMS, headers=headers_passenger)
    if r_res.json().get('status') != 1:
        print('T1-05 (reserve 123)')
        return

    # Passenger reserves second listing (234) → this should now be the "latest"
    RESERVATIONPARAMS = {'listingid': 234}
    r_res = requests.post(url=URLRESERVE, data=RESERVATIONPARAMS, headers=headers_passenger)
    if r_res.json().get('status') != 1:
        print('T1-06 (reserve 234)')
        return

    # View as passenger: should return listingid 234
    print('T1: Viewing reservations as passenger (expect listing 234)')
    r_view = requests.get(url=URLRESERVEVIEW, headers=headers_passenger)
    view_data = r_view.json()
    print('T1 view response:', view_data)

    if view_data.get('status') != 1:
        print('T1-07 (status not 1)')
        return

    data = view_data['data']
    expected_listing = 234
    expected_price = '7.50'

    if data['listingid'] != expected_listing or data['price'] != expected_price or data['user'] != 'jmm':
        print('T1-08 (wrong latest reservation)')
        return

    print('T1 Passed (passenger gets latest reservation)')


def test_driver_gets_latest_reservation():
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
        print('T2-01 (create driver)')
        return

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
        print('T2-02 (create passenger)')
        return

    headers_driver = {'Authorization': JMM_JWT}
    headers_passenger = {'Authorization': GRIFFIN_JWT}

    # Two availabilities for jmm
    ADDAVAILABILITYPARAMS = {'day': 'Monday', 'price': '4.00', 'listingid': 123}
    r_create = requests.post(url=URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('T2-03 (create availability 123)')
        return

    ADDAVAILABILITYPARAMS = {'day': 'Tuesday', 'price': '7.50', 'listingid': 234}
    r_create = requests.post(url=URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('T2-04 (create availability 234)')
        return

    # Passenger reserves both in order: 123 then 234
    RESERVATIONPARAMS = {'listingid': 123}
    r_res = requests.post(url=URLRESERVE, data=RESERVATIONPARAMS, headers=headers_passenger)
    if r_res.json().get('status') != 1:
        print('T2-05 (reserve 123)')
        return

    RESERVATIONPARAMS = {'listingid': 234}
    r_res = requests.post(url=URLRESERVE, data=RESERVATIONPARAMS, headers=headers_passenger)
    if r_res.json().get('status') != 1:
        print('T2-06 (reserve 234)')
        return

    # Now view as driver: should see latest (listing 234)
    print('T2: Viewing reservations as driver (expect listing 234)')
    r_view = requests.get(url=URLRESERVEVIEW, headers=headers_driver)
    view_data = r_view.json()
    print('T2 view response:', view_data)

    if view_data.get('status') != 1:
        print('T2-07 (status not 1)')
        return

    data = view_data['data']
    expected_listing = 234
    expected_price = '7.50'

    if data['listingid'] != expected_listing or data['price'] != expected_price or data['user'] != 'griffin':
        print('T2-08 (wrong latest reservation)')
        return

    print('T2 Passed (driver gets latest reservation)')


if __name__ == "__main__":
    try:
        test_passenger_gets_latest_reservation()
        test_driver_gets_latest_reservation()
        print("All latest-reservation tests passed")
    except Exception as e:
        print("Test Failed with exception:", e)

