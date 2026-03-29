import sqlite3
import os
from flask import Flask, request
from base64 import urlsafe_b64encode as b64url_encode, urlsafe_b64decode as b64url_decode
import json
from hashlib import sha256
import hmac
import requests

app = Flask(__name__)
db_name = "availability.db"
sql_file = "availability.sql"

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
	cursor.execute("SELECT * FROM availability;")
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

@app.route('/listing', methods=(['POST']))
def listing():
	#Get parameters
	day = request.form.get('day')
	price = request.form.get('price')
	listingid = request.form.get('listingid')

	jwt_token = request.headers.get('Authorization')
	payload = verify_JWT(jwt_token)
	if not payload:
		return json.dumps({"status": 2})
	driver = payload['username']

	#Get users URL
	URLGETUSERS = "http://user:5000/get_user"
	r_get_users = requests.get(url = URLGETUSERS, params = {'username':driver})
	resp_json = r_get_users.json()

	if resp_json.get("status") != 1:
		return json.dumps({"status": 2})

	user_data = resp_json.get("user")

	#Check that user is driver
	if user_data.get('driver') != 'True':
		return json.dumps({"status": 2})
	
	#Insert availability into database
	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("INSERT INTO availability (listing_id, dayOfWeek, price, driver_username) VALUES (?, ?, ?, ?);", (listingid, day, price, driver))
	conn.commit()
	conn.close()
	return json.dumps({"status": 1})

@app.route('/search', methods=(['GET']))
def search():
	day = request.args.get('day')

	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT listing_id, dayOfWeek, price, driver_username FROM availability WHERE dayOfWeek = ?;", (day,))
	result = cursor.fetchall()
	conn.close()

	availability_list = []
	for row in result:
		#Get user rating
		URLGETUSERRATING = "http://user:5000/view_rating"
		r_get_users = requests.get(url = URLGETUSERRATING, params = {'username':row[3]})
		resp_json = r_get_users.json()

		if resp_json.get("status") != 1:
			return json.dumps({"status": 2})
		user_rating = resp_json.get("rating")

		availability = {
			"listingid": row[0],
			"price": f"{row[2]:.2f}",
			"driver": row[3],
			"rating": user_rating
		}
		availability_list.append(availability)

	return json.dumps({"status": 1, "data": availability_list})

@app.route('/get_listing', methods=(['GET']))
def get_listing():
	listingid = request.args.get('listingid')

	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT listing_id, dayOfWeek, price, driver_username FROM availability WHERE listing_id = ?;", (listingid,))
	result = cursor.fetchall()
	conn.close()

	if not result:
		return json.dumps({"status": 2})

	row = result[0]

	#Get user rating
	URLGETUSERRATING = "http://user:5000/view_rating"
	r_get_users = requests.get(url = URLGETUSERRATING, params = {'username':row[3]})
	resp_json = r_get_users.json()

	if resp_json.get("status") != 1:
		return json.dumps({"status": 2})
	user_rating = resp_json.get("rating")

	availability = {
		"listingid": row[0],
		"day": row[1],
		"price": f"{row[2]:.2f}",
		"driver": row[3],
		"rating": user_rating
	}

	return json.dumps({"status": 1, "data": availability})

@app.route('/remove_listing', methods=(['POST']))
def remove_listing():
	listingid = request.form.get('listingid')

	jwt_token = request.headers.get('Authorization')
	payload = verify_JWT(jwt_token)
	if not payload:
		return json.dumps({"status": 2})
	driver = payload['username']

	conn = get_db()
	cursor = conn.cursor()
	#Check that listing exists and belongs to driver
	cursor.execute("SELECT * FROM availability WHERE listing_id = ? AND driver_username = ?;", (listingid, driver))
	result = cursor.fetchall()
	if not result:
		conn.close()
		return json.dumps({"status": 3})

	#Delete listing
	cursor.execute("DELETE FROM availability WHERE listing_id = ? AND driver_username = ?;", (listingid, driver))
	conn.commit()
	conn.close()
	return json.dumps({"status": 1})







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










