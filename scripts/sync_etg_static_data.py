#!/usr/bin/env python3
"""
ETG Static Data Sync Scheduler
Per ETG Certification Requirements (3rd Update - Item 2):
"Content API is now enabled for your key. Switch to weekly so if an 
/info/incremental_dump/ day is missed, the database stays current."

This script is designed to be run via cron on the production server.
Schedule:
- Weekly /hotel/dump/ (Full Dump): Runs every Sunday at 02:00 AM
- Daily /hotel/dump/incremental/ (Incremental Dump): Runs Mon-Sat at 02:00 AM

Example crontab entries:
# ETG Full Dump (Weekly on Sunday)
0 2 * * 0 /path/to/venv/bin/python /path/to/scripts/sync_etg_static_data.py --type full

# ETG Incremental Dump (Daily Mon-Sat)
0 2 * * 1-6 /path/to/venv/bin/python /path/to/scripts/sync_etg_static_data.py --type incremental
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add backend dir to path so we can import etg_service
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

try:
    from services.etg_service import etg_service
    from services.supabase_service import supabase_service
except ImportError as e:
    print(f"Error importing required services: {e}")
    print("Run this script from the project root or ensure backend is in PYTHONPATH")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'etg_sync.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('etg_sync')

def sync_full_dump():
    """Execute weekly full /hotel/dump/"""
    logger.info("Starting WEEKLY FULL /hotel/dump/ sync...")
    try:
        # Trigger the ETG API for a full dump
        result = etg_service.get_hotel_dump(language="en", inventory="all")
        if result.get('success'):
            url = result.get('data', {}).get('url')
            if url:
                logger.info(f"Successfully retrieved full dump URL: {url}")
                logger.info("TODO: Implement download and database upsert logic here")
            else:
                logger.warning("ETG returned success but no URL found in response")
        else:
            logger.error(f"Failed to trigger full dump: {result.get('error')}")
    except Exception as e:
        logger.error(f"Exception during full dump sync: {e}")

def sync_incremental_dump():
    """Execute daily /hotel/dump/incremental/"""
    logger.info("Starting DAILY INCREMENTAL /hotel/dump/incremental/ sync...")
    try:
        # Trigger the ETG API for an incremental dump
        result = etg_service.get_hotel_incremental_dump(language="en")
        if result.get('success'):
            url = result.get('data', {}).get('url')
            if url:
                logger.info(f"Successfully retrieved incremental dump URL: {url}")
                logger.info("TODO: Implement download and database upsert logic here")
            else:
                logger.warning("ETG returned success but no URL found in response")
        else:
            logger.error(f"Failed to trigger incremental dump: {result.get('error')}")
    except Exception as e:
        logger.error(f"Exception during incremental dump sync: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETG Content API Sync Script")
    parser.add_argument('--type', choices=['full', 'incremental'], required=True, 
                        help='Type of sync to run (full=weekly, incremental=daily)')
    
    args = parser.parse_args()
    
    if args.type == 'full':
        sync_full_dump()
    elif args.type == 'incremental':
        sync_incremental_dump()
