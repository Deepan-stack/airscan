-- ========================================================
-- AirScan - MySQL Database Schema
-- Database: airline_db
-- ========================================================

CREATE DATABASE IF NOT EXISTS airline_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE airline_db;

-- 1. Users table (authentication & verification)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(30),
    passport_number VARCHAR(50),
    is_verified TINYINT(1) DEFAULT 0,
    verification_code VARCHAR(10),
    verification_expiry DATETIME,
    role VARCHAR(20) DEFAULT 'passenger',
    miles INT DEFAULT 12500,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Airports table
CREATE TABLE IF NOT EXISTS airports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(5) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL,
    timezone VARCHAR(50) DEFAULT 'UTC'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Flights table
CREATE TABLE IF NOT EXISTS flights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flight_number VARCHAR(20) NOT NULL UNIQUE,
    airline_name VARCHAR(100) DEFAULT 'AirScan',
    origin_id INT NOT NULL,
    destination_id INT NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    duration_minutes INT NOT NULL,
    aircraft_model VARCHAR(100) NOT NULL,
    status VARCHAR(30) DEFAULT 'On Time',
    economy_price DECIMAL(10,2) NOT NULL,
    business_price DECIMAL(10,2) NOT NULL,
    first_price DECIMAL(10,2) NOT NULL,
    terminal VARCHAR(10) DEFAULT 'T1',
    gate VARCHAR(10) DEFAULT 'A4',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (origin_id) REFERENCES airports(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES airports(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Seats table
CREATE TABLE IF NOT EXISTS seats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flight_id INT NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    seat_class VARCHAR(20) NOT NULL, -- 'First', 'Business', 'Economy'
    is_extra_legroom TINYINT(1) DEFAULT 0,
    price_modifier DECIMAL(10,2) DEFAULT 0.00,
    is_occupied TINYINT(1) DEFAULT 0,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE,
    UNIQUE KEY flight_seat_unique (flight_id, seat_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Bookings table
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_reference VARCHAR(12) NOT NULL UNIQUE,
    user_id INT NOT NULL,
    flight_id INT NOT NULL,
    trip_type VARCHAR(20) DEFAULT 'One-Way',
    cabin_class VARCHAR(30) NOT NULL,
    total_fare DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'Paid',
    booking_status VARCHAR(20) DEFAULT 'Confirmed', -- 'Confirmed', 'Checked-In', 'Cancelled'
    booking_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Passengers table
CREATE TABLE IF NOT EXISTS passengers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    passport_number VARCHAR(50),
    date_of_birth DATE,
    seat_id INT,
    seat_number VARCHAR(10),
    meal_preference VARCHAR(50) DEFAULT 'Standard Gourmet',
    extra_baggage_kg INT DEFAULT 0,
    ticket_number VARCHAR(30) NOT NULL UNIQUE,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
