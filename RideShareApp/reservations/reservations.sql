drop TABLE IF EXISTS reservations;
CREATE TABLE reservations(
    listing_id INTEGER,
    rider_username TEXT NOT NULL,
    driver_username TEXT NOT NULL,
    price INTEGER NOT NULL,
    reservation_id INTEGER PRIMARY KEY AUTOINCREMENT
);