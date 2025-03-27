from flask import Flask, request, render_template, send_from_directory, abort, jsonify, url_for, redirect
from flask_cors import CORS
import os
import csv
from datetime import datetime
import json
import signal
import atexit

app = Flask(__name__, static_url_path='')
CORS(app)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Ensure static directories exist
os.makedirs('static', exist_ok=True)
os.makedirs('static/admin', exist_ok=True)

def cleanup_handler():
    """Handle cleanup when the app shuts down"""
    import multiprocessing.resource_tracker as rt
    # Clear any remaining semaphores
    if hasattr(rt, '_CLEANUP_FUNCS'):
        for func in rt._CLEANUP_FUNCS.values():
            try:
                func()
            except Exception:
                pass

# Register cleanup handlers
atexit.register(cleanup_handler)
signal.signal(signal.SIGINT, lambda s, f: cleanup_handler())

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/thank-you')
def thank_you():
    return send_from_directory('static', 'thank-you.html')

@app.route('/admin')
def admin():
    return send_from_directory('static/admin', 'dashboard.html')

@app.route('/admin/login')
def admin_login():
    return send_from_directory('static/admin', 'login.html')

@app.route('/submit', methods=['POST'])
def submit():
    # Handle form submission
    first_name = request.form.get('firstName')
    email = request.form.get('email')
    focus = request.form.get('focus')
    
    # Here you would typically save this to a database
    print(f"New submission: {first_name} ({email}) - Focus: {focus}")
    
    return redirect(url_for('thank_you'))

@app.route('/api/waitlist')
def get_waitlist():
    try:
        # Get the most recent CSV file
        csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]
        if not csv_files:
            return jsonify([])
        
        latest_file = max(csv_files)
        data = []
        
        with open(os.path.join('data', latest_file), 'r') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            data = request.form.to_dict()
        
        # Simple authentication (replace with proper authentication in production)
        if data.get('username') == 'admin' and data.get('password') == 'admin123':
            return jsonify({"status": "success"})
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"status": "error", "message": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

# This is for local development
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=8080, debug=True)
    except KeyboardInterrupt:
        cleanup_handler()
        print("\nShutting down gracefully...") 