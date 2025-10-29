#!/usr/bin/env python3
"""
Crypto Tax Tool - Web Interface
Professional-grade cryptocurrency tax calculations with modern web UI
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.web.simple_web_app import app

if __name__ == "__main__":
    print("Starting Professional Crypto Tax Tool...")
    print("Web Interface: http://localhost:5000")
    print("Privacy: All processing happens locally on your computer")
    print("Cost: Completely FREE (no subscription, no hidden fees)")
    print("=" * 60)
    
    app.run(debug=False, host='0.0.0.0', port=5000)