import os
import random
import string
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, abort, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from db import Database

app = Flask(__name__)
app.config.from_object(Config)

# Ensure database tables and initial seed data exist
try:
    from seed_data import seed_all
    # Quick check if flights exist
    try:
        flights_exist = Database.execute_query("SELECT id FROM flights LIMIT 1", fetch_one=True)
        if not flights_exist:
            seed_all()
    except Exception:
        seed_all()
except Exception as e:
    print(f"[INIT] DB initialization check: {e}")

# Helper: login_required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Helper: admin_required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Admin authentication required.', 'warning')
            return redirect(url_for('login', next=request.url))
        if session.get('user_role') != 'admin':
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Inject current user and db info into all templates
@app.context_processor
def inject_global_data():
    current_user = None
    if 'user_id' in session:
        current_user = Database.execute_query(
            "SELECT id, full_name, email, phone, passport_number, is_verified, role, miles FROM users WHERE id = %s",
            (session['user_id'],),
            fetch_one=True
        )
    db_info = Database.get_db_info()
    return {
        'current_user': current_user,
        'db_info': db_info,
        'current_year': datetime.now().year
    }

def generate_reference():
    letters = ''.join(random.choices(string.ascii_uppercase, k=4))
    digits = ''.join(random.choices(string.digits, k=3))
    return f"AS-{digits}{letters[:2]}"

def generate_ticket_num():
    return f"TKT-{''.join(random.choices(string.digits, k=8))}"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ==========================================
