"""
Hari Marg — Your Digital Companion for the Wari Pilgrimage
Flask Backend Application
"""

import os
import json
import sqlite3
import tempfile
from datetime import datetime
from io import BytesIO

from flask import (
    Flask, render_template, request, jsonify, send_file, session, redirect, url_for
)
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SESSION_SECRET_KEY') or 'hari-marg-session-key-fallback-2026'

# --- Configuration ---
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

DATABASE = os.path.join(os.path.dirname(__file__), 'hari_marg.db')
AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'static', 'audio')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'photos')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '')

# --- Supabase Production DB & Storage Configuration ---
SUPABASE_URL = os.getenv('SUPABASE_URL', '')
SUPABASE_SECRET_KEY = os.getenv('SUPABASE_SECRET_KEY', '')
SUPABASE_STORAGE_BUCKET = os.getenv('SUPABASE_STORAGE_BUCKET', 'hari-marg-photos')
POSTGRES_URL = os.getenv('DATABASE_URL', '')
VOLUNTEER_SECRET_CODE = os.getenv('VOLUNTEER_SECRET_CODE', 'WARI-VOL-2026')

# Ensure required directories exist
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================
# EMAIL HELPER
# ============================================
def send_email(to_email, subject, body):
    """Send an email using SMTP credentials from environment or fallback to console log."""
    mail_server = os.getenv('MAIL_SERVER', '')
    mail_port = int(os.getenv('MAIL_PORT', '587'))
    mail_user = os.getenv('MAIL_USERNAME', '')
    mail_pass = os.getenv('MAIL_PASSWORD', '')
    sender = os.getenv('MAIL_DEFAULT_SENDER', mail_user or 'noreply@harimarg.org')

    if mail_server and mail_user and mail_pass:
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(mail_server, mail_port)
            server.starttls()
            server.login(mail_user, mail_pass)
            server.send_message(msg)
            server.quit()
            print(f'[Email System] Successfully sent email to {to_email}')
            return True
        except Exception as e:
            print(f'[Email Error] Failed to send email to {to_email}: {e}')
            return False
    else:
        print(f'[Email Log (Dev Mode)] To: {to_email} | Subject: {subject}\nBody:\n{body}')
        return True


# ============================================
# DATABASE
# ============================================
def get_db():
    """Get a database connection (Supabase PostgreSQL with fallback to SQLite)."""
    if POSTGRES_URL:
        try:
            import psycopg2
            from psycopg2.extras import DictCursor
            conn = psycopg2.connect(POSTGRES_URL)
            conn.cursor_factory = DictCursor
            return conn
        except Exception as e:
            print(f'[DB Warning] Could not connect to Supabase PostgreSQL: {e}. Falling back to SQLite.')
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def is_pg(conn):
    """Return True if connection is PostgreSQL."""
    return not isinstance(conn, sqlite3.Connection)


