#!/usr/bin/env python3
"""
Modern Web GUI for Crypto Tax Tool
A beautiful, responsive web interface for the crypto tax calculation tool.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.main import main as cli_main
    from src.auto_detect import ExchangeDetector, auto_process_input_folder
    from src.calculate import calculate_taxes
    from src.report import generate_all_reports
    from src.config import load_exchange_mappings
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
app.secret_key = 'crypto_tax_tool_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_mb(filepath):
    """Get file size in MB."""
    return os.path.getsize(filepath) / (1024 * 1024)

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads."""
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
                errors.append(f"{filename} is too large (max 50MB)")
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

@app.route('/detect', methods=['POST'])
def detect_exchanges():
    """Detect exchange formats for uploaded files."""
    try:
        detector = ExchangeDetector()
        results = []
        
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath) and allowed_file(filename):
                exchange, confidence, details = detector.detect_exchange(filepath)
                results.append({
                    'filename': filename,
                    'exchange': exchange,
                    'confidence': round(confidence * 100, 1),
                    'needs_confirmation': confidence < 0.7,
                    'details': details
                })
        
        return jsonify({'results': results})
    
    except Exception as e:
        logger.error(f"Detection error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process_files():
    """Process uploaded files with exchange detection."""
    try:
        data = request.get_json()
        exchange_mappings = data.get('exchange_mappings', {})
        
        # Create temporary input directory
        temp_input = tempfile.mkdtemp()
        
        # Copy files to temp input with exchange-specific naming
        for filename, exchange in exchange_mappings.items():
            if exchange and exchange != 'skip':
                src_path = os.path.join(UPLOAD_FOLDER, filename)
                dst_path = os.path.join(temp_input, filename)
                shutil.copy2(src_path, dst_path)
        
        # Process files
        results = auto_process_input_folder(
            input_dir=temp_input,
            output_dir=OUTPUT_FOLDER,
            interactive=False
        )
        
        # Cleanup temp directory
        shutil.rmtree(temp_input)
        
        return jsonify({
            'success': True,
            'results': results,
            'message': f'Processed {len(results)} files successfully'
        })
    
    except Exception as e:
        logger.error(f"Processing error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/calculate', methods=['POST'])
def calculate_tax():
    """Calculate taxes from processed files."""
    try:
        data = request.get_json()
        method = data.get('method', 'fifo')
        currency = data.get('currency', 'usd')
        
        # Find the combined normalized file
        normalized_files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('_normalized.csv')]
        
        if not normalized_files:
            return jsonify({'error': 'No normalized files found. Please process files first.'}), 400
        
        # Use the first normalized file (or combine them)
        input_file = os.path.join(OUTPUT_FOLDER, normalized_files[0])
        
        # Calculate taxes
        gains_df, total_income = calculate_taxes(input_file, method, currency)
        
        # Generate reports
        generate_all_reports()
        
        # Prepare results
        results = {
            'method': method,
            'currency': currency,
            'total_transactions': len(gains_df) if not gains_df.empty else 0,
            'short_term_gains': float(gains_df[gains_df['short_term']]['gain_loss'].sum()) if not gains_df.empty else 0,
            'long_term_gains': float(gains_df[~gains_df['short_term']]['gain_loss'].sum()) if not gains_df.empty else 0,
            'total_income': float(total_income),
            'gains_data': gains_df.to_dict('records') if not gains_df.empty else []
        }
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Calculation error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/reports')
def list_reports():
    """List available reports."""
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
                    'url': f'/download/{filename}'
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
        'processed_files': len([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith('_normalized.csv')]),
        'reports_available': len([f for f in os.listdir(os.path.join(OUTPUT_FOLDER, 'reports')) if os.path.isfile(os.path.join(OUTPUT_FOLDER, 'reports', f))]) if os.path.exists(os.path.join(OUTPUT_FOLDER, 'reports')) else 0
    }
    return jsonify(status)

if __name__ == '__main__':
    print(" Starting Crypto Tax Tool Web Interface...")
    print(" Open your browser to: http://localhost:5000")
    print(" All processing happens locally - your data never leaves your computer")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