# AUTHENTICATION & VERIFICATION ROUTES
# ==========================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        phone = request.form.get('phone', '').strip()
        passport_number = request.form.get('passport_number', '').strip().upper()

        if not full_name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        # Check existing user
        existing = Database.execute_query("SELECT id FROM users WHERE email = %s", (email,), fetch_one=True)
        if existing:
            flash('An account with this email address already exists.', 'warning')
            return render_template('register.html')

        # Generate 6-digit verification code
        v_code = ''.join(random.choices(string.digits, k=6))
        v_expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
        pwd_hash = generate_password_hash(password)

        user_id = Database.execute_commit(
            """INSERT INTO users 
               (full_name, email, password_hash, phone, passport_number, is_verified, verification_code, verification_expiry, role, miles)
               VALUES (%s, %s, %s, %s, %s, 0, %s, %s, 'passenger', 5000)""",
            (full_name, email, pwd_hash, phone, passport_number, v_code, v_expiry)
        )

        session['pending_verification_email'] = email
        session['last_sent_code'] = v_code # Stored for simulated email notification preview

        flash('Registration successful! We have sent a 6-digit verification code to your email.', 'success')
        return redirect(url_for('verify'))

    return render_template('register.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    email = session.get('pending_verification_email')
    if not email and 'user_id' in session:
        user = Database.execute_query("SELECT email, is_verified FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
        if user and not user['is_verified']:
            email = user['email']
        else:
            return redirect(url_for('index'))

    if not email:
        flash('No pending verification session. Please sign in or register.', 'info')
        return redirect(url_for('login'))

    user = Database.execute_query("SELECT * FROM users WHERE email = %s", (email,), fetch_one=True)
    if not user:
        flash('Account not found.', 'danger')
        return redirect(url_for('register'))

    if user['is_verified']:
        flash('Your account is already verified. You can sign in.', 'success')
        return redirect(url_for('login'))

    simulated_code = user['verification_code']

    if request.method == 'POST':
        c1 = request.form.get('code_1', '')
        c2 = request.form.get('code_2', '')
        c3 = request.form.get('code_3', '')
        c4 = request.form.get('code_4', '')
        c5 = request.form.get('code_5', '')
        c6 = request.form.get('code_6', '')
        submitted_code = (c1 + c2 + c3 + c4 + c5 + c6).strip()

        # Fallback if submitted as single field
        if not submitted_code:
            submitted_code = request.form.get('verification_code', '').strip()

        if submitted_code == user['verification_code']:
            Database.execute_commit(
                "UPDATE users SET is_verified = 1, verification_code = NULL, verification_expiry = NULL WHERE id = %s",
                (user['id'],)
            )
            # Log the user in directly
            session.pop('pending_verification_email', None)
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session['user_role'] = user['role']

            flash(f'Account verified successfully! Welcome aboard AeroLux, {user["full_name"]}.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid verification code. Please check and try again.', 'danger')

    return render_template('verify.html', email=email, simulated_code=simulated_code)

@app.route('/api/resend-code', methods=['POST'])
def resend_verification_code():
    email = session.get('pending_verification_email')
    if not email and 'user_id' in session:
        user = Database.execute_query("SELECT email FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
        if user:
            email = user['email']

    if not email:
        return jsonify({'success': False, 'message': 'Session expired. Please log in.'}), 400

    new_code = ''.join(random.choices(string.digits, k=6))
    new_expiry = (datetime.now() + timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')

    Database.execute_commit(
        "UPDATE users SET verification_code = %s, verification_expiry = %s WHERE email = %s",
        (new_code, new_expiry, email)
    )
    session['last_sent_code'] = new_code

    return jsonify({
        'success': True,
        'message': f'A new verification code has been dispatched to {email}.',
        'simulated_code': new_code
    })

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = Database.execute_query("SELECT * FROM users WHERE email = %s", (email,), fetch_one=True)

        if not user or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html', email=email)

        # Check if email is verified
        if not user['is_verified']:
            session['pending_verification_email'] = user['email']
            session['last_sent_code'] = user['verification_code']
            flash('Your account has not been verified yet. Please enter the verification code sent to your email.', 'warning')
            return redirect(url_for('verify'))

        session['user_id'] = user['id']
        session['user_name'] = user['full_name']
        session['user_email'] = user['email']
        session['user_role'] = user['role']

        flash(f'Welcome back, {user["full_name"]}!', 'success')
        next_url = request.args.get('next')
        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        if user['role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been securely logged out. We look forward to flying with you again.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = Database.execute_query("SELECT * FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)
    
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        passport_number = request.form.get('passport_number', '').strip().upper()

        Database.execute_commit(
            "UPDATE users SET full_name = %s, phone = %s, passport_number = %s WHERE id = %s",
            (full_name, phone, passport_number, session['user_id'])
        )
        session['user_name'] = full_name
        flash('Your profile credentials have been updated successfully.', 'success')
        return redirect(url_for('profile'))

    # Get user booking summary
    bookings = Database.execute_query(
        """SELECT b.*, f.flight_number, orig.code as origin_code, dest.code as destination_code,
                  f.departure_time, f.arrival_time
           FROM bookings b
           JOIN flights f ON b.flight_id = f.id
           JOIN airports orig ON f.origin_id = orig.id
           JOIN airports dest ON f.destination_id = dest.id
           WHERE b.user_id = %s
           ORDER BY b.booking_date DESC LIMIT 5""",
        (session['user_id'],)
    )

    return render_template('profile.html', user=user, recent_bookings=bookings)

# ==========================================
# FLIGHT SEARCH & CATALOG ROUTES
# ==========================================

@app.route('/')
def index():
    airports = Database.execute_query("SELECT * FROM airports ORDER BY city ASC")
    featured_flights = Database.execute_query(
        """SELECT f.*, 
                  orig.city as origin_city, orig.code as origin_code, orig.country as origin_country,
                  dest.city as destination_city, dest.code as destination_code, dest.country as destination_country
           FROM flights f
           JOIN airports orig ON f.origin_id = orig.id
           JOIN airports dest ON f.destination_id = dest.id
           WHERE f.status != 'Cancelled'
           ORDER BY f.departure_time ASC
           LIMIT 6"""
    )
    return render_template('index.html', airports=airports, featured_flights=featured_flights)

@app.route('/flights')
def flights():
    airports = Database.execute_query("SELECT * FROM airports ORDER BY city ASC")
    
    origin = request.args.get('origin', '').strip().upper()
    destination = request.args.get('destination', '').strip().upper()
    dep_date = request.args.get('date', '').strip()
    trip_type = request.args.get('trip_type', 'one-way')
    cabin_class = request.args.get('cabin_class', 'Economy')
    passengers = int(request.args.get('passengers', 1))
    airline_filter = request.args.get('airline', '').strip()

    query = """
        SELECT f.*, 
               orig.name as origin_name, orig.city as origin_city, orig.code as origin_code,
               dest.name as destination_name, dest.city as destination_city, dest.code as destination_code,
               (SELECT COUNT(*) FROM seats s WHERE s.flight_id = f.id AND s.is_occupied = 0) as available_seats
        FROM flights f
        JOIN airports orig ON f.origin_id = orig.id
        JOIN airports dest ON f.destination_id = dest.id
        WHERE 1=1
    """
    params = []

    if origin:
        query += " AND (orig.code = %s OR orig.city LIKE %s)"
        params.extend([origin, f"%{origin}%"])
    if destination:
        query += " AND (dest.code = %s OR dest.city LIKE %s)"
        params.extend([destination, f"%{destination}%"])
    if dep_date:
        query += " AND DATE(f.departure_time) = %s"
        params.append(dep_date)
    if airline_filter and airline_filter != 'all':
        query += " AND f.airline_name = %s"
        params.append(airline_filter)

    query += " ORDER BY f.departure_time ASC"

    flight_results = Database.execute_query(query, tuple(params))

    # Calculate cabin specific pricing and format times
    for fl in flight_results:
        fl['duration_formatted'] = f"{fl['duration_minutes'] // 60}h {fl['duration_minutes'] % 60}m"
        fl['dep_time_formatted'] = datetime.strptime(str(fl['departure_time'])[:19], '%Y-%m-%d %H:%M:%S').strftime('%H:%M • %b %d')
        fl['arr_time_formatted'] = datetime.strptime(str(fl['arrival_time'])[:19], '%Y-%m-%d %H:%M:%S').strftime('%H:%M • %b %d')

    # Get distinct list of available airlines for dynamic filtering
    airline_rows = Database.execute_query("SELECT DISTINCT airline_name FROM flights WHERE airline_name IS NOT NULL ORDER BY airline_name ASC")
    airlines = [a['airline_name'] for a in airline_rows if a.get('airline_name')]

    return render_template(
        'flights.html',
        flights=flight_results,
        airports=airports,
        airlines=airlines,
        selected_airline=airline_filter,
        origin=origin,
        destination=destination,
        dep_date=dep_date,
        trip_type=trip_type,
        cabin_class=cabin_class,
        passengers=passengers
    )

@app.route('/api/airports')
def api_airports():
    airports = Database.execute_query("SELECT id, code, name, city, country FROM airports ORDER BY city ASC")
    return jsonify(airports)

# ==========================================
# SEAT SELECTION & BOOKING FLOW
# ==========================================

@app.route('/book/<int:flight_id>')
@login_required
def book_flight(flight_id):
    flight = Database.execute_query(
        """SELECT f.*, 
                  orig.name as origin_name, orig.city as origin_city, orig.code as origin_code,
                  dest.name as destination_name, dest.city as destination_city, dest.code as destination_code
           FROM flights f
           JOIN airports orig ON f.origin_id = orig.id
           JOIN airports dest ON f.destination_id = dest.id
           WHERE f.id = %s""",
        (flight_id,),
        fetch_one=True
    )
    if not flight:
        flash('Flight not found or no longer available.', 'danger')
        return redirect(url_for('flights'))

    flight['duration_formatted'] = f"{flight['duration_minutes'] // 60}h {flight['duration_minutes'] % 60}m"

    cabin_class = request.args.get('cabin_class', 'Economy')
    passengers_count = int(request.args.get('passengers', 1))

    # Fetch all seats for this flight
    seats = Database.execute_query(
        "SELECT * FROM seats WHERE flight_id = %s ORDER BY id ASC",
        (flight_id,)
    )

    user = Database.execute_query("SELECT * FROM users WHERE id = %s", (session['user_id'],), fetch_one=True)

    return render_template(
        'book.html',
        flight=flight,
        seats=seats,
        cabin_class=cabin_class,
        passengers_count=passengers_count,
        user=user
    )

@app.route('/api/book', methods=['POST'])
@login_required
def process_booking():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request body.'}), 400

    flight_id = data.get('flight_id')
    cabin_class = data.get('cabin_class', 'Economy')
    passengers_data = data.get('passengers', [])
    promo_code = data.get('promo_code', '').strip().upper()

    if not flight_id or not passengers_data:
        return jsonify({'success': False, 'message': 'Incomplete passenger or flight data.'}), 400

    flight = Database.execute_query("SELECT * FROM flights WHERE id = %s", (flight_id,), fetch_one=True)
    if not flight:
        return jsonify({'success': False, 'message': 'Flight not found.'}), 404

    # Determine base price per ticket
    if cabin_class == 'First':
        base_price = float(flight['first_price'])
    elif cabin_class == 'Business':
        base_price = float(flight['business_price'])
    else:
        base_price = float(flight['economy_price'])

    total_fare = 0.0
    verified_passengers = []

    # Validate and prepare each seat and passenger
    for p in passengers_data:
        seat_id = p.get('seat_id')
        seat_num = p.get('seat_number')
        p_name = p.get('full_name', '').strip()
        p_passport = p.get('passport', '').strip()
        p_meal = p.get('meal', 'Standard Gourmet')
        p_baggage = int(p.get('baggage', 0))

        if not seat_id or not p_name:
            return jsonify({'success': False, 'message': 'Passenger name and seat selection required for all passengers.'}), 400

        # Check seat availability
        seat = Database.execute_query("SELECT * FROM seats WHERE id = %s AND flight_id = %s", (seat_id, flight_id), fetch_one=True)
        if not seat or seat['is_occupied']:
            return jsonify({'success': False, 'message': f"Seat {seat_num} is no longer available. Please pick another seat."}), 400

        seat_addon = float(seat['price_modifier'])
        baggage_fee = 1200.0 if p_baggage > 23 else 0.0
        p_total = base_price + seat_addon + baggage_fee
        total_fare += p_total

        verified_passengers.append({
            'seat_id': seat_id,
            'seat_number': seat['seat_number'],
            'full_name': p_name,
            'passport_number': p_passport,
            'dob': p.get('dob', '1995-01-01'),
            'meal': p_meal,
            'baggage': p_baggage,
            'ticket_number': generate_ticket_num()
        })

    # Apply promo discount
    if promo_code in ('AIRSCAN20', 'FLYLUX20'):
        total_fare = round(total_fare * 0.80, 2)
    elif promo_code in ('AIRSCAN500', 'FIRSTFLY'):
        total_fare = max(0.0, total_fare - 500.00)

    # Taxes and airport fees (approx 12% GST)
    tax = round(total_fare * 0.12, 2)
    grand_total = total_fare + tax

    # Create Booking
    booking_ref = generate_reference()
    booking_id = Database.execute_commit(
        """INSERT INTO bookings 
           (booking_reference, user_id, flight_id, trip_type, cabin_class, total_fare, payment_status, booking_status)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (booking_ref, session['user_id'], flight_id, 'One-Way', cabin_class, grand_total, 'Paid', 'Confirmed')
    )

    # Insert passengers and mark seats occupied
    for vp in verified_passengers:
        Database.execute_commit(
            """INSERT INTO passengers 
               (booking_id, full_name, passport_number, date_of_birth, seat_id, seat_number, meal_preference, extra_baggage_kg, ticket_number)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (booking_id, vp['full_name'], vp['passport_number'], vp['dob'], vp['seat_id'], vp['seat_number'], vp['meal'], vp['baggage'], vp['ticket_number'])
        )
        Database.execute_commit("UPDATE seats SET is_occupied = 1 WHERE id = %s", (vp['seat_id'],))

    # Award frequent flyer miles to user (1 mile per ₹10 spent)
    earned_miles = max(100, int(grand_total / 10))
    Database.execute_commit("UPDATE users SET miles = miles + %s WHERE id = %s", (earned_miles, session['user_id']))

    return jsonify({
        'success': True,
        'booking_reference': booking_ref,
        'redirect_url': url_for('booking_confirmation', reference=booking_ref)
    })

@app.route('/booking-confirmation/<reference>')
@login_required
def booking_confirmation(reference):
    booking = Database.execute_query(
        """SELECT b.*, f.flight_number, f.airline_name, f.aircraft_model, f.departure_time, f.arrival_time, f.terminal, f.gate,
                  orig.name as origin_name, orig.city as origin_city, orig.code as origin_code,
                  dest.name as destination_name, dest.city as destination_city, dest.code as destination_code
           FROM bookings b
           JOIN flights f ON b.flight_id = f.id
           JOIN airports orig ON f.origin_id = orig.id
           JOIN airports dest ON f.destination_id = dest.id
           WHERE b.booking_reference = %s AND b.user_id = %s""",
        (reference, session['user_id']),
        fetch_one=True
    )
    if not booking:
        flash('Booking reference not found.', 'danger')
        return redirect(url_for('my_bookings'))

    passengers = Database.execute_query("SELECT * FROM passengers WHERE booking_id = %s", (booking['id'],))

    return render_template('booking_success.html', booking=booking, passengers=passengers)

# ==========================================
# TICKET MANAGEMENT & BOARDING PASS
# ==========================================

@app.route('/my-bookings')
@login_required
def my_bookings():
    bookings = Database.execute_query(
        """SELECT b.*, f.flight_number, f.airline_name, f.aircraft_model, f.departure_time, f.arrival_time, f.terminal, f.gate, f.status as flight_status,
                  orig.city as origin_city, orig.code as origin_code,
                  dest.city as destination_city, dest.code as destination_code,
                  (SELECT COUNT(*) FROM passengers p WHERE p.booking_id = b.id) as passenger_count
           FROM bookings b
           JOIN flights f ON b.flight_id = f.id
           JOIN airports orig ON f.origin_id = orig.id
           JOIN airports dest ON f.destination_id = dest.id
           WHERE b.user_id = %s
           ORDER BY b.booking_date DESC""",
        (session['user_id'],)
    )

    # Attach passengers list for each booking
    for b in bookings:
        b['passengers'] = Database.execute_query("SELECT * FROM passengers WHERE booking_id = %s", (b['id'],))
        dep_dt = datetime.strptime(str(b['departure_time'])[:19], '%Y-%m-%d %H:%M:%S')
        b['is_past'] = dep_dt < datetime.now()
        b['dep_formatted'] = dep_dt.strftime('%a, %d %b %Y • %H:%M')

    return render_template('my_bookings.html', bookings=bookings)

@app.route('/ticket/<reference>')
@login_required
def view_ticket(reference):
    booking = Database.execute_query(
        """SELECT b.*, f.flight_number, f.airline_name, f.aircraft_model, f.departure_time, f.arrival_time, f.terminal, f.gate, f.duration_minutes,
                  orig.name as origin_name, orig.city as origin_city, orig.code as origin_code,
                  dest.name as destination_name, dest.city as destination_city, dest.code as destination_code
           FROM bookings b
           JOIN flights f ON b.flight_id = f.id
           JOIN airports orig ON f.origin_id = orig.id
           JOIN airports dest ON f.destination_id = dest.id
           WHERE b.booking_reference = %s AND (b.user_id = %s OR %s = 'admin')""",
        (reference, session['user_id'], session.get('user_role')),
        fetch_one=True
    )
    if not booking:
        flash('Ticket not found or unauthorized.', 'danger')
        return redirect(url_for('my_bookings'))

    passengers = Database.execute_query("SELECT * FROM passengers WHERE booking_id = %s", (booking['id'],))
    dep_dt = datetime.strptime(str(booking['departure_time'])[:19], '%Y-%m-%d %H:%M:%S')
    arr_dt = datetime.strptime(str(booking['arrival_time'])[:19], '%Y-%m-%d %H:%M:%S')
    
    booking['dep_date_formatted'] = dep_dt.strftime('%d %b %Y')
    booking['dep_time_formatted'] = dep_dt.strftime('%H:%M')
    booking['arr_time_formatted'] = arr_dt.strftime('%H:%M')
    booking['boarding_time'] = (dep_dt - timedelta(minutes=45)).strftime('%H:%M')

    return render_template('ticket.html', booking=booking, passengers=passengers)

@app.route('/api/checkin/<reference>', methods=['POST'])
@login_required
def checkin_flight(reference):
    booking = Database.execute_query(
        "SELECT id, booking_status FROM bookings WHERE booking_reference = %s AND user_id = %s",
        (reference, session['user_id']),
        fetch_one=True
    )
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found.'}), 404

    if booking['booking_status'] == 'Cancelled':
        return jsonify({'success': False, 'message': 'Cannot check in for a cancelled flight.'}), 400

    Database.execute_commit(
        "UPDATE bookings SET booking_status = 'Checked-In' WHERE id = %s",
        (booking['id'],)
    )

    return jsonify({
        'success': True,
        'message': 'Check-in successful! Your digital boarding pass has been issued.',
        'status': 'Checked-In'
    })

@app.route('/api/cancel-booking/<reference>', methods=['POST'])
@login_required
def cancel_booking(reference):
    booking = Database.execute_query(
        "SELECT id, booking_status, total_fare FROM bookings WHERE booking_reference = %s AND user_id = %s",
        (reference, session['user_id']),
        fetch_one=True
    )
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found.'}), 404

    if booking['booking_status'] == 'Cancelled':
        return jsonify({'success': False, 'message': 'Booking is already cancelled.'}), 400

    # Get all assigned seat IDs to release them
    passengers = Database.execute_query("SELECT seat_id FROM passengers WHERE booking_id = %s", (booking['id'],))
    for p in passengers:
        if p['seat_id']:
            Database.execute_commit("UPDATE seats SET is_occupied = 0 WHERE id = %s", (p['seat_id'],))

    # Mark booking cancelled
    Database.execute_commit(
        "UPDATE bookings SET booking_status = 'Cancelled' WHERE id = %s",
        (booking['id'],)
    )

    refund_amount = round(float(booking['total_fare']) * 0.90, 2) # 10% standard cancellation fee

    return jsonify({
        'success': True,
        'message': f'Booking {reference} has been successfully cancelled. A refund of ₹{refund_amount:,.2f} has been processed.',
        'refund_amount': refund_amount
    })

# ==========================================
# ADMIN MANAGEMENT PANEL
# ==========================================

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Overall statistics
    total_flights = Database.execute_query("SELECT COUNT(*) as cnt FROM flights", fetch_one=True)['cnt']
    total_bookings = Database.execute_query("SELECT COUNT(*) as cnt FROM bookings", fetch_one=True)['cnt']
    total_revenue = Database.execute_query("SELECT COALESCE(SUM(total_fare), 0) as rev FROM bookings WHERE booking_status != 'Cancelled'", fetch_one=True)['rev']
    total_users = Database.execute_query("SELECT COUNT(*) as cnt FROM users", fetch_one=True)['cnt']

    # Flights table
    flights = Database.execute_query(
        """SELECT f.*, orig.code as origin_code, dest.code as destination_code,
                  (SELECT COUNT(*) FROM seats s WHERE s.flight_id = f.id AND s.is_occupied = 1) as booked_seats,
                  (SELECT COUNT(*) FROM seats s WHERE s.flight_id = f.id) as total_seats
           FROM flights f
           JOIN airports orig ON f.origin_id = orig.id
           JOIN airports dest ON f.destination_id = dest.id
           ORDER BY f.departure_time DESC LIMIT 20"""
    )

    # Recent bookings
    recent_bookings = Database.execute_query(
        """SELECT b.*, u.full_name as passenger_name, u.email, f.flight_number
           FROM bookings b
           JOIN users u ON b.user_id = u.id
           JOIN flights f ON b.flight_id = f.id
           ORDER BY b.booking_date DESC LIMIT 10"""
    )

    airports = Database.execute_query("SELECT * FROM airports ORDER BY city ASC")

    return render_template(
        'admin.html',
        stats={
            'flights': total_flights,
            'bookings': total_bookings,
            'revenue': total_revenue,
            'users': total_users
        },
        flights=flights,
        bookings=recent_bookings,
        airports=airports
    )

@app.route('/admin/flight/status', methods=['POST'])
@admin_required
def update_flight_status():
    flight_id = request.form.get('flight_id')
    new_status = request.form.get('status')
    gate = request.form.get('gate')

    Database.execute_commit(
        "UPDATE flights SET status = %s, gate = %s WHERE id = %s",
        (new_status, gate, flight_id)
    )
    flash(f'Flight status updated to {new_status}.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/flight/add', methods=['POST'])
@admin_required
def add_flight():
    flight_number = request.form.get('flight_number', '').strip().upper()
    airline_name = request.form.get('airline_name', 'AirScan').strip() or 'AirScan'
    origin_id = request.form.get('origin_id')
    destination_id = request.form.get('destination_id')
    dep_time = request.form.get('departure_time')
    arr_time = request.form.get('arrival_time')
    duration = int(request.form.get('duration_minutes', 120))
    aircraft = request.form.get('aircraft_model', 'Airbus A321neo')
    p_eco = float(request.form.get('economy_price', 4500))
    p_biz = float(request.form.get('business_price', 16000))
    p_first = float(request.form.get('first_price', 32000))
    terminal = request.form.get('terminal', 'T2')
    gate = request.form.get('gate', 'A1')

    fid = Database.execute_commit(
        """INSERT INTO flights 
           (flight_number, airline_name, origin_id, destination_id, departure_time, arrival_time, 
            duration_minutes, aircraft_model, status, economy_price, business_price, first_price, terminal, gate)
           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'On Time', %s, %s, %s, %s, %s)""",
        (flight_number, airline_name, origin_id, destination_id, dep_time, arr_time, duration, aircraft, p_eco, p_biz, p_first, terminal, gate)
    )
    
    # Generate seats
    from seed_data import _generate_flight_seats
    _generate_flight_seats(fid)

    flash(f'Flight {flight_number} ({airline_name}) scheduled with dynamic seat map initialized.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n[AIRSCAN] AirScan Flight Search & Airline Booking Portal starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
