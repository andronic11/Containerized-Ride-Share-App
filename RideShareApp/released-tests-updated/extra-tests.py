import requests
import json

# ============
# Base URLs
# ============

URLCREATEUSER = "http://127.0.0.1:9000/create_user"
URLUSERCLEAR = "http://127.0.0.1:9000/clear"
URLRATE = "http://127.0.0.1:9000/rate"
URLVIEWRATING = "http://127.0.0.1:9000/view_rating"

URLAVAILABILITY = "http://127.0.0.1:9001/listing"
URLAVAILABILITYCLEAR = "http://127.0.0.1:9001/clear"
URLGETLISTING = "http://127.0.0.1:9001/get_listing"

URLRESERVE = "http://127.0.0.1:9002/reserve"
URLRESERVECLEAR = "http://127.0.0.1:9002/clear"
URLRESERVEVIEW = "http://127.0.0.1:9002/view"

URLPAYMENTCLEAR = "http://127.0.0.1:9003/clear"

# Same JWTs as your other tests (driver jmm, passenger griffin)
JMM_JWT = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJqbW0ifQ==.02838fbb9275f0c5f5f9b734d984d683be04491cd3a8cf506016c4903bbe8b4f"
GRIFFIN_JWT = "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VybmFtZSI6ICJncmlmZmluIn0=.803e985bbf6d4da2b9f42d0de4f33539396ecf4d82b2bffde2d29adf7d36aedb"


def clear_all():
    requests.get(URLUSERCLEAR)
    requests.get(URLAVAILABILITYCLEAR)
    requests.get(URLRESERVECLEAR)
    requests.get(URLPAYMENTCLEAR)


