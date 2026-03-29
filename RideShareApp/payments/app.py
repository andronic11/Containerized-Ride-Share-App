import sqlite3
import os
from flask import Flask, request
from base64 import urlsafe_b64encode as b64url_encode, urlsafe_b64decode as b64url_decode
import json
from hashlib import sha256
import hmac

app = Flask(__name__)
db_name = "payments.db"
sql_file = "payments.sql"

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
	cursor.execute("SELECT * FROM wallet;")
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

@app.route('/add', methods=(['POST']))
def add_payment():
	auth_header = request.headers.get('Authorization')
	payload = verify_JWT(auth_header)
	if not payload:
		return {"status": 2}
	username = payload.get('username')
	amount = request.form.get('amount')
	amount = float(amount)

	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM wallet WHERE username = ?;", (username,))
	result = cursor.fetchall()
	if result:
		new_balance = result[0][1] + amount
		cursor.execute("UPDATE wallet SET balance = ? WHERE username = ?;", (new_balance,username))
		conn.commit()
		conn.close()
		return {"status": 1}
	cursor.execute("INSERT INTO wallet (username, balance) VALUES (?, ?);", (username,amount))
	conn.commit()
	conn.close()
	return {"status": 1}

@app.route('/view', methods=(['GET']))
def view_balance():
	auth_header = request.headers.get('Authorization')
	payload = verify_JWT(auth_header)
	if not payload:
		return {"status": 2, "balance": 'NULL'}
	username = payload.get('username')

	conn = get_db()
	cursor = conn.cursor()
	cursor.execute("SELECT balance FROM wallet WHERE username = ?;", (username,))
	result = cursor.fetchall()
	conn.close()
	if not result:
		return {"status": 2, "balance": 'NULL'}
	amount = f"{result[0][0]:.2f}"
	return {"status": 1, "balance": amount}


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













