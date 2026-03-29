DROP TABLE IF EXISTS availability;

CREATE TABLE availability(
    listing_id INTEGER PRIMARY KEY,
    dayOfWeek TEXT NOT NULL,
    price INTEGER NOT NULL,
    driver_username TEXT NOT NULL
);