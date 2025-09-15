from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import os
from datetime import datetime
import folium
import feedparser
import csv
import io
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'storm-command-secret-2024')

DATABASE = 'stormcommand.db'

CITIES = [
    'Miami', 'Houston', 'Charleston', 'New Orleans', 'Tampa',
    'Jacksonville', 'Savannah', 'Mobile', 'Pensacola', 'Wilmington',
    'Virginia Beach', 'Myrtle Beach', 'Corpus Christi', 'Galveston', 'Key West',
    'Fort Lauderdale', 'West Palm Beach', 'Naples', 'Fort Myers', 'Sarasota',
    'Panama City', 'Biloxi', 'Atlantic City', 'Ocean City', 'Norfolk',
    'Baton Rouge', 'Lafayette', 'Lake Charles', 'Beaumont', 'Port Arthur',
    'Brownsville', 'McAllen', 'Laredo', 'Victoria', 'Bay City',
    'Freeport', 'Texas City', 'Pascagoula', 'Gulfport', 'Orange Beach',
    'Gulf Shores', 'Dauphin Island', 'St. Petersburg', 'Clearwater', 'Bradenton',
    'Venice', 'Punta Gorda', 'Cape Coral', 'Marco Island', 'Everglades City'
]

CATEGORIES = [
    'Hotels', 'Casinos', 'Architects', 'Contractors', 'Glass Suppliers',
    'Property Managers', 'Insurance Companies', 'Real Estate Developers', 'Resorts', 'Condominiums',
    'Shopping Malls', 'Office Buildings', 'Hospitals', 'Schools', 'Universities',
    'Government Buildings', 'Airports', 'Marina', 'Country Clubs', 'Beach Clubs',
    'Restaurants', 'Retail Stores', 'Banks', 'Museums', 'Theaters',
    'Sports Venues', 'Convention Centers', 'Hotels Extended Stay', 'Vacation Rentals', 'Apartments',
    'Senior Living', 'Medical Centers', 'Research Facilities', 'Manufacturing', 'Warehouses',
    'Distribution Centers', 'Car Dealerships', 'Yacht Clubs', 'Golf Courses', 'Theme Parks',
    'Water Parks', 'Cruise Terminals', 'Ferry Terminals', 'Train Stations', 'Bus Stations',
    'Libraries', 'Community Centers', 'Churches', 'Synagogues', 'Mosques'
]

ACTIVE_APPS = {
    'Houston': 'https://houston-glass.stormcommand.com',
    'NC Architects': 'https://nc-architects-glass.stormcommand.com',
    'Hotels': 'https://hotels-glass.stormcommand.com'
}

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT UNIQUE,
        source_app TEXT,
        city TEXT,
        category TEXT,
        website TEXT,
        email TEXT,
        phone TEXT,
        last_contacted DATE,
        times_contacted INTEGER DEFAULT 0,
        opportunity_score INTEGER
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS collab_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        idea_type TEXT,
        description TEXT,
        priority TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    total_leads = c.execute('SELECT COUNT(*) FROM leads').fetchone()[0]
    cities_active = c.execute('SELECT COUNT(DISTINCT city) FROM leads').fetchone()[0]
    emails_sent = c.execute('SELECT SUM(times_contacted) FROM leads').fetchone()[0] or 0

    success_rate = 0
    if emails_sent > 0:
        successful = c.execute('SELECT COUNT(*) FROM leads WHERE opportunity_score >= 70').fetchone()[0]
        success_rate = round((successful / total_leads * 100) if total_leads > 0 else 0, 1)

    conn.close()

    return {
        'total_leads': total_leads,
        'cities_active': cities_active,
        'emails_sent': emails_sent,
        'success_rate': success_rate
    }

def create_hurricane_map():
    m = folium.Map(location=[28.5, -88.0], zoom_start=5)

    hurricane_zones = [
        {'name': 'Miami', 'lat': 25.7617, 'lon': -80.1918, 'risk': 'High'},
        {'name': 'Houston', 'lat': 29.7604, 'lon': -95.3698, 'risk': 'High'},
        {'name': 'New Orleans', 'lat': 29.9511, 'lon': -90.0715, 'risk': 'High'},
        {'name': 'Charleston', 'lat': 32.7765, 'lon': -79.9311, 'risk': 'Medium'},
        {'name': 'Tampa', 'lat': 27.9506, 'lon': -82.4572, 'risk': 'High'},
    ]

    for zone in hurricane_zones:
        color = 'red' if zone['risk'] == 'High' else 'orange'
        folium.CircleMarker(
            location=[zone['lat'], zone['lon']],
            radius=15,
            popup=f"{zone['name']}<br>Risk: {zone['risk']}",
            color=color,
            fill=True,
            fillColor=color
        ).add_to(m)

    return m._repr_html_()

