#!/usr/bin/env python3
"""
Crypto Tax Tool - Command Line Interface
Professional-grade cryptocurrency tax calculations
"""

import sys
import os
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.cli.main import main

if __name__ == "__main__":
    main()
