drop table IF EXISTS wallet;
CREATE TABLE wallet(
    username TEXT PRIMARY KEY,
    balance INTEGER NOT NULL
)