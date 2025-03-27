from flask import Flask, request, redirect, url_for, send_from_directory, jsonify, session, abort
from flask_cors import CORS
import csv
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Admin credentials
ADMIN_USERNAME = 'hadiqa'
ADMIN_PASSWORD = 'Pmme!chk'

# Ensure the data directory exists
if not os.path.exists('data'):
    os.makedirs('data')

# Ensure static directories exist
for dir_path in ['static', 'static/admin']:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

@app.route('/')
def index():
    try:
        return send_from_directory('static', 'index.html')
    except Exception as e:
        app.logger.error(f"Error serving index.html: {str(e)}")
        abort(500)

@app.route('/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory('static', filename)
    except Exception as e:
        app.logger.error(f"Error serving {filename}: {str(e)}")
        abort(404)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Get form data
        data = request.form
        
        # Create filename with current date
        filename = f'data/waitlist_{datetime.now().strftime("%Y%m%d")}.csv'
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.exists(filename)
        
        # Write to CSV
        with open(filename, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                # Write headers if file is new
                writer.writerow(['Timestamp', 'First Name', 'Email', 'Focus Area', 'Early Access', 'Feedback'])
            
            # Write data
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data.get('firstName', ''),
                data.get('email', ''),
                data.get('focus', ''),
                data.get('earlyAccess', ''),
                data.get('feedback', '')
            ])
        
        return redirect('/thank-you')
    except Exception as e:
        app.logger.error(f"Error in submit: {str(e)}")
        abort(500)

@app.route('/thank-you')
def thank_you():
    return app.send_static_file('thank-you.html')

@app.route('/admin')
def admin():
    return redirect('/admin/login')

@app.route('/admin/login')
def admin_login():
    try:
        return send_from_directory('static/admin', 'login.html')
    except Exception as e:
        app.logger.error(f"Error serving login.html: {str(e)}")
        abort(404)

@app.route('/admin/authenticate', methods=['POST'])
def authenticate():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['authenticated'] = True
            return redirect('/admin/dashboard')
        else:
            return redirect('/admin/login')
    except Exception as e:
        app.logger.error(f"Error in authenticate: {str(e)}")
        abort(500)

@app.route('/admin/dashboard')
def admin_dashboard():
    try:
        if not session.get('authenticated'):
            return redirect('/admin/login')
        return send_from_directory('static/admin', 'dashboard.html')
    except Exception as e:
        app.logger.error(f"Error serving dashboard.html: {str(e)}")
        abort(404)

@app.route('/admin/data')
def get_data():
    try:
        if not session.get('authenticated'):
            return jsonify({'error': 'Unauthorized'}), 401
        
        all_data = []
        data_dir = 'data'
        
        # Read all CSV files in the data directory
        for filename in os.listdir(data_dir):
            if filename.startswith('waitlist_') and filename.endswith('.csv'):
                with open(os.path.join(data_dir, filename), 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        all_data.append(row)
        
        # Sort data by timestamp (newest first)
        all_data.sort(key=lambda x: x['Timestamp'], reverse=True)
        
        return jsonify(all_data)
    except Exception as e:
        app.logger.error(f"Error in get_data: {str(e)}")
        abort(500)

@app.route('/admin/logout')
def logout():
    session.pop('authenticated', None)
    return redirect('/admin/login')

@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
def handle_error(error):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error {error.code}</title>
        <style>
            body {{ font-family: 'Inter', sans-serif; text-align: center; padding: 40px; }}
            h1 {{ color: #2D3436; }}
            .error-container {{ max-width: 600px; margin: 0 auto; }}
            .back-link {{ color: #81B29A; text-decoration: none; }}
            .back-link:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1>Error {error.code}</h1>
            <p>{error.description}</p>
            <p><a href="/" class="back-link">← Return to Home</a></p>
        </div>
    </body>
    </html>
    """, error.code

if __name__ == '__main__':
    # Use port 8080 instead of 5000 to avoid conflict with AirPlay
    app.run(debug=True, port=8080, host='0.0.0.0') 