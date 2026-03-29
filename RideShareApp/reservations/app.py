import sqlite3
import os
from flask import Flask, request
from base64 import urlsafe_b64encode as b64url_encode, urlsafe_b64decode as b64url_decode
import json
from hashlib import sha256
import hmac
import time
import requests

app = Flask(__name__)
db_name = "reservations.db"
sql_file = "reservations.sql"

db_flag = False
def create_db():
	global db_flag
	conn = sqlite3.connect(db_name)

	with open(sql_file, "r") as sql_startup:
		init_db = sql_startup.read()

	cursor = conn.cursor()
	cursor.executescript(init_db)
	conn.commit()

	# Enable foreign key constraints
	conn.execute("PRAGMA foreign_keys = ON;")
	conn.close()

	db_flag = True

def get_db():
	if not db_flag:
		create_db()
	conn = sqlite3.connect(db_name)

	# Enable foreign key constraints
	conn.execute("PRAGMA foreign_keys = ON;")
	return conn

@app.route('/', methods=(['GET']))
def index():
	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM reservations;")
	result = cursor.fetchall()
	conn.close()

	return result

@app.route('/clear', methods=(['GET']))
def clear():
	if os.path.exists(db_name):
		os.remove(db_name)
	global db_flag
	db_flag = False
	return "Database cleared"

@app.route('/reserve', methods=(['POST']))
def reserve():
	auth_header = request.headers.get('Authorization')
	if not auth_header:
		return {"status": 2}
	payload = verify_JWT(auth_header)
	if not payload:
		return {"status": 2}
	username = payload.get('username')
	listingid = request.form.get('listingid')
	if not listingid:
		return {"status": 3}
	
	conn = get_db()
	cursor = conn.cursor()

	# Check if listing exists
	GETLISTINGURL = "http://availability:5000/get_listing"
	params = {'listingid': listingid}
	response = requests.get(url = GETLISTINGURL, params = params)
	listing_data = response.json()
	if listing_data['status'] != 1:
		return {"status": 3}
	listing_info = listing_data['data']
	price = listing_info['price']

	driver = listing_info['driver']
	# Check if user has sufficient balance
	GETUSERURL = "http://user:5000/get_user"
	params = {'username': username}
	response = requests.get(url = GETUSERURL, params = params)
	user_data = response.json()
	if user_data['status'] != 1:
		return {"status": 3}
	user_info = user_data['user']
	if user_info['driver'] == 'True':
		return {"status": 3}
	
	#Check balance
	GETBALANCEURL = "http://payments:5000/view"
	jwt = get_JWT(username)
	headers = {'Authorization': jwt}
	response = requests.get(url = GETBALANCEURL, headers = headers)
	balance_data = response.json()
	if balance_data['status'] != 1:
		return {"status": 3}
	balance = float(balance_data['balance'])
	if balance < float(price):
		return {"status": 3}
	
	# Deduct price from user's balance
	jwt = get_JWT(username)
	headers = {'Authorization': jwt}
	ADDPAYMENTURL = "http://payments:5000/add"
	params = {'amount': str(float(price)* -1)}
	response = requests.post(url = ADDPAYMENTURL, data = params, headers = headers)
	payment_data = response.json()
	if payment_data['status'] != 1:
		return {"status": 3}
	
	#Add price to driver's balance
	jwt_driver = get_JWT(driver)
	headers_driver = {'Authorization': jwt_driver}
	params = {'amount': str(float(price))}
	response = requests.post(url = ADDPAYMENTURL, data = params, headers = headers_driver)
	payment_data_driver = response.json()
	if payment_data_driver['status'] != 1:
		return {"status": 3}
	
	REMOVELISTINGURL = "http://availability:5000/remove_listing"
	params = {'listingid': listingid}
	response = requests.post(url = REMOVELISTINGURL, data = params, headers = headers_driver)
	remove_data = response.json()
	if remove_data['status'] != 1:
		return {"status": 3}
	
	# Create reservation
	cursor.execute("INSERT INTO reservations (listing_id, rider_username,driver_username, price) VALUES (?, ?,?,?);", (listingid, username, driver, price))
	conn.commit()
	conn.close()
	return {"status": 1}

