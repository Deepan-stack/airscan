# ✈️ AirScan — Flight Search & Airline Reservation System

A full-stack, enterprise-grade Airline Reservation Website featuring comprehensive multi-carrier flight search across Indian & international routes, Indian Rupee (₹ / INR) dynamic pricing, 2D aircraft fuselage cabin seat booking, digital boarding pass generation, ticket cancellation with refunds, user authentication with 6-digit OTP verification, and flight operations admin dispatch.

Built with **Python Flask**, **MySQL** (with seamless auto-fallback to **SQLite**), and **Modern HTML5 / Vanilla CSS3 / JavaScript**.

---

## 🌟 Key Features

### 1. 🛫 Flight Discovery & Multi-Airline Carrier Search
- **Extensive Airport Network (33+ Airports)**:
  - **Indian Metros & Regional Hubs (22)**: New Delhi (DEL), Mumbai (BOM), Bengaluru (BLR), Hyderabad (HYD), Chennai (MAA), Kolkata (CCU), Ahmedabad (AMD), Pune (PNQ), Goa Dabolim (GOI), Goa Mopa (GOX), Kochi (COK), Jaipur (JAI), Lucknow (LKO), Thiruvananthapuram (TRV), Guwahati (GAU), Varanasi (VNS), Amritsar (ATQ), Srinagar (SXR), Chandigarh (IXC), Patna (PAT), Bhubaneswar (BBI), Indore (IDR).
  - **International Gateways (11)**: Dubai (DXB), Singapore (SIN), London Heathrow (LHR), New York (JFK), Frankfurt (FRA), Doha (DOH), Bangkok (BKK), Paris Charles de Gaulle (CDG), Tokyo Haneda (HND), Abu Dhabi (AUH), Sydney (SYD).
- **Major Domestic & Global Airlines**:
  - IndiGo (`6E`), Air India (`AI`), Vistara (`UK`), Akasa Air (`QP`), SpiceJet (`SG`), Air India Express (`IX`), Emirates (`EK`), Singapore Airlines (`SQ`), Qatar Airways (`QR`), British Airways (`BA`), Lufthansa (`LH`), Etihad Airways (`EY`).
- **Real-Time Client-Side Filters**:
  - **Airline Carrier Filter**: Filter instantly by airline (e.g. IndiGo, Air India, Emirates, Singapore Airlines, etc.).
  - **Live INR Price Slider**: Dynamic filtering from ₹2,000 to ₹2,50,000+.
  - **Cabin Switcher**: Real-time price switching between Economy, Business, and First Class.
  - **Non-stop / Direct Flights Toggle**: Quick filter for point-to-point flights.
  - **Sorting**: Instant sorting by lowest fare or shortest duration.

### 2. 💺 Interactive 2D Aircraft Fuselage Seat Map
- **Fuselage Cabin Layout**:
  - Cockpit flight deck nose cone with glowing radar indicators (`AIRSCAN CABIN`).
  - **First Class Private Suites** (Rows 1–2): 1-2-1 layout, gold foil border, reclining bed mode.
  - **Business Class Lie-Flat Pods** (Rows 3–6): 2-2 layout, electric cyan accents.
  - **Economy Seating** (Rows 10–20): 3-3 configuration with exit row extra-legroom indicators (`★ Extra Legroom`).
- **Dynamic Add-Ons in Indian Rupees (₹)**:
  - Seat upgrades with transparent fare breakdown.
  - In-flight meals: Masala Dosa, Paneer Tikka, Butter Chicken, Continental Breakfast, etc.
  - Baggage allowance: Priority 32kg add-on (+ ₹1,200).
  - Promotional discount codes: `AIRSCAN20` (20% off) and `AIRSCAN500` (₹500 flat discount).

### 3. 🎫 Boarding Pass & Ticket Management
- **Authentic Digital Boarding Pass**:
  - Display airline carrier name, flight number, and PNR (format: `AS-XXXXX`).
  - Perforated tear-off stub line with notch cutouts.
  - Vector QR code and simulated high-density boarding barcode.
  - Dedicated **Print / Save as PDF** stylesheet (`@media print`).
- **Online Web Check-In**: One-click check-in simulation with confirmed status.
- **Ticket Cancellation & Refunds**: Automatic 90% refund calculation in Indian Rupees (₹) with instant seat release.

### 4. 🔐 Security, Authentication & Verification
- User registration with Full Name, Email, Password, Mobile Phone, and Passport Number.
- **6-Digit OTP Email Verification**:
  - Auto-advancing digit inputs with backspace and paste support.
  - Built-in **Simulated Inbox preview** and **Auto-Fill** for seamless testing.
  - Resend Code API with 60-second cooldown timer.
- Secure password hashing using PBKDF2 / Werkzeug security.
- Frequent flyer loyalty tier tracking: Earn 1 AirScan SkyMile per ₹10 spent.

### 5. 🛡️ Flight Operations Admin Dispatch
- Real-time KPI dashboard: Total Revenue (₹), Active Flights, Confirmed Bookings, and Club Members.
- Airline dispatch form: Schedule new flights under any airline carrier with base fares in ₹.
- Fleet status controller: Toggle flight statuses (`On Time`, `Boarding`, `Delayed`, `Departed`).

---

## 🗄️ Database Architecture (MySQL + Auto-Fallback)

The system supports **MySQL** and provides **`schema_mysql.sql`** for phpMyAdmin / MySQL CLI imports.

If MySQL is not currently running locally, `db.py` automatically falls back to **SQLite (`airline.db`)** within milliseconds, ensuring immediate, zero-friction execution.

### To configure MySQL (Optional):
Set your environment variables (or create a `.env` file):
```bash
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=airline_db
USE_SQLITE=false
```

---

## 🚀 Quick Start Guide

### 1. Install Requirements
```bash
pip install -r requirements.txt
```

### 2. Initialize Database & Seed 33 Airports & 94 Flights
```bash
python seed_data.py
```

### 3. Start the Web Server
```bash
python app.py
```
Open your browser to: **`http://localhost:5000`**

### 4. Run End-to-End Tests
```bash
python test_e2e.py
```

---

## 🔑 Demo Accounts

| Role | Email | Password | Details |
|---|---|---|---|
| **Passenger** | `john.doe@example.com` | `password123` | Active booking, 34,500 SkyMiles |
| **Admin / Ops** | `admin@airscan.com` | `admin123` | Full Flight Ops & Revenue Dispatch |
| **Admin (Legacy)** | `admin@aerolux.com` | `admin123` | Full Flight Ops & Revenue Dispatch |
| **New User** | `newbie@example.com` | `password123` | Unverified test account (Code: 849201) |

---

## 🏷️ Active Promo Codes

- **`AIRSCAN20`**: 20% discount on total flight fare
- **`AIRSCAN500`**: Flat ₹500 discount
- **`FLYLUX20`**: Legacy 20% discount
- **`FIRSTFLY`**: Legacy discount