try:
    # =======================================================
    # Test C: Passenger cannot rate driver without reservation
    # =======================================================
    clear_all()

    # Create driver jmm
    PARAMS = {
        'first_name': 'james',
        'last_name': 'mariani',
        'username': 'jmm',
        'email_address': 'j@a.com',
        'password': 'Examplepassword1',
        'driver': True,
        'deposit': '10.00',
        'salt': 'FE8x1gO+7z0B'
    }
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('C01 (create driver)')
        quit()

    # Create passenger griffin
    PARAMS = {
        'first_name': 'griffin',
        'last_name': 'klever',
        'username': 'griffin',
        'email_address': 'a@a.com',
        'password': 'Examplepassword1',
        'driver': False,
        'deposit': '10.00',
        'salt': 'K8ENdhu#nxe3'
    }
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('C02 (create passenger)')
        quit()

    # Passenger tries to rate driver with NO reservation
    headers_passenger = {'Authorization': GRIFFIN_JWT}
    RATINGPARAMS = {'username': 'jmm', 'rating': 4}
    r_rate = requests.post(URLRATE, data=RATINGPARAMS, headers=headers_passenger)
    if r_rate.json().get('status') != 2:
        print('C03 (rate without reservation should fail with status 2)')
        quit()

    # Driver's rating should still be 0.00
    r_view_rating = requests.get(URLVIEWRATING, params={'username': 'jmm'})
    data = r_view_rating.json()
    if data.get('status') != 1 or data.get('rating') != '0.00':
        print('C04 (rating for jmm should be 0.00 with no valid ratings)')
        quit()

    print('Test C Passed (cannot rate without reservation, rating remains 0.00)')

    # ======================================================
    # Test D: Multiple ratings average correctly for driver
    # ======================================================
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
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('D01 (create driver)')
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
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('D02 (create passenger)')
        quit()

    headers_driver = {'Authorization': JMM_JWT}
    headers_passenger = {'Authorization': GRIFFIN_JWT}

    # Create listing 200 at price 4.00
    ADDAVAILABILITYPARAMS = {'day': 'Monday', 'price': '4.00', 'listingid': 200}
    r_create = requests.post(URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('D03 (create availability 200)')
        quit()

    # Passenger reserves listing 200
    RESERVATIONPARAMS = {'listingid': 200}
    r_res = requests.post(URLRESERVE, data=RESERVATIONPARAMS, headers=headers_passenger)
    if r_res.json().get('status') != 1:
        print('D04 (reserve listing 200 failed)')
        quit()

    # First rating: 3
    RATINGPARAMS = {'username': 'jmm', 'rating': 3}
    r_rate = requests.post(URLRATE, data=RATINGPARAMS, headers=headers_passenger)
    if r_rate.json().get('status') != 1:
        print('D05 (first rating 3 failed)')
        quit()

    # Second rating: 5
    RATINGPARAMS = {'username': 'jmm', 'rating': 5}
    r_rate = requests.post(URLRATE, data=RATINGPARAMS, headers=headers_passenger)
    if r_rate.json().get('status') != 1:
        print('D06 (second rating 5 failed)')
        quit()

    # Average should now be (3 + 5) / 2 = 4.00
    r_view_rating = requests.get(URLVIEWRATING, params={'username': 'jmm'})
    data = r_view_rating.json()
    if data.get('status') != 1 or data.get('rating') != '4.00':
        print('D07 (average rating for jmm should be 4.00)')
        quit()

    print('Test D Passed (multiple ratings averaged correctly)')

    # ===========================================================
    # Test E: Driver can rate passenger when reservation exists
    # ===========================================================
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
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('E01 (create driver)')
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
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('E02 (create passenger)')
        quit()

    headers_driver = {'Authorization': JMM_JWT}
    headers_passenger = {'Authorization': GRIFFIN_JWT}

    # Create listing 300
    ADDAVAILABILITYPARAMS = {'day': 'Tuesday', 'price': '7.00', 'listingid': 300}
    r_create = requests.post(URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('E03 (create availability 300)')
        quit()

    # Passenger reserves listing 300
    RESERVATIONPARAMS = {'listingid': 300}
    r_res = requests.post(URLRESERVE, data=RESERVATIONPARAMS, headers=headers_passenger)
    if r_res.json().get('status') != 1:
        print('E04 (reserve listing 300 failed)')
        quit()

    # Driver rates passenger griffin with rating 2
    RATINGPARAMS = {'username': 'griffin', 'rating': 2}
    r_rate = requests.post(URLRATE, data=RATINGPARAMS, headers=headers_driver)
    if r_rate.json().get('status') != 1:
        print('E05 (driver rating passenger failed)')
        quit()

    # griffin's rating should now be 2.00
    r_view_rating = requests.get(URLVIEWRATING, params={'username': 'griffin'})
    data = r_view_rating.json()
    if data.get('status') != 1 or data.get('rating') != '2.00':
        print('E06 (rating for griffin should be 2.00)')
        quit()

    print('Test E Passed (driver can rate passenger after reservation)')

    # =======================================================
    # Test F: Same-type users (passenger->passenger) blocked
    # =======================================================
    clear_all()

    # Create jmm as PASSENGER this time
    PARAMS = {
        'first_name': 'james',
        'last_name': 'mariani',
        'username': 'jmm',
        'email_address': 'j@a.com',
        'password': 'Examplepassword1',
        'driver': False,
        'deposit': '10.00',
        'salt': 'FE8x1gO+7z0B'
    }
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('F01 (create passenger jmm)')
        quit()

    # Create griffin as PASSENGER too
    PARAMS = {
        'first_name': 'griffin',
        'last_name': 'klever',
        'username': 'griffin',
        'email_address': 'a@a.com',
        'password': 'Examplepassword1',
        'driver': False,
        'deposit': '10.00',
        'salt': 'K8ENdhu#nxe3'
    }
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('F02 (create passenger griffin)')
        quit()

    # jmm (passenger) tries to rate griffin (passenger)
    headers_jmm = {'Authorization': JMM_JWT}
    RATINGPARAMS = {'username': 'griffin', 'rating': 5}
    r_rate = requests.post(URLRATE, data=RATINGPARAMS, headers=headers_jmm)
    if r_rate.json().get('status') != 2:
        print('F03 (passenger->passenger rating should fail with status 2)')
        quit()

    print('Test F Passed (same-type rating is rejected)')

    # ============================================================
    # Test G: Reservation fails when passenger has insufficient $
    # ============================================================
    clear_all()

    # Driver jmm
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
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('G01 (create driver)')
        quit()

    # Passenger griffin with only 3.00 in account
    PARAMS = {
        'first_name': 'griffin',
        'last_name': 'klever',
        'username': 'griffin',
        'email_address': 'a@a.com',
        'password': 'Examplepassword1',
        'driver': False,
        'deposit': '3.00',
        'salt': 'K8ENdhu#nxe3'
    }
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('G02 (create low-balance passenger)')
        quit()

    headers_driver = {'Authorization': JMM_JWT}
    headers_passenger = {'Authorization': GRIFFIN_JWT}

    # Listing costs 5.00, more than passenger's balance
    ADDAVAILABILITYPARAMS = {'day': 'Wednesday', 'price': '5.00', 'listingid': 400}
    r_create = requests.post(URLAVAILABILITY, data=ADDAVAILABILITYPARAMS, headers=headers_driver)
    if r_create.json().get('status') != 1:
        print('G03 (create availability 400)')
        quit()

    # Reservation should fail with status 3 (cannot make reservation)
    RESERVATIONPARAMS = {'listingid': 400}
    r_res = requests.post(URLRESERVE, data=RESERVATIONPARAMS, headers=headers_passenger)
    if r_res.json().get('status') != 3:
        print('G04 (reservation should fail for insufficient funds)')
        quit()

    # Listing should still exist
    r_get = requests.get(URLGETLISTING, params={'listingid': 400})
    if r_get.json().get('status') != 1:
        print('G05 (listing 400 should still be available after failed reservation)')
        quit()

    print('Test G Passed (insufficient funds prevents reservation, listing remains)')

    # =======================================================
    # Test H: /view returns NULL for users with no reservation
    # =======================================================
    clear_all()

    # Driver jmm
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
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('H01 (create driver)')
        quit()

    # Passenger griffin
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
    r = requests.post(URLCREATEUSER, data=PARAMS)
    if r.json().get('status') != 1:
        print('H02 (create passenger)')
        quit()

    headers_driver = {'Authorization': JMM_JWT}
    headers_passenger = {'Authorization': GRIFFIN_JWT}

    # No listings created, no reservations made

    # Passenger view
    r_view = requests.get(URLRESERVEVIEW, headers=headers_passenger)
    data = r_view.json()
    if data.get('status') != 2 or data.get('data') != 'NULL':
        print('H03 (passenger /view should return status 2 and data NULL with no reservation)')
        quit()

    # Driver view
    r_view = requests.get(URLRESERVEVIEW, headers=headers_driver)
    data = r_view.json()
    if data.get('status') != 2 or data.get('data') != 'NULL':
        print('H04 (driver /view should return status 2 and data NULL with no reservation)')
        quit()

    print('Test H Passed (/view returns status 2 and data NULL with no reservations)')

    print('All edge case tests passed')

except Exception as e:
    print('Test Failed with exception:', e)
