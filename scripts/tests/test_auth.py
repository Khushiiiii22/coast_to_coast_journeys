import os
import sys
sys.path.insert(0, '/Users/priyeshsrivastava/Travel production/coast_to_coast_journeys/backend')
from app import create_app
from flask import request
app = create_app()

print("App created")
