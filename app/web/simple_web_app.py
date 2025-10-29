#!/usr/bin/env python3
"""
Simple Crypto Tax Tool - Web Interface
A working version with proper directory structure
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from app.core.auto_processor import process_crypto_taxes
    from app.core.auto_detect import ExchangeDetector
    from app.core.config import load_exchange_mappings
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate random secret key

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'data/output'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_mb(filepath):
    """Get file size in MB."""
    return os.path.getsize(filepath) / (1024 * 1024)

@app.route('/')
def index():
    """Main dashboard - professional landing page."""
    return render_template('web/dashboard.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads with drag & drop."""
    if 'files' not in request.files:
        return jsonify({'error': 'No files selected'}), 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400
    
    uploaded_files = []
    errors = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Check file size
            file.save(filepath)
            if get_file_size_mb(filepath) > MAX_FILE_SIZE / (1024 * 1024):
                errors.append(f"{filename} is too large (max 100MB)")
                os.remove(filepath)
                continue
            
            uploaded_files.append({
                'filename': filename,
                'size_mb': round(get_file_size_mb(filepath), 2),
                'path': filepath
            })
        else:
            errors.append(f"Invalid file type: {file.filename}")
    
    return jsonify({
        'uploaded': uploaded_files,
        'errors': errors,
        'total_files': len(uploaded_files)
    })

@app.route('/process', methods=['POST'])
def process_files():
    """Process uploaded files automatically - ONE CLICK SOLUTION!"""
    try:
        # Move files to input directory
        input_dir = 'data/input'
        os.makedirs(input_dir, exist_ok=True)
        
        # Clear input directory
        for file in os.listdir(input_dir):
            if os.path.isfile(os.path.join(input_dir, file)):
                os.remove(os.path.join(input_dir, file))
        
        # Move uploaded files to input
        for file in os.listdir(UPLOAD_FOLDER):
            if os.path.isfile(os.path.join(UPLOAD_FOLDER, file)):
                shutil.move(os.path.join(UPLOAD_FOLDER, file), os.path.join(input_dir, file))
        
        # Process everything automatically
        results = process_crypto_taxes(input_dir, OUTPUT_FOLDER)
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/reports')
def list_reports():
    """List all generated reports."""
    reports = []
    reports_dir = os.path.join(OUTPUT_FOLDER, 'reports')
    
    if os.path.exists(reports_dir):
        for filename in os.listdir(reports_dir):
            filepath = os.path.join(reports_dir, filename)
            if os.path.isfile(filepath):
                reports.append({
                    'filename': filename,
                    'size_mb': round(get_file_size_mb(filepath), 2),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                    'url': f'/download/{filename}',
                    'type': _get_report_type(filename)
                })
    
    return jsonify({'reports': reports})

@app.route('/download/<filename>')
def download_report(filename):
    """Download a report file."""
    filepath = os.path.join(OUTPUT_FOLDER, 'reports', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/exchanges')
def list_exchanges():
    """List supported exchanges."""
    try:
        exchanges = load_exchange_mappings()
        return jsonify({'exchanges': list(exchanges.keys())})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/status')
def get_status():
    """Get processing status."""
    status = {
        'uploaded_files': len([f for f in os.listdir(UPLOAD_FOLDER) if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))]),
        'input_files': len([f for f in os.listdir('data/input') if os.path.isfile(os.path.join('data/input', f))]) if os.path.exists('data/input') else 0,
        'reports_available': len([f for f in os.listdir(os.path.join(OUTPUT_FOLDER, 'reports')) if os.path.isfile(os.path.join(OUTPUT_FOLDER, 'reports', f))]) if os.path.exists(os.path.join(OUTPUT_FOLDER, 'reports')) else 0
    }
    return jsonify(status)

def _get_report_type(filename):
    """Determine report type from filename."""
    if 'turbotax' in filename.lower():
        return 'TurboTax'
    elif 'hrblock' in filename.lower():
        return 'H&R Block'
    elif 'taxact' in filename.lower():
        return 'TaxAct'
    elif 'taxslayer' in filename.lower():
        return 'TaxSlayer'
    elif 'creditkarma' in filename.lower():
        return 'Credit Karma'
    elif 'coinledger' in filename.lower():
        return 'CoinLedger'
    elif 'portfolio' in filename.lower():
        return 'Portfolio Analysis'
    elif 'summary' in filename.lower():
        return 'Summary Report'
    else:
        return 'Tax Report'

if __name__ == '__main__':
    print("Starting Professional Crypto Tax Tool...")
    print("Web Interface: http://localhost:5000")
    print("Privacy: All processing happens locally on your computer")
    print("Cost: Completely FREE (no subscription, no hidden fees)")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)