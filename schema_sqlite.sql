-- ========================================================
-- AirScan - SQLite Database Schema
-- ========================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    phone TEXT,
    passport_number TEXT,
    is_verified INTEGER DEFAULT 0,
    verification_code TEXT,
    verification_expiry TEXT,
    role TEXT DEFAULT 'passenger',
    miles INTEGER DEFAULT 12500,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS airports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    timezone TEXT DEFAULT 'UTC'
);

CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number TEXT NOT NULL UNIQUE,
    airline_name TEXT DEFAULT 'AirScan',
    origin_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    aircraft_model TEXT NOT NULL,
    status TEXT DEFAULT 'On Time',
    economy_price REAL NOT NULL,
    business_price REAL NOT NULL,
    first_price REAL NOT NULL,
    terminal TEXT DEFAULT 'T1',
    gate TEXT DEFAULT 'A4',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (origin_id) REFERENCES airports(id),
    FOREIGN KEY (destination_id) REFERENCES airports(id)
);

CREATE TABLE IF NOT EXISTS seats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_id INTEGER NOT NULL,
    seat_number TEXT NOT NULL,
    seat_class TEXT NOT NULL,
    is_extra_legroom INTEGER DEFAULT 0,
    price_modifier REAL DEFAULT 0.0,
    is_occupied INTEGER DEFAULT 0,
    FOREIGN KEY (flight_id) REFERENCES flights(id),
    UNIQUE (flight_id, seat_number)
);

CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_reference TEXT NOT NULL UNIQUE,
    user_id INTEGER NOT NULL,
    flight_id INTEGER NOT NULL,
    trip_type TEXT DEFAULT 'One-Way',
    cabin_class TEXT NOT NULL,
    total_fare REAL NOT NULL,
    payment_status TEXT DEFAULT 'Paid',
    booking_status TEXT DEFAULT 'Confirmed',
    booking_date TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (flight_id) REFERENCES flights(id)
);

CREATE TABLE IF NOT EXISTS passengers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    passport_number TEXT,
    date_of_birth TEXT,
    seat_id INTEGER,
    seat_number TEXT,
    meal_preference TEXT DEFAULT 'Standard Gourmet',
    extra_baggage_kg INTEGER DEFAULT 0,
    ticket_number TEXT NOT NULL UNIQUE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (seat_id) REFERENCES seats(id)
);
