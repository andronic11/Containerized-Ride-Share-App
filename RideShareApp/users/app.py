import sqlite3
import os
from flask import Flask, request
from base64 import urlsafe_b64encode as b64url_encode, urlsafe_b64decode as b64url_decode
import json
from hashlib import sha256
import hmac
import requests

app = Flask(__name__)
db_name = "users.db"
sql_file = "users.sql"
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
	cursor.execute("SELECT * FROM users;")
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

@app.route('/get_user',methods=(['GET']))
def get_user():
	username = request.args.get('username')
	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
	result = cursor.fetchall()
	conn.close()
	if not result:
		return json.dumps({"status": 2, "user": 'NULL'})
	user_info = {
		"first_name": result[0][0],
		"last_name": result[0][1],
		"username": result[0][2],
		"email_address": result[0][3],
		"driver": result[0][4],
		"deposit": result[0][5]
	}
	return json.dumps({"status": 1, "user": user_info})

@app.route('/create_user', methods=(['POST']))
def create_user():
	#Get form data
	first_name = request.form.get('first_name')
	last_name = request.form.get('last_name')
	username = request.form.get('username')
	email_address = request.form.get('email_address')
	driver = request.form.get('driver')
	deposit = request.form.get('deposit')
	password = request.form.get('password')
	salt = request.form.get('salt')

	# Check if username already exists
	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
	resultUsername = cursor.fetchall()
	if resultUsername or not(username):
		conn.close()
		return json.dumps({"status": 2, "pass_hash": 'NULL'})
	
	# Check if email already exists
	cursor.execute("SELECT * FROM users WHERE email_address = ?;", (email_address,))
	resultEmail = cursor.fetchall()
	if resultEmail or not(email_address):
		conn.close()
		return json.dumps({"status": 3, "pass_hash": 'NULL'})
	
	# Validate password
	if not password_validation(password, first_name, last_name, username):
		return json.dumps({"status": 4, "pass_hash": 'NULL'})
	
	
	# Hash password
	password_hash = sha256((password + salt).encode("utf-8")).hexdigest()

	INSERTDEPOSITURL = "http://payments:5000/add"
	params = {'amount': deposit}
	jwt = get_JWT(username)
	headers = {'Authorization': jwt}
	response = requests.post(url = INSERTDEPOSITURL, data = params, headers = headers)
	payment_data = response.json()
	if payment_data['status'] != 1:
		return json.dumps({"status": 2, "pass_hash": 'NULL'})
	
	# Insert user into database
	cursor.execute("INSERT INTO users (first_name, last_name, username, email_address, driver, deposit, password_hash, salt) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", (first_name, last_name, username, email_address,driver,deposit, password_hash, salt))
	conn.commit()
	conn.close()
	return json.dumps({"status": 1, "pass_hash": password_hash})
	
@app.route('/login', methods=(['POST']))
def login():
	username = request.form.get('username')
	password = request.form.get('password')

	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM users WHERE username = ?;", (username,))
	result = cursor.fetchall()

	# Check if user exists
	if not result:
		conn.close()
		return json.dumps({"status": 2, "jwt": 'NULL'})
	
	salt = result[0][7]
	password_hash = sha256((password + salt).encode("utf-8")).hexdigest()

	# Check if password is correct
	if password_hash != result[0][6]:
		conn.close()
		return json.dumps({"status": 2, "jwt": 'NULL'})
	
	jwt = get_JWT(username)
	conn.close()
	return json.dumps({"status": 1, "jwt": jwt})

@app.route('/rate', methods=(['POST']))
def rate():
	username_to_rate = request.form.get('username')
	rating = request.form.get('rating')

	#Get user giving rating
	jwt_token = request.headers.get('Authorization')
	payload = verify_JWT(jwt_token)
	if not payload:
		return json.dumps({"status": 2})
	
	user_rater = payload['username']

	conn = get_db()
	cursor = conn.cursor()

	# Check if user to rate exists and if driver or not
	cursor.execute("SELECT * FROM users WHERE username = ?;", (username_to_rate,))
	result = cursor.fetchall()
	if not result:
		conn.close()
		return json.dumps({"status": 2})
	rated_user_driver = result[0][4]
	
	# Check if user exists and if driver or not
	cursor.execute("SELECT * FROM users WHERE username = ?;", (user_rater,))
	result_rater = cursor.fetchall()
	rater_is_driver = result_rater[0][4]

	#Check that both aren't drivers or riders
	if(rated_user_driver == rater_is_driver):
		conn.close()
		return json.dumps({"status": 2})
	
	GETRESERVATIONURL = "http://reservations:5000/get_reservation"
	params = {'driver_username': user_rater,'rider_username': username_to_rate} if rater_is_driver == 'True' else {'driver_username': username_to_rate,'rider_username': user_rater}
	response = requests.get(url = GETRESERVATIONURL, params = params)
	reservation_data = response.json()
	if reservation_data['status'] != 1:
		conn.close()
		return json.dumps({"status": 2})
	
	# Insert rating into database
	cursor.execute("INSERT INTO ratings (username, rating) VALUES (?,?);", (username_to_rate, rating))
	conn.commit()
	conn.close()
	return json.dumps({"status": 1})

@app.route('/view_rating', methods=(['GET']))
def view_rating():
	username = request.args.get('username')

	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT rating FROM ratings WHERE username = ?;", (username,))
	result = cursor.fetchall()
	conn.close()

	if not result:
		return json.dumps({"status": 1, "rating": f"{0:.2f}"})

	total_rating = 0
	for row in result:
		total_rating += int(row[0])
	average_rating = total_rating / len(result)
	average_rating = f"{average_rating:.2f}"
	return json.dumps({"status": 1, "rating": average_rating})

	






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