@app.route('/')
def index():
    stats = get_stats()
    map_html = create_hurricane_map()

    app_grid = []
    for city in CITIES:
        if city == 'Houston':
            app_grid.append({'name': city, 'type': 'city', 'active': True, 'url': ACTIVE_APPS.get(city, '#')})
        else:
            app_grid.append({'name': city, 'type': 'city', 'active': False, 'url': '#'})

    for category in CATEGORIES:
        if category == 'Hotels' or category == 'Architects':
            active = True
            if category == 'Architects':
                url = ACTIVE_APPS.get('NC Architects', '#')
            else:
                url = ACTIVE_APPS.get(category, '#')
            app_grid.append({'name': category, 'type': 'category', 'active': active, 'url': url})
        else:
            app_grid.append({'name': category, 'type': 'category', 'active': False, 'url': '#'})

    try:
        feed = feedparser.parse('https://www.nhc.noaa.gov/xml/ATCF_ATL.xml')
        news_items = feed.entries[:5] if feed.entries else []
    except:
        news_items = []

    return render_template('index.html',
                         stats=stats,
                         map_html=map_html,
                         app_grid=app_grid,
                         news_items=news_items)

@app.route('/email-generator', methods=['GET', 'POST'])
def email_generator():
    if request.method == 'POST':
        data = request.json
        company = data.get('company_name')
        website = data.get('website')
        city = data.get('city')
        category = data.get('category')

        email_content = f"""Subject: Hurricane Protection for {company}

Dear {company} Team,

As a {category} in {city}, your property faces significant hurricane risk. Glass Strategies specializes in impact-resistant window solutions that meet Miami-Dade standards. We've protected over 500 properties in hurricane zones with our certified systems.

Would you be interested in a brief consultation about fortifying {company} before the next hurricane season?

Best regards,
Glass Strategies Team"""

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        try:
            c.execute('''INSERT OR REPLACE INTO leads
                        (company_name, source_app, city, category, website, last_contacted, times_contacted, opportunity_score)
                        VALUES (?, ?, ?, ?, ?, ?, 1, ?)''',
                     (company, 'email-generator', city, category, website, datetime.now().strftime('%Y-%m-%d'), 50))
            conn.commit()
        except:
            pass
        conn.close()

        return jsonify({'email': email_content})

    return render_template('email_generator.html', cities=CITIES, categories=CATEGORIES)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/strategy')
def strategy():
    return render_template('strategy.html')

@app.route('/collab', methods=['GET', 'POST'])
def collab():
    if request.method == 'POST':
        data = request.json

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO collab_submissions (name, idea_type, description, priority)
                     VALUES (?, ?, ?, ?)''',
                  (data['name'], data['type'], data['description'], data['priority']))
        conn.commit()
        submission_id = c.lastrowid
        conn.close()

        return jsonify({'success': True, 'id': submission_id})

    # GET request - load previous submissions
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    submissions = c.execute('''SELECT name, idea_type, description, priority, timestamp
                               FROM collab_submissions
                               ORDER BY timestamp DESC
                               LIMIT 20''').fetchall()
    conn.close()

    return render_template('collab.html', submissions=submissions)

@app.route('/prompts')
def prompts():
    return render_template('prompts.html')

@app.route('/reports')
def reports():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    by_city = c.execute('''SELECT city, COUNT(*) as count
                          FROM leads
                          GROUP BY city
                          ORDER BY count DESC''').fetchall()

    by_category = c.execute('''SELECT category, COUNT(*) as count
                              FROM leads
                              GROUP BY category
                              ORDER BY count DESC''').fetchall()

    duplicates = c.execute('''SELECT company_name, COUNT(*) as count
                             FROM leads
                             GROUP BY company_name
                             HAVING count > 1''').fetchall()

    conn.close()

    return render_template('reports.html',
                         by_city=by_city,
                         by_category=by_category,
                         duplicates=duplicates)

@app.route('/export-csv')
def export_csv():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    leads = c.execute('SELECT * FROM leads').fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Company', 'Source', 'City', 'Category', 'Website', 'Email', 'Phone', 'Last Contacted', 'Times Contacted', 'Score'])
    writer.writerows(leads)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'leads_export_{datetime.now().strftime("%Y%m%d")}.csv'
    )

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)