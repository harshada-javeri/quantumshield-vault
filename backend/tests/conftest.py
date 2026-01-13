"""Test configuration and fixtures."""

import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Set test environment
os.environ["DATABASE_ENV"] = "test"
