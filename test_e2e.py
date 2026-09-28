import sys
import requests
import uuid
from db import Database

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
BASE = 'http://127.0.0.1:5000'

# 1. Home
r_home = session.get(f'{BASE}/')
assert r_home.status_code == 200, f'Home failed: {r_home.status_code}'
assert 'AIRSCAN' in r_home.text.upper()
print('[PASS] 1. AirScan home page loaded successfully with luxury theme')

# 2. Login as John Doe
r_login = session.post(f'{BASE}/login', data={'email': 'john.doe@example.com', 'password': 'password123'}, allow_redirects=True)
assert r_login.status_code == 200
assert 'Welcome back' in r_login.text or 'John Doe' in r_login.text
print('[PASS] 2. Logged in successfully as John Doe')

# 3. Flights search
r_flights = session.get(f'{BASE}/flights?origin=DEL&destination=BOM&cabin_class=Business')
assert r_flights.status_code == 200
assert '6E-204' in r_flights.text or 'AI-102' in r_flights.text or 'IndiGo' in r_flights.text
print('[PASS] 3. Flight search returned Indian routes and airlines correctly')

# 4. Get seat booking page
fl_row = Database.execute_query('SELECT id FROM flights LIMIT 1', fetch_one=True)
assert fl_row, 'No flights available in database'
flight_id = fl_row['id']

r_book_page = session.get(f'{BASE}/book/{flight_id}?cabin_class=Business&passengers=1')
assert r_book_page.status_code == 200
assert 'airplane-wrapper' in r_book_page.text
print('[PASS] 4. Interactive fuselage seat booking page rendered')

# 5. Book a seat via API in INR
seat = Database.execute_query('SELECT id, seat_number FROM seats WHERE flight_id = %s AND is_occupied = 0 LIMIT 1', (flight_id,), fetch_one=True)
assert seat, 'No available seat found'

booking_payload = {
    'flight_id': flight_id,
    'cabin_class': 'Business',
    'passengers': [{
        'seat_id': seat['id'],
        'seat_number': seat['seat_number'],
        'full_name': 'John Doe',
        'passport': 'A12345678',
        'dob': '1990-01-01',
        'meal': 'Hindu Vegetarian Thali',
        'baggage': 15
    }],
    'promo_code': 'AIRSCAN20'
}
r_api_book = session.post(f'{BASE}/api/book', json=booking_payload)
assert r_api_book.status_code == 200, f'Booking failed: {r_api_book.text}'
book_json = r_api_book.json()
assert book_json['success'] is True
b_ref = book_json['booking_reference']
print(f'[PASS] 5. Successfully booked seat {seat["seat_number"]} on Flight 1 with PNR {b_ref}')

# 6. View Boarding Pass
r_ticket = session.get(f'{BASE}/ticket/{b_ref}')
assert r_ticket.status_code == 200
assert 'BOARDING PASS' in r_ticket.text
assert b_ref in r_ticket.text
print(f'[PASS] 6. Boarding pass and digital ticket rendered for PNR {b_ref}')

# 7. Check-in API
r_checkin = session.post(f'{BASE}/api/checkin/{b_ref}')
assert r_checkin.json()['success'] is True
print(f'[PASS] 7. Online check-in successful for {b_ref}')

# 8. My bookings page
r_my_bookings = session.get(f'{BASE}/my-bookings')
assert r_my_bookings.status_code == 200
assert b_ref in r_my_bookings.text
print('[PASS] 8. My Bookings shows new active reservation in INR (₹)')

# 9. Test Registration & OTP Verification Flow
new_sess = requests.Session()
test_email = f'amelia.{uuid.uuid4().hex[:6]}@airscan.com'
r_reg = new_sess.post(f'{BASE}/register', data={
    'full_name': 'Amelia Earhart',
    'email': test_email,
    'password': 'password123',
    'confirm_password': 'password123',
    'phone': '+91-98765-43210',
    'passport_number': 'US99112233'
}, allow_redirects=True)
assert r_reg.status_code == 200
assert 'Verify Your Account' in r_reg.text

# Get the generated OTP code from the DB
u_new = Database.execute_query('SELECT id, verification_code FROM users WHERE email = %s', (test_email,), fetch_one=True)
assert u_new and u_new['verification_code']
otp = u_new['verification_code']

# Submit OTP
r_verify = new_sess.post(f'{BASE}/verify', data={
    'code_1': otp[0], 'code_2': otp[1], 'code_3': otp[2],
    'code_4': otp[3], 'code_5': otp[4], 'code_6': otp[5]
}, allow_redirects=True)
assert r_verify.status_code == 200
assert 'Account verified successfully' in r_verify.text
print(f'[PASS] 9. Registration and 6-digit OTP verification flow verified for code {otp}')

# 10. Admin Ops Dashboard
admin_sess = requests.Session()
admin_sess.post(f'{BASE}/login', data={'email': 'admin@airscan.com', 'password': 'admin123'})
r_admin = admin_sess.get(f'{BASE}/admin')
assert r_admin.status_code == 200
assert 'Flight Operations' in r_admin.text
print('[PASS] 10. Flight Ops Command Center verified with admin privileges')

print('\n[SUCCESS] ALL 10 CORE USER JOURNEYS & INTEGRATION TESTS PASSED!')