def init_db():
    """Initialize database tables and seed default dindis if empty."""
    conn = get_db()
    if not isinstance(conn, sqlite3.Connection):
        print('[Supabase DB] Running on PostgreSQL production database.')
        conn.close()
        return

    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS dindis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palkhi_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            name_mr TEXT,
            leader TEXT,
            leader_mr TEXT,
            members INTEGER DEFAULT 0,
            lat REAL,
            lng REAL,
            current_halt TEXT,
            current_halt_mr TEXT,
            status TEXT DEFAULT 'halt',
            status_label TEXT,
            status_label_mr TEXT,
            next_destination TEXT,
            next_destination_mr TEXT,
            day INTEGER DEFAULT 1,
            route TEXT DEFAULT 'alandi',
            color TEXT DEFAULT '#E8703A',
            admin_name TEXT,
            contact TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS dindi_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palkhi_id TEXT NOT NULL,
            name TEXT NOT NULL,
            age INTEGER,
            health_note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            palkhi_id TEXT NOT NULL,
            role TEXT DEFAULT 'palkhi_admin',
            is_approved INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS dindi_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            palkhi_id TEXT NOT NULL,
            photo_url TEXT NOT NULL,
            caption TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dindi_id INTEGER,
            family_code TEXT,
            latitude REAL,
            longitude REAL,
            current_halt TEXT,
            status_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (dindi_id) REFERENCES dindis(id)
        );

        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            image_url TEXT,
            audio_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS seva_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            provider_name TEXT,
            contact TEXT,
            location_name TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS main_palkhi (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            palkhi_name TEXT NOT NULL,
            palkhi_name_mr TEXT,
            current_location_name TEXT,
            current_location_name_mr TEXT,
            lat REAL,
            lng REAL,
            day INTEGER DEFAULT 1,
            status TEXT,
            status_mr TEXT,
            next_destination TEXT,
            next_destination_mr TEXT,
            route TEXT DEFAULT 'alandi',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            passcode TEXT NOT NULL,
            status TEXT DEFAULT 'approved',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()

    # Add last_updated column if missing (migration)
    try:
        cursor.execute('ALTER TABLE dindis ADD COLUMN last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        conn.commit()
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute('ALTER TABLE seva_requests ADD COLUMN description TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # Reseed if empty or using legacy PALKHI- IDs
    count = cursor.execute('SELECT COUNT(*) FROM dindis').fetchone()[0]
    legacy = cursor.execute("SELECT COUNT(*) FROM dindis WHERE palkhi_id LIKE 'PALKHI-%'").fetchone()[0]
    if count == 0 or legacy > 0:
        if legacy > 0:
            cursor.execute('DELETE FROM dindi_members')
            cursor.execute('DELETE FROM dindi_photos')
            cursor.execute('DELETE FROM dindis')
            conn.commit()
    if count == 0 or legacy > 0:
        dindis_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'dindis.json')
        if os.path.exists(dindis_path):
            with open(dindis_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for d in data.get('dindis', []):
                    cursor.execute('''
                        INSERT INTO dindis (
                            palkhi_id, name, name_mr, leader, leader_mr, members,
                            lat, lng, current_halt, current_halt_mr, status,
                            status_label, status_label_mr, next_destination,
                            next_destination_mr, day, route, color, admin_name
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        d.get('palkhi_id', f"PALKHI-00{d.get('id', '1')[-1]}"),
                        d.get('name'), d.get('name_mr'),
                        d.get('leader'), d.get('leader_mr'),
                        d.get('members', 100),
                        d.get('lat'), d.get('lng'),
                        d.get('current_halt'), d.get('current_halt_mr'),
                        d.get('status', 'halt'),
                        d.get('status_label'), d.get('status_label_mr'),
                        d.get('next_destination'), d.get('next_destination_mr'),
                        d.get('day', 1), d.get('route', 'alandi'),
                        d.get('color', '#E8703A'),
                        d.get('leader', 'Admin')
                    ))
            conn.commit()

    # Seed sample members if empty
    m_count = cursor.execute('SELECT COUNT(*) FROM dindi_members').fetchone()[0]
    if m_count == 0:
        sample_members = [
            ('HM-001', 'Panditrao Deshmukh', 58, 'Healthy — Dindi Leader'),
            ('HM-001', 'Shantabai Shinde', 65, 'Mild Hypertension — Needs frequent water breaks'),
            ('HM-001', 'Ramesh Gaitonde', 42, 'Feet Blisters — Under treatment at medical camp'),
            ('HM-002', 'Babasaheb Patil', 60, 'Healthy — Group Commander'),
            ('HM-002', 'Savitri Patil', 55, 'Diabetic — Carries ORS & glucose packets'),
            ('HM-042', 'Namdev More', 52, 'Healthy — Active walker'),
            ('HM-042', 'Laxmi More', 48, 'Asthma — Inhaler carried'),
        ]
        cursor.executemany('''
            INSERT INTO dindi_members (palkhi_id, name, age, health_note)
            VALUES (?, ?, ?, ?)
        ''', sample_members)
        conn.commit()

    # Seed sample gallery photos if empty
    p_count = cursor.execute('SELECT COUNT(*) FROM dindi_photos').fetchone()[0]
    if p_count == 0:
        sample_photos = [
            ('HM-001', 'https://images.unsplash.com/photo-1605649487212-47bdab064df7?w=400&q=80', 'Morning bhajan at Saswad'),
            ('HM-001', 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=400&q=80', 'Afternoon prasad distribution'),
            ('HM-002', 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80', 'Walking towards Walhe'),
            ('HM-042', 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=400&q=80', 'Night halt at Lonand'),
            ('HM-042', 'https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=400&q=80', 'Group photo at medical camp'),
        ]
        cursor.executemany('''
            INSERT INTO dindi_photos (palkhi_id, photo_url, caption)
            VALUES (?, ?, ?)
        ''', sample_photos)
        conn.commit()

    # Seed sample seva if empty
    s_count = cursor.execute('SELECT COUNT(*) FROM seva_requests').fetchone()[0]
    if s_count == 0:
        sample_seva = [
            ('food', 'Shri Vitthal Annadan Kendra', '9876543210', 'Saswad Phata', 'Free hot meals for 500+ Warkaris daily', 18.3419, 74.0198),
            ('water', 'Jal Seva Samiti', '9876543211', 'Jejuri Bus Stand', '24/7 ORS and drinking water distribution', 18.2764, 74.1614),
            ('medical', 'Red Cross Medical Camp', '108', 'Lonand Main Road', 'Free first aid, blister treatment, BP check', 17.9333, 74.1500),
            ('rest', 'Warkari Vishram Gruh', '9876543212', 'Walhe Village', 'Covered rest area with mats and blankets', 18.1234, 74.0567),
            ('sanitation', 'Swachh Wari Initiative', '9876543213', 'Phaltan Chowk', 'Clean washrooms and bathing facilities', 17.9922, 74.4306),
        ]
        cursor.executemany('''
            INSERT INTO seva_requests (type, provider_name, contact, location_name, description, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', sample_seva)
        conn.commit()

    # Seed main palkhi if empty
    mp_count = cursor.execute('SELECT COUNT(*) FROM main_palkhi').fetchone()[0]
    if mp_count == 0:
        palkhi_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'palkhi.json')
        if os.path.exists(palkhi_path):
            with open(palkhi_path, 'r', encoding='utf-8') as f:
                p = json.load(f)
            cursor.execute('''
                INSERT INTO main_palkhi (
                    id, palkhi_name, palkhi_name_mr, current_location_name, current_location_name_mr,
                    lat, lng, day, status, status_mr, next_destination, next_destination_mr, route
                ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                p.get('palkhi_name'), p.get('palkhi_name_mr'),
                p.get('current_location_name'), p.get('current_location_name_mr'),
                p.get('lat'), p.get('lng'), p.get('day', 1),
                p.get('status'), p.get('status_mr'),
                p.get('next_destination'), p.get('next_destination_mr'), 'alandi'
            ))
            conn.commit()

    conn.close()


def normalize_palkhi_id(raw_id):
    """Normalize user input to HM-XXX format."""
    if not raw_id:
        return ''
    pid = raw_id.strip().upper()
    if pid.startswith('PALKHI-'):
        num = pid.replace('PALKHI-', '').lstrip('0') or '0'
        pid = f'HM-{num.zfill(3)}'
    elif pid.startswith('HM') and not pid.startswith('HM-'):
        pid = 'HM-' + pid[2:].lstrip('-')
    return pid


# Initialize DB on startup
init_db()


def get_dindis_from_db(user_lat=None, user_lng=None):
    """Retrieve all dindis from SQLite database."""
    conn = get_db()
    rows = conn.execute('SELECT * FROM dindis ORDER BY id ASC').fetchall()
    conn.close()

    dindis = []
    for r in rows:
        d = dict(r)
        d['id'] = d.get('palkhi_id', f"dindi-{d['id']}")
        if user_lat is not None and user_lng is not None:
            dist = haversine_km(user_lat, user_lng, d['lat'], d['lng'])
            d['distance_km'] = round(dist, 2)
            if dist < 1.0:
                d['distance_text'] = f"{int(dist * 1000)} meters"
            else:
                d['distance_text'] = f"{round(dist, 1)} km"
        dindis.append(d)
    return dindis


# ============================================
# PAGE ROUTES
# ============================================
@app.route('/')
def home():
    """Home / Dashboard page."""
    weather_data = get_mock_weather()
    return render_template('index.html', weather=weather_data)


@app.route('/route')
def route_page():
    """Palkhi Route Map page."""
    return render_template('route.html')


@app.route('/near_me')
def near_me():
    """Near Me — nearby facilities."""
    return render_template('near_me.html')


@app.route('/weather')
def weather_page():
    """Weather Advisory page."""
    return render_template('weather.html')


@app.route('/profile')
def profile():
    """User profile page."""
    return render_template('profile.html')


@app.route('/chat')
def chat_page():
    """Redirect legacy chat to emergency tips."""
    return redirect('/emergency')


@app.route('/emergency')
def emergency_page():
    """AI Emergency Tips — fast bullet-point guidance."""
    return render_template('emergency.html')


@app.route('/main_palkhi')
def main_palkhi_page():
    """Main ceremonial Palkhi tracking page."""
    return render_template('main_palkhi.html')


@app.route('/track')
def track_page():
    """Public Palkhi ID lookup — no login required."""
    return render_template('track.html')


@app.route('/seva')
def seva_page():
    """Seva & Daan Network page."""
    return render_template('seva.html')


@app.route('/gallery')
def gallery_page():
    """Photo Gallery page."""
    return render_template('gallery.html')


@app.route('/certificate')
def certificate_page():
    """Certificate of Completion page."""
    return render_template('certificate.html')


@app.route('/demo')
def demo_page():
    """Interactive demo mobile view."""
    return render_template('demo.html')


# ============================================
# API: NEARBY FACILITIES (Haversine Formula)
# ============================================
import math

def haversine_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates in kilometers using Haversine formula."""
    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@app.route('/api/nearby')
def api_nearby():
    """Return N nearest facilities relative to provided lat/lng, optionally filtered by category."""
    try:
        user_lat = float(request.args.get('lat', 18.5204))  # Default Pune
        user_lng = float(request.args.get('lng', 73.8567))
        category = request.args.get('category', 'all').strip().lower()
        limit = int(request.args.get('limit', 5))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid lat/lng or parameters'}), 400

    facilities_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'facilities.json')
    if not os.path.exists(facilities_path):
        return jsonify({'facilities': [], 'count': 0})

    with open(facilities_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    facilities = data.get('facilities', [])

    # Map aliases for categories (e.g. washroom -> sanitation)
    category_map = {
        'washroom': 'sanitation',
        'toilet': 'sanitation',
        'rest': 'rest',
        'halt': 'rest',
        'food': 'food',
        'annadan': 'food',
        'water': 'water',
        'medical': 'medical',
        'hospital': 'medical',
    }
    target_category = category_map.get(category, category)

    # Filter by category if not 'all'
    if target_category and target_category != 'all':
        facilities = [item for item in facilities if item.get('category') == target_category]

    # Calculate distance for each facility
    results = []
    for item in facilities:
        dist = haversine_km(user_lat, user_lng, item['lat'], item['lng'])
        item_copy = dict(item)
        item_copy['distance_km'] = round(dist, 2)
        if dist < 1.0:
            item_copy['distance_text'] = f"{int(dist * 1000)} meters"
        else:
            item_copy['distance_text'] = f"{round(dist, 1)} km"
        results.append(item_copy)

    # Sort ascending by distance
    results.sort(key=lambda x: x['distance_km'])

    # Cap at limit
    top_results = results[:limit]

    return jsonify({
        'user_lat': user_lat,
        'user_lng': user_lng,
        'category': category,
        'count': len(top_results),
        'facilities': top_results
    })


# ============================================
# API: WEATHER
# ============================================
@app.route('/api/weather')
def api_weather():
    """Fetch weather data from OpenWeatherMap or return mock data."""
    import requests as req

    lat = request.args.get('lat', '18.5204')  # Default: Pune
    lng = request.args.get('lng', '73.8567')

    if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != 'your_openweather_api_key_here':
        try:
            # Current weather
            url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={OPENWEATHER_API_KEY}&units=metric'
            resp = req.get(url, timeout=10)
            data = resp.json()

            current = {
                'temp': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'].title(),
                'main': data['weather'][0]['main'],
                'wind': round(data['wind']['speed'] * 3.6, 1),  # m/s to km/h
                'rain': data.get('rain', {}).get('1h', 0),
                'location': data.get('name', 'Pune Region'),
            }

            # Generate alert and advisory
            alert = generate_weather_alert(current)
            current['alert'] = alert

            # Forecast for route stops
            route_stops = [
                {'name': 'Saswad', 'lat': 18.3454, 'lng': 74.0315},
                {'name': 'Jejuri', 'lat': 18.2709, 'lng': 74.1603},
                {'name': 'Lonand', 'lat': 18.0000, 'lng': 74.1900},
                {'name': 'Phaltan', 'lat': 17.9833, 'lng': 74.4333},
                {'name': 'Pandharpur', 'lat': 17.6780, 'lng': 75.3260},
            ]

            forecast = []
            for stop in route_stops:
                try:
                    furl = f'https://api.openweathermap.org/data/2.5/weather?lat={stop["lat"]}&lon={stop["lng"]}&appid={OPENWEATHER_API_KEY}&units=metric'
                    fresp = req.get(furl, timeout=5)
                    fdata = fresp.json()
                    forecast.append({
                        'location': stop['name'],
                        'temp': fdata['main']['temp'],
                        'main': fdata['weather'][0]['main'],
                        'description': fdata['weather'][0]['description'].title(),
                        'rain': fdata.get('rain', {}).get('1h', 0),
                    })
                except Exception:
                    forecast.append({
                        'location': stop['name'],
                        'temp': 28,
                        'main': 'Clouds',
                        'description': 'Partly Cloudy',
                        'rain': 0,
                    })

            return jsonify({'current': current, 'forecast': forecast})

        except Exception as e:
            pass

    # Mock fallback
    mock = get_mock_weather()
    mock_current = {
        'temp': mock['temp'],
        'humidity': 78,
        'description': mock['description'],
        'main': 'Clouds',
        'wind': 12,
        'rain': 3,
        'location': mock['location'],
    }
    mock_current['alert'] = generate_weather_alert(mock_current)
    return jsonify({
        'current': mock_current,
        'forecast': []
    })


def get_mock_weather():
    """Return mock weather data for demo purposes."""
    return {
        'temp': 28,
        'description': 'Partly Cloudy',
        'location': 'Pune Region',
        'safety_class': 'caution',
        'safety_label': '⚠️ Monsoon Active',
    }


def generate_weather_alert(weather_data):
    """Generate alert banner and one-line advisory based on weather thresholds."""
    temp = weather_data.get('temp', 25)
    rain = weather_data.get('rain', 0)
    main = (weather_data.get('main', '') or '').lower()
    desc = (weather_data.get('description', '') or '').lower()
    wind = weather_data.get('wind', 0)
    humidity = weather_data.get('humidity', 50)

    alert = {
        'has_alert': False,
        'type': 'none',
        'banner_text': '',
        'banner_text_mr': '',
        'advisory': '',
        'advisory_mr': '',
        'severity': 'safe',
    }

    # HEAT ALERT: >35°C
    if temp > 35:
        alert['has_alert'] = True
        alert['type'] = 'heat'
        alert['severity'] = 'danger' if temp > 40 else 'caution'
        if temp > 40:
            alert['banner_text'] = f'🔴 EXTREME HEAT ALERT — {round(temp)}°C'
            alert['banner_text_mr'] = f'🔴 अत्यंत उष्णतेचा इशारा — {round(temp)}°C'
            alert['advisory'] = 'Extreme heat — avoid walking between 11 AM to 4 PM. Drink ORS and rest in shade.'
            alert['advisory_mr'] = 'अत्यंत उष्णता — सकाळी ११ ते दुपारी ४ वाजेपर्यंत चालणे टाळा. ORS प्या आणि सावलीत विश्रांती घ्या.'
        else:
            alert['banner_text'] = f'🟡 HEAT WARNING — {round(temp)}°C'
            alert['banner_text_mr'] = f'🟡 उष्णतेचा इशारा — {round(temp)}°C'
            alert['advisory'] = f'Heavy heat expected — rest before 2 PM. Carry extra water and wear light clothes.'
            alert['advisory_mr'] = f'तीव्र उष्णता अपेक्षित — दुपारी २ च्या आधी विश्रांती घ्या. अतिरिक्त पाणी ठेवा.'

    # RAIN ALERT: rain expected or rainy conditions
    elif main in ('rain', 'drizzle', 'thunderstorm') or rain > 2:
        alert['has_alert'] = True
        alert['type'] = 'rain'
        if main == 'thunderstorm' or rain > 15:
            alert['severity'] = 'danger'
            alert['banner_text'] = '🔴 THUNDERSTORM ALERT — Seek shelter immediately'
            alert['banner_text_mr'] = '🔴 वादळाचा इशारा — तात्काळ सुरक्षित ठिकाणी जा'
            alert['advisory'] = 'Heavy rain & thunderstorm — stop walking, seek permanent shelter. Avoid open fields.'
            alert['advisory_mr'] = 'मुसळधार पाऊस आणि वादळ — चालणे थांबवा, कायमस्वरूपी आश्रय घ्या. मोकळ्या मैदानात जाऊ नका.'
        else:
            alert['severity'] = 'caution'
            alert['banner_text'] = f'🟡 RAIN EXPECTED — {round(rain, 1)} mm/hr'
            alert['banner_text_mr'] = f'🟡 पाऊस अपेक्षित — {round(rain, 1)} मिमी/तास'
            alert['advisory'] = 'Rain on route — carry raincoat and waterproof your belongings. Walk carefully on wet roads.'
            alert['advisory_mr'] = 'मार्गावर पाऊस — रेनकोट घ्या आणि सामान निरोगी ठेवा. ओल्या रस्त्यावर सावधगिरीने चाला.'

    # HIGH WIND WARNING
    elif wind > 40:
        alert['has_alert'] = True
        alert['type'] = 'wind'
        alert['severity'] = 'caution'
        alert['banner_text'] = f'🟡 HIGH WIND — {round(wind)} km/h'
        alert['banner_text_mr'] = f'🟡 जोरदार वारा — {round(wind)} किमी/तास'
        alert['advisory'] = 'Strong winds — secure loose items and walk in groups. Avoid areas with trees.'
        alert['advisory_mr'] = 'जोरदार वारा — सैल वस्तू सुरक्षित करा आणि गटात चाला. झाडांजवळ जाऊ नका.'

    # Safe conditions — still provide an advisory
    else:
        alert['advisory'] = 'Weather is favorable for walking. Stay hydrated and enjoy the Wari! 🏃'
        alert['advisory_mr'] = 'चालण्यासाठी हवामान अनुकूल आहे. हायड्रेटेड रहा आणि वारीचा आनंद घ्या! 🏃'

    return alert


# Route segments for AI weather recommendations
ROUTE_SEGMENTS = [
    {'name': 'Saswad', 'name_mr': 'सासवड', 'lat': 18.3454, 'lng': 74.0315},
    {'name': 'Jejuri', 'name_mr': 'जेजुरी', 'lat': 18.2709, 'lng': 74.1603},
    {'name': 'Walhe', 'name_mr': 'वाल्हे', 'lat': 18.1234, 'lng': 74.0567},
    {'name': 'Lonand', 'name_mr': 'लोणंद', 'lat': 18.0000, 'lng': 74.1900},
    {'name': 'Phaltan', 'name_mr': 'फलटण', 'lat': 17.9833, 'lng': 74.4333},
    {'name': 'Pandharpur', 'name_mr': 'पंढरपूर', 'lat': 17.6780, 'lng': 75.3260},
]

NEAREST_HALTS = {
    'Saswad': 'Saswad Vishram Gruh',
    'Jejuri': 'Jejuri Annadan Kendra',
    'Walhe': 'Walhe Village Halt',
    'Lonand': 'Lonand Medical Camp',
    'Phaltan': 'Phaltan Rest Area',
    'Pandharpur': 'Pandharpur Main Halt',
}


@app.route('/api/weather/ai-recommendation')
def api_weather_ai_recommendation():
    """Generate AI-based route/timing recommendation blending weather + route data."""
    import requests as req

    lat = request.args.get('lat', '18.5204')
    lng = request.args.get('lng', '73.8567')
    lang = request.args.get('lang', 'en')

    weather_data = None
    if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != 'your_openweather_api_key_here':
        try:
            url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={OPENWEATHER_API_KEY}&units=metric'
            resp = req.get(url, timeout=10)
            weather_data = resp.json()
        except Exception:
            pass

    if weather_data:
        current = {
            'temp': weather_data['main']['temp'],
            'humidity': weather_data['main']['humidity'],
            'description': weather_data['weather'][0]['description'].title(),
            'main': weather_data['weather'][0]['main'],
            'wind': round(weather_data['wind']['speed'] * 3.6, 1),
            'rain': weather_data.get('rain', {}).get('1h', 0),
            'location': weather_data.get('name', 'Pune Region'),
        }
    else:
        current = {
            'temp': 28, 'humidity': 78, 'description': 'Partly Cloudy',
            'main': 'Clouds', 'wind': 12, 'rain': 3, 'location': 'Pune Region',
        }

    alert = generate_weather_alert(current)
    segment = ROUTE_SEGMENTS[2]  # Walhe as default context
    nearest_halt = NEAREST_HALTS.get(segment['name'], 'nearest halt point')

    weather_context = (
        f"Current weather at {current['location']}: {current['temp']}°C, "
        f"{current['description']}, humidity {current['humidity']}%, "
        f"wind {current['wind']} km/h, rain {current.get('rain', 0)} mm/hr. "
        f"Alert type: {alert.get('type', 'none')}. "
        f"Route segment focus: {segment['name']} stretch. "
        f"Nearest recommended halt: {nearest_halt}."
    )

    if GROQ_API_KEY and GROQ_API_KEY != 'your_groq_api_key_here':
        try:
            system_prompt = """You are a Wari pilgrimage route advisor. Given weather and route data, produce ONE specific, actionable recommendation (2-3 sentences max) about route timing and safety. Mention specific stretch names and halt points. Be direct — no greetings."""
            user_prompt = f"Weather context: {weather_context}\nGive a route/timing recommendation for Warkaris walking today."
            if lang == 'mr':
                user_prompt += " Respond in Marathi."

            headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
            payload = {
                'model': 'llama-3.3-70b-versatile',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_prompt},
                ],
                'temperature': 0.5,
                'max_tokens': 200,
            }
            resp = req.post('https://api.groq.com/openai/v1/chat/completions',
                            headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                recommendation = resp.json()['choices'][0]['message']['content'].strip()
                return jsonify({
                    'recommendation': recommendation,
                    'source': 'ai',
                    'weather': current,
                    'alert': alert,
                })
        except Exception as e:
            print(f'Groq weather AI error: {e}')

    # Mock fallback recommendations
    temp = current['temp']
    rain = current.get('rain', 0)
    if rain > 5 or current['main'] in ('Rain', 'Thunderstorm'):
        rec = f"Heavy rain expected on the {segment['name']} stretch — consider delaying departure by 1 hour. Recommended halt: {nearest_halt} until conditions improve."
        if lang == 'mr':
            rec = f"{segment['name_mr']} मार्गावर जोरदार पाऊस अपेक्षित — प्रस्थान १ तास लांब करा. {nearest_halt} येथे थांबण्याची शिफारस."
    elif temp > 35:
        rec = f"High heat after 12pm — recommended halt: {nearest_halt} before 1pm. Start walking early morning and carry extra ORS."
        if lang == 'mr':
            rec = f"दुपारी १२ नंतर तीव्र उष्णता — {nearest_halt} येथे दुपारी १ च्या आधी विश्रांती घ्या. सकाळी लवकर चालणे सुरू करा."
    else:
        rec = f"Weather is favorable for the {segment['name']} stretch. Depart before 10am and plan a rest break at {nearest_halt} around noon."
        if lang == 'mr':
            rec = f"{segment['name_mr']} मार्गासाठी हवामान अनुकूल. सकाळी १० पूर्वी प्रस्थान करा आणि {nearest_halt} येथे दुपारी विश्रांती घ्या."

    return jsonify({'recommendation': rec, 'source': 'mock', 'weather': current, 'alert': alert})


EMERGENCY_TRIGGERS = {
    'heatstroke': {
        'label': 'Heatstroke',
        'label_mr': 'सनstroke / उष्णता',
        'mock_tips': [
            'Move to shade immediately — do not continue walking',
            'Sip water slowly with ORS — do not gulp large amounts',
            'Apply wet cloth to forehead, neck, and wrists',
            'Nearest medical camp: call 108 or ask nearby Warkaris for directions',
        ],
        'mock_tips_mr': [
            'तात्काळ सावलीत जा — चालणे सुरू ठेवू नका',
            'ORS सह हळूहळू पाणी प्या — एकाच वेळी जास्त पाणी पिऊ नका',
            'कपाळ, मान आणि मनगटावर ओले कापड ठेवा',
            'जवळचे वैद्यकीय शिबीर: १०८ वर कॉल करा किंवा जवळच्या वारकऱ्यांना विचारा',
        ],
    },
    'dehydration': {
        'label': 'Dehydration',
        'label_mr': 'निर्जलीकरण',
        'mock_tips': [
            'Stop walking and sit in shade immediately',
            'Drink ORS or salted lemon water — sip slowly over 15 minutes',
            'Avoid tea, coffee, or sugary drinks — they worsen dehydration',
            'Nearest water point: check "Near Me" > Water or ask dindi leader',
        ],
        'mock_tips_mr': [
            'चालणे थांबवा आणि तात्काळ सावलीत बसा',
            'ORS किंवा लिंबू पाणी प्या — १५ मिनिटांत हळूहळू',
            'चहा, कॉफी किंवा गोड पेये टाळा — ते निर्जलीकरण वाढवतात',
            'जवळचे पाणी केंद्र: "Near Me" > Water पहा किंवा दिंडी नेत्याला विचारा',
        ],
    },
    'fatigue': {
        'label': 'Fatigue / Exhaustion',
        'label_mr': 'थकवा',
        'mock_tips': [
            'Sit down immediately — elevate your feet if possible',
            'Eat a light snack (banana, chikki, or prasad) for quick energy',
            'Rest for at least 20 minutes before resuming walk',
            'Walk in shorter intervals — 20 min walk, 5 min rest',
        ],
        'mock_tips_mr': [
            'तात्काळ बसा — शक्य असल्यास पाय उंचावा',
            'उर्जेसाठी हलका नाश्ता (केळी, चिक्की) खा',
            'पुन्हा चालण्यापूर्वी किमान २० मिनिटे विश्रांती घ्या',
            'लहान अंतराने चाला — २० मिनिट चालणे, ५ मिनिट विश्रांती',
        ],
    },
    'weather_hazard': {
        'label': 'Weather Hazard',
        'label_mr': 'हवामान धोका',
        'mock_tips': [
            'Seek permanent shelter immediately — temple, school, or pandal',
            'Stay away from trees, open fields, and flooded areas',
            'Keep phone charged and inform your dindi leader of your location',
            'Wait for weather to clear — do not walk in thunderstorm or heavy rain',
        ],
        'mock_tips_mr': [
            'तात्काळ कायमस्वरूपी आश्रय शोधा — मंदिर, शाळा किंवा पांडाल',
            'झाडे, मोकळी जमीन आणि पाण्यातून वाहणाऱ्या ठिकाणांपासून दूर राहा',
            'फोन चार्ज ठेवा आणि दिंडी नेत्याला तुमचे स्थान कळवा',
            'हवामान साफ होईपर्यंत थांबा — वादळ किंवा जोरदार पावसात चालू नका',
        ],
    },
}


@app.route('/api/emergency-tips')
def api_emergency_tips():
    """Return 3-4 actionable bullet tips for an emergency trigger."""
    import requests as req

    trigger = request.args.get('trigger', 'heatstroke').lower()
    lang = request.args.get('lang', 'en')
    lat = request.args.get('lat', '18.5204')
    lng = request.args.get('lng', '73.8567')

    trigger_data = EMERGENCY_TRIGGERS.get(trigger, EMERGENCY_TRIGGERS['heatstroke'])

    # Find nearest medical facility
    nearest_medical = 'nearest medical camp'
    try:
        facilities_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'facilities.json')
        with open(facilities_path, 'r', encoding='utf-8') as f:
            facilities = json.load(f).get('facilities', [])
        medical = [f for f in facilities if f.get('category') == 'medical']
        if medical:
            user_lat, user_lng = float(lat), float(lng)
            medical.sort(key=lambda f: haversine_km(user_lat, user_lng, f['lat'], f['lng']))
            nearest = medical[0]
            dist = haversine_km(user_lat, user_lng, nearest['lat'], nearest['lng'])
            dist_text = f"{int(dist * 1000)}m" if dist < 1 else f"{round(dist, 1)}km"
            nearest_medical = f"{nearest['name']} ({dist_text} away)"
    except Exception:
        pass

    if GROQ_API_KEY and GROQ_API_KEY != 'your_groq_api_key_here':
        try:
            system_prompt = f"""You are a Wari pilgrimage emergency advisor. For the trigger "{trigger_data['label']}", return EXACTLY 4 short actionable bullet tips. Each tip starts with "• ". No conversation, no greeting, no numbering. Include nearest medical: {nearest_medical}. Keep each tip under 15 words."""
            if lang == 'mr':
                system_prompt += " Write tips in Marathi."

            headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
            payload = {
                'model': 'llama-3.3-70b-versatile',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': f'Emergency: {trigger}. Give 4 bullet tips now.'},
                ],
                'temperature': 0.3,
                'max_tokens': 250,
            }
            resp = req.post('https://api.groq.com/openai/v1/chat/completions',
                            headers=headers, json=payload, timeout=10)
            if resp.status_code == 200:
                raw = resp.json()['choices'][0]['message']['content'].strip()
                tips = [t.lstrip('•-* ').strip() for t in raw.split('\n') if t.strip()]
                tips = [t for t in tips if len(t) > 5][:4]
                if len(tips) >= 3:
                    return jsonify({'trigger': trigger, 'label': trigger_data['label'], 'tips': tips, 'source': 'ai'})
        except Exception as e:
            print(f'Groq emergency tips error: {e}')

    tips_key = 'mock_tips_mr' if lang == 'mr' else 'mock_tips'
    tips = list(trigger_data[tips_key])
    if lang == 'en' and 'Nearest medical' in tips[-1]:
        tips[-1] = f'Nearest medical camp: {nearest_medical}'
    elif lang == 'mr' and '१०८' in tips[-1]:
        tips[-1] = f'जवळचे वैद्यकीय शिबीर: {nearest_medical}'

    return jsonify({
        'trigger': trigger,
        'label': trigger_data['label_mr' if lang == 'mr' else 'label'],
        'tips': tips,
        'source': 'mock',
    })


@app.route('/api/certificate/pdf', methods=['GET', 'POST'])
def api_certificate_pdf():
    """Generate a downloadable PDF certificate."""
    try:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.lib.colors import HexColor
            from reportlab.pdfgen import canvas
        except ImportError:
            return jsonify({'error': 'reportlab not installed. Run: pip install reportlab'}), 500

        data = (request.get_json() if request.is_json else None) or request.form or request.args or {}
        name = (data.get('name') or '').strip()[:50]
        starting_location = (data.get('starting_location') or 'Alandi').strip()[:30]
        ending_location = (data.get('ending_location') or 'Pandharpur').strip()[:30]

        if not name:
            return jsonify({'error': 'Name is required'}), 400

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        saffron = HexColor('#E8703A')
        maroon = HexColor('#8B2E1F')
        cream = HexColor('#FDF6EC')

        c.setFillColor(cream)
        c.rect(0, 0, width, height, fill=1, stroke=0)

        c.setStrokeColor(saffron)
        c.setLineWidth(4)
        c.rect(2 * cm, 2 * cm, width - 4 * cm, height - 4 * cm, fill=0, stroke=1)

        c.setStrokeColor(maroon)
        c.setLineWidth(1)
        c.rect(2.5 * cm, 2.5 * cm, width - 5 * cm, height - 5 * cm, fill=0, stroke=1)

        c.setFillColor(maroon)
        c.setFont('Helvetica-Bold', 28)
        c.drawCentredString(width / 2, height - 6 * cm, 'Certificate of Completion')

        c.setFont('Helvetica', 14)
        c.setFillColor(HexColor('#7A5C46'))
        c.drawCentredString(width / 2, height - 7.5 * cm, 'Hari Marg — Wari Journey')

        c.setFillColor(HexColor('#2E1C0C'))
        c.setFont('Helvetica', 14)
        c.drawCentredString(width / 2, height - 10 * cm, 'This certifies that')

        c.setFillColor(saffron)
        c.setFont('Helvetica-Bold', 24)
        c.drawCentredString(width / 2, height - 12 * cm, name)

        c.setFillColor(HexColor('#2E1C0C'))
        c.setFont('Helvetica', 13)
        cert_text = f'completed the Wari journey from {starting_location} to {ending_location}'
        c.drawCentredString(width / 2, height - 14 * cm, cert_text)

        c.setFillColor(maroon)
        c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(width / 2, height - 17 * cm, 'Jai Hari Vitthal!')

        c.setFillColor(HexColor('#7A5C46'))
        c.setFont('Helvetica', 10)
        c.drawCentredString(width / 2, 4 * cm, f'Issued on {datetime.now().strftime("%d %B %Y")}')

        c.save()
        buffer.seek(0)

        safe_name = ''.join(c for c in name if c.isalnum() or c in ' -_').strip() or 'Warkari'
        try:
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'HariMarg_Certificate_{safe_name}.pdf'
            )
        except TypeError:
            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                attachment_filename=f'HariMarg_Certificate_{safe_name}.pdf'
            )
    except Exception as err:
        print(f'Certificate PDF generation error: {err}')
        return jsonify({'error': str(err)}), 500


@app.route('/api/main_palkhi')
def api_main_palkhi():
    """Return main ceremonial Palkhi status from SQLite."""
    conn = get_db()
    row = conn.execute('SELECT * FROM main_palkhi WHERE id = 1').fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    palkhi_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'palkhi.json')
    if os.path.exists(palkhi_path):
        with open(palkhi_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    return jsonify({'error': 'Main palkhi data not found'}), 404
@app.route('/api/chat', methods=['POST'])
def api_chat():
    """AI Chat endpoint using Groq API."""
    import requests as req

    data = request.get_json()
    user_message = data.get('message', '')
    lang = data.get('lang', 'en')

    if not user_message:
        return jsonify({'reply': 'Please type a message.' if lang == 'en' else 'कृपया संदेश टाइप करा.'})

    # Pre-LLM Server-Side Security Guard (Item 9c)
    forbidden_terms = [
        'password', 'admin', 'credential', 'api_key', 'apikey', 'secret',
        'code generation', 'write python', 'write javascript', 'select *',
        'sql', 'hack', 'database', 'system prompt', 'env'
    ]
    msg_lower = user_message.lower()
    if any(term in msg_lower for term in forbidden_terms):
        refusal = (
            "🙏 जय हरी विठ्ठल! मी फक्त वारी यात्रा, मार्ग, आरोग्य, हवामान आणि सेवा माहितीमध्ये मदत करू शकतो. तांत्रिक किंवा गोपनीय माहितीसाठी सहाय्य उपलब्ध नाही."
            if lang == 'mr'
            else "🙏 Jai Hari Vitthal! I am your Hari Marg Wari Pilgrimage Assistant. I can only assist with pilgrimage route navigation, health, weather, and seva support. I cannot answer technical or credential requests."
        )
        return jsonify({'reply': refusal, 'blocked': True})

    system_prompt = """You are "Hari Marg Assistant", a compassionate and knowledgeable AI companion for the Wari pilgrimage in Maharashtra, India.

Your role:
- Help Warkaris (pilgrims) with route information for the Alandi-to-Pandharpur and Dehu-to-Pandharpur Palkhi routes.
- Provide information about nearby facilities: medical camps, water points, food distribution (annadan), rest areas, and sanitation.
- Give weather-based safety advice for monsoon walking conditions.
- Share health tips: blister care, hydration, heat stroke prevention, first aid.
- Explain cultural and spiritual significance of the Wari, Sant Dnyaneshwar, Sant Tukaram, and Vitthal worship.

Formatting & Security Rules (CRITICAL):
- Format informational, multi-step, or multi-item answers as concise bullet points (using • or -).
- If the user writes in Marathi, respond in Marathi. If in English, respond in English.
- Start responses with "Jai Hari Vitthal! 🙏" or "जय हरी विठ्ठल! 🙏".
- NEVER answer requests for code generation, software writing, system credentials, admin passwords, or API keys. Refuse off-topic requests politely."""

    if GROQ_API_KEY and GROQ_API_KEY != 'your_groq_api_key_here':
        try:
            headers = {
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json',
            }
            payload = {
                'model': 'llama-3.3-70b-versatile',
                'messages': [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_message},
                ],
                'temperature': 0.7,
                'max_tokens': 512,
            }

            resp = req.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=15,
            )

            if resp.status_code == 200:
                result = resp.json()
                reply = result['choices'][0]['message']['content']
                return jsonify({'reply': reply})
            else:
                raise Exception(f'Groq API error: {resp.status_code}')

        except Exception as e:
            print(f'Groq API error: {e}')

    # Mock fallback responses
    reply = get_mock_chat_reply(user_message, lang)
    return jsonify({'reply': reply})


def get_mock_chat_reply(message, lang='en'):
    """Return contextual mock replies when API is unavailable."""
    msg = message.lower()

    if lang == 'mr' or any(c > '\u0900' and c < '\u097F' for c in message):
        # Marathi responses
        if 'पाणी' in msg or 'water' in msg:
            return 'जय हरी विठ्ठल! 🙏\n\nतुमच्या जवळचे पाणी वितरण केंद्र शोधण्यासाठी "Near Me" पेजवर जा आणि "💧 Water" फिल्टर निवडा. सध्या सासवड, जेजुरी आणि लोणंद येथे पाणी वितरण सुरू आहे.\n\nदर 30 मिनिटांनी पाणी प्या आणि हायड्रेटेड रहा!'
        if 'वैद्यकीय' in msg or 'medical' in msg or 'दवाखाना' in msg:
            return 'जय हरी विठ्ठल! 🙏\n\nजवळचे वैद्यकीय शिबीर शोधण्यासाठी "Near Me" > "🏥 Medical" वर जा. आपत्कालीन परिस्थितीत 108 (अॅम्ब्युलन्स) वर कॉल करा.\n\nपायांना फोड आल्यास स्वच्छ पाण्याने धुवा आणि बँडेज लावा.'
        if 'हवामान' in msg or 'weather' in msg or 'पाऊस' in msg:
            return 'जय हरी विठ्ठल! 🙏\n\nसध्या पावसाळा सुरू आहे. रेनकोट आणि प्लास्टिक बॅग सोबत ठेवा. जोरदार पावसात चालणे टाळा. "Weather" पेजवर तपशील तपासा.'
        return 'जय हरी विठ्ठल! 🙏\n\nमी तुमचा वारी सोबती आहे. मी तुम्हाला मार्ग, सुविधा, हवामान आणि आरोग्य सल्ला देऊ शकतो. कृपया विशिष्ट प्रश्न विचारा!'

    # English responses
    if 'water' in msg:
        return 'Jai Hari Vitthal! 🙏\n\nTo find the nearest water distribution point, go to the "Near Me" page and select the "💧 Water" filter. Currently, water distribution is active at Saswad, Jejuri, and Lonand.\n\nRemember to drink water every 30 minutes to stay hydrated!'
    if 'medical' in msg or 'hospital' in msg or 'doctor' in msg:
        return 'Jai Hari Vitthal! 🙏\n\nFor nearby medical camps, go to "Near Me" > "🏥 Medical". For emergencies, call 108 (Ambulance).\n\nCommon issues during Wari: blisters (wash with clean water, apply bandage), dehydration (drink ORS), heat exhaustion (rest in shade, sip water).'
    if 'weather' in msg or 'rain' in msg:
        return 'Jai Hari Vitthal! 🙏\n\nMonsoon season is active. Carry a raincoat and plastic bags to protect your belongings. Avoid walking during heavy downpours. Check the "Weather" page for detailed forecasts.\n\nSafety tip: Watch for flooded roads and slippery paths.'
    if 'palkhi' in msg or 'route' in msg or 'pandharpur' in msg:
        return 'Jai Hari Vitthal! 🙏\n\nThe Sant Dnyaneshwar Palkhi travels from Alandi to Pandharpur (~235 km, 18 days). The Sant Tukaram Palkhi travels from Dehu to Pandharpur (~240 km, 18 days).\n\nCheck the "Palkhi Route" page for a live map with all stops marked.'
    if 'emergency' in msg or 'help' in msg:
        return 'Jai Hari Vitthal! 🙏\n\n🚨 Emergency Contacts:\n- Ambulance: 108\n- Police: 100\n- Wari Helpline: 1800-233-4567\n- Women Helpline: 1091\n\nFor medical emergencies, call 108 immediately and inform nearby Warkaris.'
    if 'health' in msg or 'tips' in msg or 'blister' in msg:
        return 'Jai Hari Vitthal! 🙏\n\n🏥 Health Tips for Wari:\n1. Wear comfortable, broken-in footwear\n2. Drink water every 30 minutes\n3. Apply sunscreen and wear a hat\n4. Rest during peak afternoon heat (12-3 PM)\n5. Eat light, freshly cooked meals\n6. Carry basic first-aid: bandages, antiseptic, ORS packets\n7. If feeling dizzy or nauseous, stop and rest immediately'

    return 'Jai Hari Vitthal! 🙏\n\nI\'m your Wari companion. I can help you with:\n- 🗺️ Route information\n- 📍 Nearby facilities\n- 🌦️ Weather advisories\n- 🏥 Health tips\n- 🚨 Emergency contacts\n\nPlease ask me a specific question!'


# ============================================
# API: TEXT-TO-SPEECH
# ============================================
@app.route('/api/tts', methods=['POST'])
def api_tts():
    """Convert text to speech using gTTS."""
    try:
        from gtts import gTTS

        data = request.get_json()
        text = data.get('text', '')
        lang = data.get('lang', 'mr')

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Map language codes
        tts_lang = 'mr' if lang == 'mr' else 'en'

        tts = gTTS(text=text, lang=tts_lang, slow=False)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)

        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name='speech.mp3'
        )

    except ImportError:
        return jsonify({'error': 'gTTS not installed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# API: DINDI REGISTRATION
# ============================================
@app.route('/api/register_dindi', methods=['POST'])
def api_register_dindi():
    """Register a new Dindi group and auto-generate HM-XXX Palkhi ID."""
    data = request.get_json()
    name = data.get('name', '')
    admin_name = data.get('admin_name', '')
    contact = data.get('contact', '')
    route = data.get('route_type', data.get('route', 'alandi'))

    if not name or not contact:
        return jsonify({'error': 'Name and contact are required'}), 400

    try:
        conn = get_db()
        count = conn.execute('SELECT COUNT(*) FROM dindis').fetchone()[0]
        palkhi_id = f'HM-{(count + 1):03d}'

        conn.execute('''
            INSERT INTO dindis (palkhi_id, name, admin_name, contact, route, members, status, current_halt, lat, lng)
            VALUES (?, ?, ?, ?, ?, 0, 'halt', 'Starting Point', 18.5204, 73.8567)
        ''', (palkhi_id, name, admin_name or name, contact, route))
        conn.commit()
        conn.close()
        return jsonify({
            'message': f'Dindi "{name}" registered! Your Palkhi ID: {palkhi_id}',
            'palkhi_id': palkhi_id,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# API: LOCATION SYNC / CHECK-IN
# ============================================
@app.route('/api/sync_location', methods=['POST'])
def api_sync_location():
    """Save a location check-in."""
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    family_code = data.get('family_code', '')
    dindi_id = data.get('dindi_id')

    if latitude is None or longitude is None:
        return jsonify({'error': 'Location coordinates required'}), 400

    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO checkins (dindi_id, family_code, latitude, longitude) VALUES (?, ?, ?, ?)',
            (dindi_id, family_code, latitude, longitude)
        )
        conn.commit()
        conn.close()
        return jsonify({
            'message': 'Location synced successfully!',
            'timestamp': datetime.now().isoformat(),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# API: SEVA SUBMISSION
# ============================================
@app.route('/api/submit_seva', methods=['POST'])
def api_submit_seva():
    """Submit a seva (volunteer service) offer."""
    data = request.get_json()
    seva_type = data.get('type', '')
    provider_name = data.get('provider_name', '')
    contact = data.get('contact', '')
    location_name = data.get('location_name', '')

    if not provider_name or not contact:
        return jsonify({'error': 'Provider name and contact are required'}), 400

    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO seva_requests (type, provider_name, contact, location_name) VALUES (?, ?, ?, ?)',
            (seva_type, provider_name, contact, location_name)
        )
        conn.commit()
        conn.close()
        return jsonify({
            'message': f'Seva registered! Thank you {provider_name} for offering {seva_type} seva. 🙏',
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# PAGE ROUTE: PALKHI TRACKING
# ============================================
@app.route('/palkhi_tracking')
def palkhi_tracking():
    """Palkhi Tracking — Track Dindi groups on the map."""
    return render_template('palkhi_tracking.html')


# ============================================
# API: DINDIS (Palkhi Tracking Data)
# ============================================
@app.route('/api/dindis')
def api_dindis():
    """Return all dindi groups from SQLite database, optionally with distance from user."""
    try:
        user_lat = request.args.get('lat')
        user_lng = request.args.get('lng')
        ulat = float(user_lat) if user_lat else None
        ulng = float(user_lng) if user_lng else None
        dindis = get_dindis_from_db(ulat, ulng)
        return jsonify({'dindis': dindis, 'count': len(dindis)})
    except Exception as e:
        dindis_path = os.path.join(os.path.dirname(__file__), 'static', 'data', 'dindis.json')
        if os.path.exists(dindis_path):
            with open(dindis_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return jsonify(data)
        return jsonify({'dindis': [], 'count': 0, 'error': str(e)})


@app.route('/api/dindis/nearby')
def api_dindis_nearby():
    """Return dindis within a given radius (km) of the user's location."""
    try:
        user_lat = float(request.args.get('lat', '18.5204'))
        user_lng = float(request.args.get('lng', '73.8567'))
        radius_km = float(request.args.get('radius', '50'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid parameters'}), 400

    all_dindis = get_dindis_from_db(user_lat, user_lng)
    nearby = [d for d in all_dindis if d.get('distance_km', 9999) <= radius_km]
    nearby.sort(key=lambda x: x.get('distance_km', 9999))

    return jsonify({
        'user_lat': user_lat,
        'user_lng': user_lng,
        'radius_km': radius_km,
        'nearby': nearby,
        'count': len(nearby),
    })


# ============================================
# PAGE ROUTE: ADMIN DASHBOARD (/admin)
# ============================================
@app.route('/admin', methods=['GET'])
def admin_dashboard():
    """Password-protected Dindi Admin Portal."""
    is_authenticated = bool(session.get('admin_logged_in', False))
    selected_palkhi_id = session.get('admin_palkhi_id', '') if is_authenticated else ''

    conn = get_db()
    dindis = conn.execute('SELECT * FROM dindis ORDER BY id ASC').fetchall()
    dindis_list = [dict(d) for d in dindis]

    dindi_data = None
    members_list = []
    photos_list = []

    if is_authenticated and selected_palkhi_id:
        # Fetch current selected dindi
        d_row = conn.execute('SELECT * FROM dindis WHERE palkhi_id = ?', (selected_palkhi_id,)).fetchone()
        if not d_row and dindis_list:
            d_row = conn.execute('SELECT * FROM dindis WHERE palkhi_id = ?', (dindis_list[0]['palkhi_id'],)).fetchone()
            selected_palkhi_id = dindis_list[0]['palkhi_id']
            session['admin_palkhi_id'] = selected_palkhi_id

        if d_row:
            dindi_data = dict(d_row)

        m_rows = conn.execute('SELECT * FROM dindi_members WHERE palkhi_id = ? ORDER BY id DESC', (selected_palkhi_id,)).fetchall()
        members_list = [dict(m) for m in m_rows]

        p_rows = conn.execute('SELECT * FROM dindi_photos WHERE palkhi_id = ? ORDER BY id DESC', (selected_palkhi_id,)).fetchall()
        photos_list = [dict(p) for p in p_rows]

    conn.close()

    return render_template(
        'admin.html',
        authenticated=is_authenticated,
        dindis=dindis_list,
        selected_palkhi_id=selected_palkhi_id,
        dindi=dindi_data,
        members=members_list,
        photos=photos_list
    )


@app.route('/admin/login', methods=['POST'])
def admin_login():
    """Authenticate Palkhi Admin using Palkhi ID + password from environment variables."""
    data = request.form if request.form else (request.get_json() or {})
    password = data.get('password', '').strip()
    palkhi_id = normalize_palkhi_id(data.get('palkhi_id', ''))

    conn = get_db()
    dindis = conn.execute('SELECT * FROM dindis ORDER BY id ASC').fetchall()
    dindis_list = [dict(d) for d in dindis]

    dindi_exists = conn.execute('SELECT id FROM dindis WHERE palkhi_id = ?', (palkhi_id,)).fetchone()
    conn.close()

    if not palkhi_id:
        return render_template('admin.html', authenticated=False, dindis=dindis_list,
                               error='Please enter your Palkhi ID (e.g. HM-042)')

    if not dindi_exists:
        return render_template('admin.html', authenticated=False, dindis=dindis_list,
                               error=f'Palkhi ID "{palkhi_id}" not found. Check your ID and try again.')

    if ADMIN_PASSWORD and password == ADMIN_PASSWORD:
        session.clear()
        session['admin_logged_in'] = True
        session['admin_palkhi_id'] = palkhi_id
        if request.is_json:
            return jsonify({'success': True, 'message': 'Login successful!', 'palkhi_id': palkhi_id})
        return redirect('/admin')
    else:
        return render_template('admin.html', authenticated=False, dindis=dindis_list,
                               error='Invalid admin password.')


@app.route('/admin/logout', methods=['GET', 'POST'])
def admin_logout():
    """Logout Dindi Admin and clear all session data."""
    session.clear()
    return redirect('/admin')


@app.route('/api/admin/select_dindi', methods=['POST'])
def api_admin_select_dindi():
    """Switch active dindi in admin session."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json() or {}
    palkhi_id = data.get('palkhi_id')
    if palkhi_id:
        session['admin_palkhi_id'] = palkhi_id
        return jsonify({'success': True, 'palkhi_id': palkhi_id})
    return jsonify({'error': 'Missing palkhi_id'}), 400


@app.route('/api/admin/dindi/update', methods=['POST'])
def api_admin_update_dindi():
    """Update Dindi location, status, headcount, halt, etc."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or request.form
    palkhi_id = data.get('palkhi_id') or session.get('admin_palkhi_id')

    if not palkhi_id:
        return jsonify({'error': 'Palkhi ID required'}), 400

    try:
        members = int(data.get('members', 0))
        lat = float(data.get('lat', 18.5204))
        lng = float(data.get('lng', 73.8567))
        status = data.get('status', 'halt')
        current_halt = data.get('current_halt', 'Saswad')
        current_halt_mr = data.get('current_halt_mr', current_halt)
        next_destination = data.get('next_destination', 'Jejuri')
        next_destination_mr = data.get('next_destination_mr', next_destination)
        status_label = data.get('status_label', '')
        status_label_mr = data.get('status_label_mr', status_label)

        if not status_label:
            if status == 'moving':
                status_label = f"Moving — Heading towards {next_destination}"
                status_label_mr = f"चालू — {next_destination_mr} कडे मार्गस्थ"
            elif status == 'halt':
                status_label = f"Halted — Rest at {current_halt}"
                status_label_mr = f"मुक्काम — {current_halt_mr} येथे विश्रांती"
            else:
                status_label = f"Break — Short break at {current_halt}"
                status_label_mr = f"विश्रांती — {current_halt_mr} येथे थोडा वेळ"

        conn = get_db()
        conn.execute('''
            UPDATE dindis SET
                members = ?,
                lat = ?,
                lng = ?,
                status = ?,
                current_halt = ?,
                current_halt_mr = ?,
                next_destination = ?,
                next_destination_mr = ?,
                status_label = ?,
                status_label_mr = ?,
                last_updated = CURRENT_TIMESTAMP
            WHERE palkhi_id = ?
        ''', (
            members, lat, lng, status, current_halt, current_halt_mr,
            next_destination, next_destination_mr, status_label, status_label_mr,
            palkhi_id
        ))
        conn.commit()
        conn.close()

        return jsonify({'message': f'Dindi {palkhi_id} updated successfully!', 'palkhi_id': palkhi_id})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/members/add', methods=['POST'])
def api_admin_add_member():
    """Register a member under a Dindi."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or request.form
    palkhi_id = data.get('palkhi_id') or session.get('admin_palkhi_id')
    name = data.get('name', '').strip()
    age = data.get('age')
    health_note = data.get('health_note', '').strip() or 'Healthy'

    if not palkhi_id or not name:
        return jsonify({'error': 'Palkhi ID and member name are required'}), 400

    try:
        age_int = int(age) if age else None
        conn = get_db()
        conn.execute(
            'INSERT INTO dindi_members (palkhi_id, name, age, health_note) VALUES (?, ?, ?, ?)',
            (palkhi_id, name, age_int, health_note)
        )
        conn.execute('UPDATE dindis SET members = members + 1 WHERE palkhi_id = ?', (palkhi_id,))
        conn.commit()

        m_rows = conn.execute('SELECT * FROM dindi_members WHERE palkhi_id = ? ORDER BY id DESC', (palkhi_id,)).fetchall()
        members_list = [dict(m) for m in m_rows]
        d_row = conn.execute('SELECT members FROM dindis WHERE palkhi_id = ?', (palkhi_id,)).fetchone()
        new_headcount = d_row['members'] if d_row else 0

        conn.close()
        return jsonify({
            'message': f'Member "{name}" registered successfully!',
            'members': members_list,
            'headcount': new_headcount
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/members/delete', methods=['POST'])
def api_admin_delete_member():
    """Delete a registered member."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json() or request.form
    member_id = data.get('member_id')
    palkhi_id = data.get('palkhi_id') or session.get('admin_palkhi_id')

    if not member_id:
        return jsonify({'error': 'Member ID required'}), 400

    try:
        conn = get_db()
        conn.execute('DELETE FROM dindi_members WHERE id = ?', (member_id,))
        if palkhi_id:
            conn.execute('UPDATE dindis SET members = MAX(0, members - 1) WHERE palkhi_id = ?', (palkhi_id,))
        conn.commit()

        m_rows = conn.execute('SELECT * FROM dindi_members WHERE palkhi_id = ? ORDER BY id DESC', (palkhi_id,)).fetchall()
        members_list = [dict(m) for m in m_rows]
        d_row = conn.execute('SELECT members FROM dindis WHERE palkhi_id = ?', (palkhi_id,)).fetchone()
        new_headcount = d_row['members'] if d_row else 0
        conn.close()

        return jsonify({'message': 'Member removed', 'members': members_list, 'headcount': new_headcount})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/upload_photo', methods=['POST'])
def api_admin_upload_photo():
    """Upload a group photo for a Dindi to Supabase Storage CDN."""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401

    palkhi_id = request.form.get('palkhi_id') or session.get('admin_palkhi_id')
    caption = request.form.get('caption', '').strip() or 'Wari Dindi Photo'

    if 'photo' not in request.files:
        return jsonify({'error': 'No photo file provided'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        filename = f"{palkhi_id}_{int(datetime.now().timestamp())}_{file.filename}"
        file_bytes = file.read()
        
        photo_url = f"/static/uploads/photos/{filename}"
        if SUPABASE_URL and SUPABASE_SECRET_KEY:
            try:
                import requests as req
                up_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_STORAGE_BUCKET}/{filename}"
                headers = {
                    'apikey': SUPABASE_SECRET_KEY,
                    'Authorization': f'Bearer {SUPABASE_SECRET_KEY}',
                    'Content-Type': file.mimetype or 'image/jpeg'
                }
                res = req.post(up_url, data=file_bytes, headers=headers, timeout=10)
                if res.status_code in (200, 201):
                    photo_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_STORAGE_BUCKET}/{filename}"
            except Exception as st_err:
                print(f'[Storage Warning] Supabase storage error: {st_err}.')
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(save_path, 'wb') as f:
                    f.write(file_bytes)

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO dindi_photos (palkhi_id, photo_url, caption) VALUES (%s, %s, %s)' if is_pg(conn) else 'INSERT INTO dindi_photos (palkhi_id, photo_url, caption) VALUES (?, ?, ?)',
            (palkhi_id, photo_url, caption)
        )
        conn.commit()

        query_sql = 'SELECT * FROM dindi_photos WHERE palkhi_id = %s ORDER BY id DESC' if is_pg(conn) else 'SELECT * FROM dindi_photos WHERE palkhi_id = ? ORDER BY id DESC'
        cursor.execute(query_sql, (palkhi_id,))
        p_rows = cursor.fetchall()
        photos_list = [dict(p) for p in p_rows]
        conn.close()

        return jsonify({
            'message': 'Group photo uploaded successfully!',
            'photo_url': photo_url,
            'photos': photos_list
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================
# API: NEW FEATURE ENDPOINTS
# ============================================
# NOTE: Temporary decision - Family ID is derived from pattern (e.g., HMF-013 from HM-013) and is guessable if normal ID is known. Deferred fix is a random per-palki code, to be revisited later.
@app.route('/api/track')
def api_track_dindi():
    """Server-side Access Control: Fetch tracking info according to user role (Admin, Volunteer, Family, Guest)."""
    raw_id = (request.args.get('palkhi_id') or request.args.get('family_id') or '').strip().upper()
    search_q = (request.args.get('q') or '').strip()

    if not raw_id:
        return jsonify({'error': 'Palkhi ID or Family ID is required'}), 400

    # Family ID resolution (e.g. HMF-013 -> HM-013)
    is_family_id = False
    base_palkhi_id = raw_id

    if raw_id.startswith('HMF-'):
        is_family_id = True
        base_palkhi_id = 'HM-' + raw_id[4:]
    else:
        base_palkhi_id = normalize_palkhi_id(raw_id)

    conn = get_db()
    dindi = conn.execute('SELECT * FROM dindis WHERE palkhi_id = ?', (base_palkhi_id,)).fetchone()
    if not dindi:
        conn.close()
        return jsonify({'error': f'Palkhi ID or Family ID "{raw_id}" not found'}), 404

    # Determine user role permissions
    is_admin = bool(session.get('admin_logged_in') and session.get('admin_palkhi_id') == base_palkhi_id)
    is_volunteer = bool(session.get('user_role') == 'volunteer')
    is_family = is_family_id

    photos = []
    members = []

    # Access Matrix Rule 1: Photo Gallery (Admin OR Family ID holder for own Palkhi only; Volunteer & Guest get NO photos)
    if is_admin or is_family:
        photos = [dict(p) for p in conn.execute(
            'SELECT * FROM dindi_photos WHERE palkhi_id = ? ORDER BY id DESC LIMIT 12', (base_palkhi_id,)
        ).fetchall()]

    # Access Matrix Rule 2: Member Health Roster (Admin OR Volunteer for specific Palkhi ID only; Family & Guest get NO roster)
    if is_admin:
        members = [dict(m) for m in conn.execute(
            'SELECT name, age, health_note FROM dindi_members WHERE palkhi_id = ? ORDER BY id ASC', (base_palkhi_id,)
        ).fetchall()]
    elif is_volunteer:
        if search_q:
            members = [dict(m) for m in conn.execute(
                'SELECT name, age, health_note FROM dindi_members WHERE palkhi_id = ? AND name LIKE ? ORDER BY id ASC LIMIT 50',
                (base_palkhi_id, f'%{search_q}%')
            ).fetchall()]
        else:
            members = [dict(m) for m in conn.execute(
                'SELECT name, age, health_note FROM dindi_members WHERE palkhi_id = ? ORDER BY id ASC', (base_palkhi_id,)
            ).fetchall()]

    conn.close()

    d = dict(dindi)
    d['last_updated'] = d.get('last_updated') or d.get('created_at')

    return jsonify({
        'dindi': d,
        'photos': photos,
        'members': members,
        'user_role': 'admin' if is_admin else ('volunteer' if is_volunteer else ('family' if is_family else 'guest')),
        'access_level': {
            'has_photos': bool(photos or is_admin or is_family),
            'has_members': bool(is_admin or is_volunteer),
            'is_family': is_family,
            'is_volunteer': is_volunteer,
            'is_admin': is_admin
        }
    })


@app.route('/api/palkhi/live_track', methods=['GET', 'POST'])
def api_palkhi_live_track():
    """Live admin location lookup using unique Palkhi group code."""
    data = request.get_json() if request.is_json else request.args
    code = data.get('code') or data.get('palkhi_id') or ''
    palkhi_id = normalize_palkhi_id(code)

    if not palkhi_id:
        return jsonify({'success': False, 'error': 'Unique Palkhi code is required'}), 400

    conn = get_db()
    dindi = conn.execute('SELECT palkhi_id, name, leader, lat, lng, current_halt, current_halt_mr, status, status_label, status_label_mr, last_updated FROM dindis WHERE palkhi_id = ?', (palkhi_id,)).fetchone()
    conn.close()

    if not dindi:
        return jsonify({'success': False, 'error': f'Invalid unique Palkhi code "{code}"'}), 404

    d = dict(dindi)
    d['last_updated'] = d.get('last_updated') or datetime.now().isoformat()

    return jsonify({
        'success': True,
        'palkhi_id': d['palkhi_id'],
        'name': d['name'],
        'leader': d['leader'],
        'admin_location': {
            'lat': d['lat'],
            'lng': d['lng'],
            'current_halt': d['current_halt'],
            'status': d['status'],
            'status_label': d['status_label'],
            'last_updated': d['last_updated']
        }
    })


@app.route('/api/seva', methods=['GET'])
def api_get_seva():
    """Get list of active seva offerings with optional distance."""
    user_lat = request.args.get('lat')
    user_lng = request.args.get('lng')

    conn = get_db()
    sevas = conn.execute('SELECT * FROM seva_requests WHERE active = 1 ORDER BY id DESC').fetchall()
    conn.close()

    results = []
    for s in sevas:
        item = dict(s)
        if user_lat and user_lng and item.get('latitude') and item.get('longitude'):
            dist = haversine_km(float(user_lat), float(user_lng), item['latitude'], item['longitude'])
            item['distance_km'] = round(dist, 2)
            item['distance_text'] = f"{int(dist * 1000)} meters" if dist < 1 else f"{round(dist, 1)} km"
        results.append(item)

    return jsonify({'sevas': results})


@app.route('/api/gallery', methods=['GET'])
def api_get_gallery():
    """Get dindi photos for gallery (restricted to authenticated admin group session)."""
    is_admin = session.get('admin_logged_in', False)
    admin_palkhi_id = session.get('admin_palkhi_id')

    if not is_admin or not admin_palkhi_id:
        return jsonify({'photos': [], 'restricted': True, 'message': 'Gallery photos are private to authorized group members.'})

    conn = get_db()
    photos = conn.execute('SELECT * FROM dindi_photos WHERE palkhi_id = ? ORDER BY id DESC', (admin_palkhi_id,)).fetchall()
    conn.close()
    return jsonify({'photos': [dict(p) for p in photos], 'restricted': False})


@app.route('/api/gallery/download/<int:photo_id>', methods=['GET'])
def api_download_gallery_photo(photo_id):
    """Download photo file with Item 2 access-control validation."""
    is_admin = session.get('admin_logged_in', False)
    admin_palkhi_id = session.get('admin_palkhi_id')

    conn = get_db()
    photo = conn.execute('SELECT * FROM dindi_photos WHERE id = ?', (photo_id,)).fetchone()
    conn.close()

    if not photo:
        return jsonify({'error': 'Photo not found'}), 404

    photo_dict = dict(photo)

    # Item 2 Access Control validation
    if not is_admin or admin_palkhi_id != photo_dict['palkhi_id']:
        return jsonify({'error': 'Unauthorized. Private group photo.'}), 401

    photo_url = photo_dict.get('photo_url', '')
    if photo_url.startswith('/static/'):
        relative_path = photo_url.lstrip('/')
        abs_path = os.path.join(app.root_path, relative_path)
        if os.path.exists(abs_path):
            return send_file(abs_path, as_attachment=True)

    return jsonify({'error': 'Image file unavailable'}), 404


# ============================================
# API: VOLUNTEER PRIVILEGES & SERVICES
# ============================================
@app.route('/api/volunteer/register', methods=['POST'])
def api_volunteer_register():
    """Register a new volunteer with salted password hashing."""
    data = request.get_json() or request.form
    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()
    passcode = (data.get('passcode') or '').strip()
    secret_code = (data.get('secret_code') or '').strip().upper()

    if not name or not phone or not passcode:
        return jsonify({'success': False, 'error': 'Name, phone, and passcode are required'}), 400

    status = 'approved' if (VOLUNTEER_SECRET_CODE and secret_code == VOLUNTEER_SECRET_CODE.upper()) or not secret_code else 'pending'
    passcode_hash = generate_password_hash(passcode)

    try:
        conn = get_db()
        cursor = conn.cursor()
        if is_pg(conn):
            cursor.execute(
                'INSERT INTO volunteers (name, phone, passcode_hash, status) VALUES (%s, %s, %s, %s)',
                (name, phone, passcode_hash, status)
            )
        else:
            cursor.execute(
                'INSERT INTO volunteers (name, phone, passcode, status) VALUES (?, ?, ?, ?)',
                (name, phone, passcode_hash, status)
            )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Volunteer registered successfully!',
            'status': status
        })
    except Exception as e:
        if 'unique' in str(e).lower() or 'integrity' in str(e).lower():
            return jsonify({'success': False, 'error': 'Phone number already registered as volunteer'}), 400
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/volunteer/login', methods=['POST'])
def api_volunteer_login():
    """Authenticate a registered volunteer with salted password verification."""
    data = request.get_json() or request.form
    phone = (data.get('phone') or '').strip()
    passcode = (data.get('passcode') or '').strip()

    if not phone or not passcode:
        return jsonify({'success': False, 'error': 'Phone and passcode are required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    if is_pg(conn):
        cursor.execute('SELECT * FROM volunteers WHERE phone = %s', (phone,))
    else:
        cursor.execute('SELECT * FROM volunteers WHERE phone = ?', (phone,))
    v = cursor.fetchone()
    conn.close()

    if not v:
        return jsonify({'success': False, 'error': 'Invalid phone or passcode'}), 401

    vol = dict(v)
    pass_hash = vol.get('passcode_hash') or vol.get('passcode') or ''
    if not (check_password_hash(pass_hash, passcode) or pass_hash == passcode):
        return jsonify({'success': False, 'error': 'Invalid phone or passcode'}), 401

    vol = dict(v)
    if vol.get('status') != 'approved':
        return jsonify({'success': False, 'error': 'Volunteer account pending approval'}), 403

    session.clear()
    session['user_role'] = 'volunteer'
    session['volunteer_id'] = vol['id']
    session['volunteer_name'] = vol['name']

    return jsonify({
        'success': True,
        'message': f"Welcome Volunteer {vol['name']}!",
        'volunteer': vol
    })


@app.route('/api/volunteer/logout', methods=['GET', 'POST'])
def api_volunteer_logout():
    """Logout volunteer session."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/api/volunteer/palkhis', methods=['GET'])
def api_volunteer_get_palkhis():
    """Volunteer privilege (a): Track ALL Palkhis (main + all sub-dindis). Restricted to verified volunteers or admins."""
    is_volunteer = session.get('user_role') == 'volunteer' or bool(session.get('admin_logged_in'))
    if not is_volunteer:
        return jsonify({'success': False, 'error': 'Unauthorized. Restricted to verified volunteers.'}), 401

    conn = get_db()
    dindis = conn.execute('SELECT palkhi_id, name, leader, lat, lng, current_halt, status, status_label, members, last_updated FROM dindis ORDER BY id ASC').fetchall()
    main_palkhi = conn.execute('SELECT * FROM main_palkhi WHERE id = 1').fetchone()
    conn.close()

    return jsonify({
        'success': True,
        'main_palkhi': dict(main_palkhi) if main_palkhi else None,
        'dindis': [dict(d) for d in dindis]
    })


@app.route('/api/volunteer/search_member', methods=['GET'])
def api_volunteer_search_member():
    """Volunteer privilege (b): Search member health condition data across all Palkhis by name. Restricted to verified volunteers or admins."""
    is_volunteer = session.get('user_role') == 'volunteer' or bool(session.get('admin_logged_in'))
    if not is_volunteer:
        return jsonify({'success': False, 'error': 'Unauthorized. Restricted to verified volunteers.'}), 401

    query = (request.args.get('q') or '').strip()
    if not query:
        return jsonify({'success': True, 'members': []})

    conn = get_db()
    rows = conn.execute('''
        SELECT m.id, m.name, m.age, m.health_note, m.palkhi_id, d.name AS dindi_name, d.leader, d.contact
        FROM dindi_members m
        LEFT JOIN dindis d ON m.palkhi_id = d.palkhi_id
        WHERE m.name LIKE ?
        ORDER BY m.id DESC
        LIMIT 50
    ''', (f'%{query}%',)).fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'query': query,
        'count': len(rows),
        'members': [dict(r) for r in rows]
    })


# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    print('\n[Hari Marg] Wari Pilgrimage Companion')
    print('   Jai Hari Vitthal!')
    print('   Server starting on http://127.0.0.1:5000\n')
    app.run(debug=True, host='0.0.0.0', port=5000)