@app.route('/view', methods=(['GET']))
def view():
	auth_header = request.headers.get('Authorization')
	if not auth_header:
		return {"status": 2, "data": 'NULL'}
	payload = verify_JWT(auth_header)
	if not payload:
		return {"status": 2, "data": 'NULL'}
	username = payload.get('username')

	GETUSERURL = "http://user:5000/get_user"
	params = {'username': username}
	response = requests.get(url = GETUSERURL, params = params)
	user_data = response.json()
	if user_data['status'] != 1:
		return {"status": 2, "data": 'NULL'}
	
	conn = get_db()
	cursor = conn.cursor()

	isDriver = user_data['user']['driver']
	if isDriver == 'True':
		cursor.execute("SELECT * FROM reservations WHERE driver_username = ? ORDER BY reservation_id DESC;", (username,))
		result = cursor.fetchone()
		conn.close()
		if not result:
			return {"status": 2, "data": 'NULL'}
		listing_id = result[0]
		rider_username = result[1]
		price = f"{result[3]:.2f}"
		# Get driver rating
		GETUSERRATINGURL = "http://user:5000/view_rating"
		params = {'username': rider_username}
		response = requests.get(url = GETUSERRATINGURL, params = params)
		rating_data = response.json()
		if rating_data['status'] != 1:
			return {"status": 2, "data": 'NULL'}
		rating = rating_data['rating']
		return {"status": 1, "data": {"listingid": listing_id, "price": price, "user": rider_username, "rating": rating}}


	cursor.execute("SELECT * FROM reservations WHERE rider_username = ? ORDER BY reservation_id DESC;", (username,))
	result = cursor.fetchone()
	conn.close()
	if not result:
		return {"status": 2, "data": 'NULL'}
	
	listing_id = result[0]
	rider_username = result[1]
	driver_username = result[2]
	price = f"{result[3]:.2f}"

	# Get driver rating
	GETUSERRATINGURL = "http://user:5000/view_rating"
	params = {'username': driver_username}
	response = requests.get(url = GETUSERRATINGURL, params = params)
	rating_data = response.json()
	if rating_data['status'] != 1:
		return {"status": 2, "data": 'NULL'}
	rating = rating_data['rating']
	return {"status": 1, "data": {"listingid": listing_id, "price": price, "user": driver_username, "rating": rating}}

@app.route('/get_reservation', methods=(['GET']))
def get_reservation():
	driver_username = request.args.get('driver_username')
	rider_username = request.args.get('rider_username')
	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM reservations WHERE driver_username = ? AND rider_username = ? ORDER BY reservation_id DESC;", (driver_username, rider_username))
	result = cursor.fetchone()
	conn.close()
	if not result:
		return {"status": 2}
	return {"status": 1}
	

	
	

	

	
	


#Helper functions

# Password validation function
def password_validation(password, first_name, last_name, username):
	if len(password) < 8:
		return False
	if first_name.lower() in password.lower() or last_name.lower() in password.lower() or username.lower() in password.lower():
		return False
	if not any(char.isdigit() for char in password):
		return False
	if not any(char.isupper() for char in password):
		return False
	if not any(char.islower() for char in password):
		return False
	return True

# Get JWT function
def get_JWT(username):
	header = json.dumps({"alg":"HS256","typ":"JWT"}).encode("utf-8")
	payload = json.dumps({"username": username}).encode("utf-8")
	header_b64 = b64url_encode(header).decode("utf-8")
	payload_b64 = b64url_encode(payload).decode("utf-8")
	message = f"{header_b64}.{payload_b64}".encode("utf-8")
	key = open("key.txt", "rb").readline().strip()
	signature_hex = hmac.new(key, message, sha256).hexdigest()
	return f"{header_b64}.{payload_b64}.{signature_hex}"

# Verify and decode JWT function
def verify_JWT(jwt: str):
	# Verify signature
    try:
        header_b64, payload_b64, signature = jwt.split(".")
    except ValueError:
        return None

    message = f"{header_b64}.{payload_b64}".encode("utf-8")
	# Read key from file
    with open("key.txt", "rb") as f:
        key = f.readline().strip()

    expected = hmac.new(key, message, sha256).hexdigest()

	# Compare signatures
    if not hmac.compare_digest(expected, signature):
        return None

    # Parse and check header and payload
    try:
        header = json.loads(b64url_decode(header_b64).decode("utf-8"))
        payload = json.loads(b64url_decode(payload_b64).decode("utf-8"))
    except Exception:
        return None

    if header.get("alg") != "HS256" or header.get("typ") != "JWT":
        return None

    return payload










