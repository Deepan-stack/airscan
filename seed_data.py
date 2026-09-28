import random
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from db import Database

def seed_all(reset=False):
    print("[SEED] Starting database initialization and seeding for AirScan...")
    Database.init_db()

    if reset:
        print("[SEED] Resetting existing flights, seats, bookings and passengers...")
        conn, mode = Database.get_connection()
        try:
            if mode == 'sqlite':
                conn.execute("DELETE FROM passengers;")
                conn.execute("DELETE FROM bookings;")
                conn.execute("DELETE FROM seats;")
                conn.execute("DELETE FROM flights;")
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
                cursor.execute("TRUNCATE TABLE passengers;")
                cursor.execute("TRUNCATE TABLE bookings;")
                cursor.execute("TRUNCATE TABLE seats;")
                cursor.execute("TRUNCATE TABLE flights;")
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
                conn.commit()
        finally:
            conn.close()

    # 1. Airports (Comprehensive Indian Metros + Regional + Top Global Hubs)
    airports = [
        # Major Indian Metros & Tech Hubs
        ('DEL', 'Indira Gandhi International Airport', 'New Delhi', 'India', 'Asia/Kolkata'),
        ('BOM', 'Chhatrapati Shivaji Maharaj International', 'Mumbai', 'India', 'Asia/Kolkata'),
        ('BLR', 'Kempegowda International Airport', 'Bengaluru', 'India', 'Asia/Kolkata'),
        ('MAA', 'Chennai International Airport', 'Chennai', 'India', 'Asia/Kolkata'),
        ('CCU', 'Netaji Subhash Chandra Bose International', 'Kolkata', 'India', 'Asia/Kolkata'),
        ('HYD', 'Rajiv Gandhi International Airport', 'Hyderabad', 'India', 'Asia/Kolkata'),
        ('COK', 'Cochin International Airport', 'Kochi', 'India', 'Asia/Kolkata'),
        ('GOI', 'Dabolim Airport', 'Goa', 'India', 'Asia/Kolkata'),
        ('GOX', 'Manohar International Airport', 'Mopa, Goa', 'India', 'Asia/Kolkata'),
        ('AMD', 'Sardar Vallabhbhai Patel International', 'Ahmedabad', 'India', 'Asia/Kolkata'),
        ('PNQ', 'Pune International Airport', 'Pune', 'India', 'Asia/Kolkata'),
        ('JAI', 'Jaipur International Airport', 'Jaipur', 'India', 'Asia/Kolkata'),
        ('LKO', 'Chaudhary Charan Singh International', 'Lucknow', 'India', 'Asia/Kolkata'),
        ('ATQ', 'Sri Guru Ram Dass Jee International', 'Amritsar', 'India', 'Asia/Kolkata'),
        ('TRV', 'Thiruvananthapuram International', 'Thiruvananthapuram', 'India', 'Asia/Kolkata'),
        ('GAU', 'Lokpriya Gopinath Bordoloi International', 'Guwahati', 'India', 'Asia/Kolkata'),
        ('IXC', 'Shaheed Bhagat Singh International', 'Chandigarh', 'India', 'Asia/Kolkata'),
        ('PAT', 'Jay Prakash Narayan Airport', 'Patna', 'India', 'Asia/Kolkata'),
        ('BBI', 'Biju Patnaik International Airport', 'Bhubaneswar', 'India', 'Asia/Kolkata'),
        ('SXR', 'Sheikh ul-Alam International Airport', 'Srinagar', 'India', 'Asia/Kolkata'),
        ('VNS', 'Lal Bahadur Shastri International Airport', 'Varanasi', 'India', 'Asia/Kolkata'),
        ('IDR', 'Devi Ahilyabai Holkar Airport', 'Indore', 'India', 'Asia/Kolkata'),

        # Major Global Hubs
        ('DXB', 'Dubai International Airport', 'Dubai', 'United Arab Emirates', 'Asia/Dubai'),
        ('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore', 'Asia/Singapore'),
        ('LHR', 'Heathrow Airport', 'London', 'United Kingdom', 'Europe/London'),
        ('JFK', 'John F. Kennedy International', 'New York', 'United States', 'America/New_York'),
        ('BKK', 'Suvarnabhumi Airport', 'Bangkok', 'Thailand', 'Asia/Bangkok'),
        ('DOH', 'Hamad International Airport', 'Doha', 'Qatar', 'Asia/Qatar'),
        ('KUL', 'Kuala Lumpur International Airport', 'Kuala Lumpur', 'Malaysia', 'Asia/Kuala_Lumpur'),
        ('CDG', 'Paris Charles de Gaulle Airport', 'Paris', 'France', 'Europe/Paris'),
        ('FRA', 'Frankfurt Airport', 'Frankfurt', 'Germany', 'Europe/Berlin'),
        ('HND', 'Tokyo Haneda Airport', 'Tokyo', 'Japan', 'Asia/Tokyo'),
        ('SYD', 'Sydney Kingsford Smith Airport', 'Sydney', 'Australia', 'Australia/Sydney'),
    ]

    for code, name, city, country, tz in airports:
        existing = Database.execute_query("SELECT id FROM airports WHERE code = %s", (code,), fetch_one=True)
        if not existing:
            Database.execute_commit(
                "INSERT INTO airports (code, name, city, country, timezone) VALUES (%s, %s, %s, %s, %s)",
                (code, name, city, country, tz)
            )

    airport_map = {r['code']: r['id'] for r in Database.execute_query("SELECT id, code FROM airports")}

    # 2. Users (Admin + Demo Passenger + Newbie)
    pwd_passenger = generate_password_hash('password123')
    pwd_admin = generate_password_hash('admin123')

    users_data = [
        ('Captain James Sterling', 'admin@airscan.com', pwd_admin, '+91-98765-43210', 'Z98765432', 1, None, None, 'admin', 98000),
        ('Captain James Sterling', 'admin@aerolux.com', pwd_admin, '+91-98765-43210', 'Z98765432', 1, None, None, 'admin', 98000),
        ('John Doe', 'john.doe@example.com', pwd_passenger, '+91-91234-56789', 'A12345678', 1, None, None, 'passenger', 34500),
        ('Sarah Jenkins', 'sarah@example.com', pwd_passenger, '+44-20-7946-0912', 'GB7654321', 1, None, None, 'passenger', 48200),
        ('Elena Rostova', 'newbie@example.com', pwd_passenger, '+91-99887-76655', 'FR9988776', 0, '849201', (datetime.now() + timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'), 'passenger', 5000),
    ]

    for name, email, pwd, phone, passport, is_v, vcode, vexpiry, role, miles in users_data:
        existing = Database.execute_query("SELECT id FROM users WHERE email = %s", (email,), fetch_one=True)
        if not existing:
            Database.execute_commit(
                """INSERT INTO users 
                   (full_name, email, password_hash, phone, passport_number, is_verified, verification_code, verification_expiry, role, miles)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (name, email, pwd, phone, passport, is_v, vcode, vexpiry, role, miles)
            )

    user_john = Database.execute_query("SELECT id FROM users WHERE email = %s", ('john.doe@example.com',), fetch_one=True)

    # 3. Flight Templates (Diverse Airlines, Real Routes, Realistic INR Prices)
    # Format: (airline_name, flight_number, origin, destination, duration_min, aircraft_model, p_eco, p_biz, p_first, terminal, gate)
    flight_templates = [
        # --- Domestic Trunk Routes ---
        ('IndiGo', '6E-204', 'DEL', 'BOM', 130, 'Airbus A321neo', 4850.00, 16500.00, 28000.00, 'T2', '24A'),
        ('Air India', 'AI-102', 'DEL', 'BOM', 135, 'Boeing 787-9 Dreamliner', 5200.00, 18500.00, 32000.00, 'T3', '12'),
        ('Vistara', 'UK-995', 'DEL', 'BOM', 125, 'Airbus A320neo', 5450.00, 19200.00, 33500.00, 'T3', '08'),
        ('Akasa Air', 'QP-1302', 'BOM', 'DEL', 130, 'Boeing 737 MAX 8', 4200.00, 14500.00, 26000.00, 'T1', '04'),
        
        ('IndiGo', '6E-512', 'BOM', 'BLR', 105, 'Airbus A320neo', 3950.00, 13800.00, 24500.00, 'T1', '14'),
        ('Air India', 'AI-639', 'BOM', 'BLR', 110, 'Airbus A321neo', 4300.00, 15200.00, 27000.00, 'T2', '31'),
        ('Akasa Air', 'QP-1108', 'BLR', 'BOM', 105, 'Boeing 737 MAX 8', 3650.00, 12800.00, 23000.00, 'T1', '09'),

        ('Vistara', 'UK-812', 'DEL', 'BLR', 170, 'Airbus A321neo', 5800.00, 21000.00, 36000.00, 'T3', '15'),
        ('IndiGo', '6E-1011', 'DEL', 'BLR', 165, 'Airbus A321neo', 5100.00, 17500.00, 31000.00, 'T2', '18'),
        ('Air India', 'AI-506', 'BLR', 'DEL', 165, 'Boeing 777-300ER', 5600.00, 22000.00, 39000.00, 'T2', '05'),

        ('IndiGo', '6E-348', 'DEL', 'CCU', 135, 'Airbus A320neo', 4600.00, 15800.00, 27500.00, 'T2', '11'),
        ('Air India', 'AI-701', 'CCU', 'DEL', 140, 'Airbus A320neo', 4900.00, 16900.00, 29000.00, 'T1', '06'),

        ('IndiGo', '6E-724', 'BOM', 'GOI', 70, 'Airbus A320neo', 3200.00, 11500.00, 21000.00, 'T1', '07'),
        ('SpiceJet', 'SG-8114', 'DEL', 'GOX', 150, 'Boeing 737-800', 4900.00, 14200.00, 25000.00, 'T3', '22'),
        ('Akasa Air', 'QP-1456', 'GOX', 'BOM', 75, 'Boeing 737 MAX 8', 2999.00, 10800.00, 19500.00, 'T1', '02'),

        ('IndiGo', '6E-442', 'DEL', 'HYD', 140, 'Airbus A320neo', 4400.00, 15500.00, 27000.00, 'T2', '19'),
        ('Air India', 'AI-544', 'HYD', 'DEL', 135, 'Airbus A321neo', 4700.00, 16200.00, 28500.00, 'T1', '12'),

        ('Air India Express', 'IX-345', 'BLR', 'COK', 65, 'Boeing 737-800', 2850.00, 9500.00, 17500.00, 'T1', '03'),
        ('IndiGo', '6E-881', 'MAA', 'BOM', 115, 'Airbus A320neo', 3800.00, 13200.00, 23500.00, 'T1', '08'),
        ('Vistara', 'UK-707', 'DEL', 'SXR', 85, 'Airbus A320neo', 4600.00, 15000.00, 26500.00, 'T3', '10'),
        ('SpiceJet', 'SG-415', 'DEL', 'JAI', 55, 'Bombardier Q400', 2499.00, 8500.00, 15000.00, 'T3', '01'),
        ('IndiGo', '6E-629', 'CCU', 'GAU', 70, 'Airbus A320neo', 3100.00, 10500.00, 18500.00, 'T1', '05'),
        ('Air India', 'AI-435', 'DEL', 'LKO', 65, 'Airbus A320neo', 2900.00, 9800.00, 17000.00, 'T3', '04'),
        ('IndiGo', '6E-902', 'BOM', 'AMD', 75, 'Airbus A320neo', 3150.00, 11000.00, 19000.00, 'T1', '06'),
        ('IndiGo', '6E-551', 'DEL', 'VNS', 80, 'Airbus A320neo', 3450.00, 11800.00, 20500.00, 'T2', '16'),

        # --- International Routes from India ---
        ('Emirates', 'EK-501', 'BOM', 'DXB', 205, 'Boeing 777-300ER', 19500.00, 68000.00, 145000.00, 'T2', 'Gate 42'),
        ('Emirates', 'EK-512', 'DEL', 'DXB', 225, 'Airbus A380-800', 22000.00, 74000.00, 165000.00, 'T3', 'Gate 18'),
        ('Air India', 'AI-995', 'DEL', 'DXB', 230, 'Boeing 787-9 Dreamliner', 16500.00, 52000.00, 115000.00, 'T3', 'Gate 14'),
        ('IndiGo', '6E-1451', 'BOM', 'DXB', 215, 'Airbus A321neo', 14200.00, 44000.00, 88000.00, 'T2', 'Gate 35'),
        ('Qatar Airways', 'QR-556', 'DEL', 'DOH', 255, 'Boeing 787-9 Dreamliner', 24500.00, 78000.00, 175000.00, 'T3', 'Gate 22'),
        ('Qatar Airways', 'QR-571', 'BOM', 'DOH', 235, 'Airbus A350-900', 23500.00, 76000.00, 170000.00, 'T2', 'Gate 26'),
        ('Etihad Airways', 'EY-205', 'BOM', 'DXB', 210, 'Boeing 787-9 Dreamliner', 18500.00, 64000.00, 138000.00, 'T2', 'Gate 28'),

        ('Singapore Airlines', 'SQ-402', 'DEL', 'SIN', 335, 'Boeing 787-10 Dreamliner', 28500.00, 89000.00, 195000.00, 'T3', 'Gate 05'),
        ('Singapore Airlines', 'SQ-424', 'BOM', 'SIN', 325, 'Airbus A350-900', 27500.00, 86000.00, 190000.00, 'T2', 'Gate 11'),
        ('Air India', 'AI-380', 'DEL', 'SIN', 340, 'Airbus A350-900', 21500.00, 69000.00, 148000.00, 'T3', 'Gate 09'),
        ('IndiGo', '6E-1005', 'BLR', 'SIN', 270, 'Airbus A321neo', 16800.00, 49000.00, 95000.00, 'T2', 'Gate 16'),
        ('Air India', 'AI-332', 'DEL', 'BKK', 250, 'Boeing 787-8', 17800.00, 56000.00, 118000.00, 'T3', 'Gate 15'),

        ('British Airways', 'BA-138', 'BOM', 'LHR', 570, 'Boeing 777-300ER', 48500.00, 145000.00, 310000.00, 'T2', 'Gate 48'),
        ('British Airways', 'BA-142', 'DEL', 'LHR', 560, 'Boeing 787-9 Dreamliner', 49500.00, 149000.00, 320000.00, 'T3', 'Gate 16'),
        ('Air India', 'AI-161', 'DEL', 'LHR', 555, 'Boeing 777-300ER', 41500.00, 128000.00, 275000.00, 'T3', 'Gate 20'),
        ('Virgin Atlantic', 'VS-301', 'DEL', 'LHR', 565, 'Airbus A350-1000', 46500.00, 142000.00, 305000.00, 'T3', 'Gate 12'),

        ('Lufthansa', 'LH-760', 'DEL', 'FRA', 510, 'Boeing 747-8 Intercontinental', 52000.00, 155000.00, 340000.00, 'T3', 'Gate 24'),
        ('Air India', 'AI-144', 'DEL', 'CDG', 540, 'Boeing 787-8', 44500.00, 134000.00, 285000.00, 'T3', 'Gate 07'),

        ('Air India', 'AI-101', 'DEL', 'JFK', 940, 'Boeing 777-200LR', 68500.00, 215000.00, 480000.00, 'T3', 'Gate 02'),
        ('Air India', 'AI-119', 'BOM', 'JFK', 960, 'Boeing 777-300ER', 69500.00, 220000.00, 490000.00, 'T2', 'Gate 01'),
        ('Air India', 'AI-302', 'DEL', 'SYD', 740, 'Boeing 787-8 Dreamliner', 58000.00, 178000.00, 385000.00, 'T3', 'Gate 17'),
        ('Air India', 'AI-308', 'DEL', 'HND', 475, 'Boeing 787-8 Dreamliner', 46000.00, 142000.00, 295000.00, 'T3', 'Gate 19'),
    ]

    base_time = datetime.now().replace(minute=0, second=0, microsecond=0)

    flight_dates = [
        base_time + timedelta(hours=3),
        base_time + timedelta(hours=8),
        base_time + timedelta(days=1, hours=4),
        base_time + timedelta(days=1, hours=14),
        base_time + timedelta(days=2, hours=6),
        base_time + timedelta(days=3, hours=10),
        base_time + timedelta(days=5, hours=9),
        base_time + timedelta(days=7, hours=16),
    ]

    created_flight_ids = []

    for idx, (airline, fnum_base, orig, dest, dur, aircraft, p_eco, p_biz, p_first, term, gate) in enumerate(flight_templates):
        if orig not in airport_map or dest not in airport_map:
            continue
        for d_idx, dep_dt in enumerate([flight_dates[idx % len(flight_dates)], flight_dates[(idx + 3) % len(flight_dates)] + timedelta(days=3)]):
            f_num = f"{fnum_base}-{d_idx+1}" if d_idx > 0 else fnum_base
            arr_dt = dep_dt + timedelta(minutes=dur)

            existing_f = Database.execute_query("SELECT id FROM flights WHERE flight_number = %s", (f_num,), fetch_one=True)
            if not existing_f:
                fid = Database.execute_commit(
                    """INSERT INTO flights 
                       (flight_number, airline_name, origin_id, destination_id, departure_time, arrival_time, 
                        duration_minutes, aircraft_model, status, economy_price, business_price, first_price, terminal, gate)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'On Time', %s, %s, %s, %s, %s)""",
                    (f_num, airline, airport_map[orig], airport_map[dest],
                     dep_dt.strftime('%Y-%m-%d %H:%M:%S'), arr_dt.strftime('%Y-%m-%d %H:%M:%S'),
                     dur, aircraft, p_eco, p_biz, p_first, term, gate)
                )
                created_flight_ids.append((fid, f_num))
                _generate_flight_seats(fid)
            else:
                created_flight_ids.append((existing_f['id'], f_num))

    # 4. Generate a sample completed booking for John Doe in INR
    if user_john and created_flight_ids:
        sample_fid, sample_fnum = created_flight_ids[0]
        existing_b = Database.execute_query("SELECT id FROM bookings WHERE user_id = %s", (user_john['id'],), fetch_one=True)
        if not existing_b:
            b_ref = "AS-8924K"
            bid = Database.execute_commit(
                """INSERT INTO bookings 
                   (booking_reference, user_id, flight_id, trip_type, cabin_class, total_fare, payment_status, booking_status)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (b_ref, user_john['id'], sample_fid, 'One-Way', 'Business', 21500.00, 'Paid', 'Confirmed')
            )
            # Find an unoccupied business seat
            b_seat = Database.execute_query(
                "SELECT id, seat_number FROM seats WHERE flight_id = %s AND seat_class = 'Business' AND is_occupied = 0 LIMIT 1",
                (sample_fid,),
                fetch_one=True
            )
            if b_seat:
                Database.execute_commit("UPDATE seats SET is_occupied = 1 WHERE id = %s", (b_seat['id'],))
                Database.execute_commit(
                    """INSERT INTO passengers 
                       (booking_id, full_name, passport_number, date_of_birth, seat_id, seat_number, meal_preference, extra_baggage_kg, ticket_number)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (bid, 'John Doe', 'A12345678', '1988-06-14', b_seat['id'], b_seat['seat_number'], 'Hindu Vegetarian Thali', 0, 'TKT-78902148')
                )

    print(f"[SEED] Successfully seeded {len(airports)} airports, {len(created_flight_ids)} scheduled flights across major Indian & international airlines!")

def _generate_flight_seats(flight_id):
    """
    Generates a realistic airliner seat map with INR upgrades:
    - First Class (Rows 1-2): 1A, 1D, 1F, 2A, 2D, 2F (+ suites, ₹6,000 modifier)
    - Business Class (Rows 3-6): A, B, E, F (2-2 configuration)
    - Economy Class (Rows 10-20): A, B, C, D, E, F (3-3 configuration)
      Row 10 & 14 are Exit Rows with Extra Legroom (₹850 modifier)
    """
    seats_to_insert = []
    
    # First Class: Rows 1 to 2
    for r in [1, 2]:
        for col in ['A', 'D', 'F']:
            is_occ = 1 if random.random() < 0.20 else 0
            seats_to_insert.append((flight_id, f"{r}{col}", 'First', 1, 6000.00, is_occ))

    # Business Class: Rows 3 to 6
    for r in range(3, 7):
        for col in ['A', 'B', 'E', 'F']:
            is_occ = 1 if random.random() < 0.30 else 0
            seats_to_insert.append((flight_id, f"{r}{col}", 'Business', 0, 0.00, is_occ))

    # Economy Class: Rows 10 to 20
    for r in range(10, 21):
        is_exit = 1 if r in (10, 14) else 0
        legroom_fee = 850.00 if is_exit else (450.00 if r == 11 else 0.00)
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            is_occ = 1 if random.random() < 0.25 else 0
            seats_to_insert.append((flight_id, f"{r}{col}", 'Economy', is_exit, legroom_fee, is_occ))

    for s in seats_to_insert:
        Database.execute_commit(
            """INSERT INTO seats 
               (flight_id, seat_number, seat_class, is_extra_legroom, price_modifier, is_occupied)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            s
        )

if __name__ == '__main__':
    seed_all(reset=True)
