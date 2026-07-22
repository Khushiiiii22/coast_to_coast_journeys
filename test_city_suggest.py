import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from backend.services.etg_service import ETGApiService
import json

# This will fail locally with 403, but let's see if we can find anything else out.
