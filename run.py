#!/usr/bin/env python3
"""Simple runner script to handle import paths correctly."""

import sys
import os
from pathlib import Path

# Add both current directory and src directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'src'))

# Now import and run the main module
if __name__ == '__main__':
    from src.main import main
    main()