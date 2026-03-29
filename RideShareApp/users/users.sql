DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS users;


CREATE TABLE users (
  first_name TEXT,
  last_name  TEXT,
  username   TEXT PRIMARY KEY,
  email_address TEXT UNIQUE NOT NULL,
  driver BOOLEAN,
  deposit INTEGER,
  password_hash TEXT NOT NULL,
  salt TEXT NOT NULL
);

CREATE TABLE ratings (
  username TEXT NOT NULL,
  rating INTEGER NOT NULL,
  rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
  FOREIGN KEY(username) REFERENCES users(username)
);



