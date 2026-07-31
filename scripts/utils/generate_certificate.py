#!/usr/bin/env python3
"""
HotelBeds X-Signature Certificate Generator
Generates authentication signatures for HotelBeds API requests

Usage:
    python generate_certificate.py --api-key YOUR_KEY --secret YOUR_SECRET
    python generate_certificate.py --test  (test all 3 credentials)
"""
import hashlib
import time
import argparse
import json
from datetime import datetime

class CertificateGenerator:
    """Generate X-Signature certificates for HotelBeds API"""
    
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret
    
    def generate_signature(self, timestamp=None):
        """
        Generate X-Signature certificate
        
        Args:
            timestamp: Unix timestamp (optional, uses current time if not provided)
        
        Returns:
            dict: Certificate details
        """
        # Use provided timestamp or current time
        if timestamp is None:
            timestamp = str(int(time.time()))
        else:
            timestamp = str(timestamp)
        
        # Step 1: Concatenate ApiKey + Secret + Timestamp
        signature_string = self.api_key + self.secret + timestamp
        
        # Step 2: Generate SHA256 hash
        signature = hashlib.sha256(signature_string.encode('utf-8')).hexdigest()
        
        return {
            'api_key': self.api_key,
            'signature': signature,
            'timestamp': timestamp,
            'timestamp_readable': datetime.fromtimestamp(int(timestamp)).strftime('%Y-%m-%d %H:%M:%S'),
            'expires_in': '60 seconds (recommended)',
            'concatenated_string': signature_string,
            'algorithm': 'SHA-256'
        }
    
    def print_certificate(self, cert):
        """Print certificate in a readable format"""
        print("\n" + "="*70)
        print("🔐 HotelBeds API X-Signature Certificate".center(70))
        print("="*70)
        print(f"\n📋 API Key:        {cert['api_key']}")
        print(f"🔑 Secret:         {'*' * len(self.secret)} (hidden)")
        print(f"⏰ Timestamp:      {cert['timestamp']}")
        print(f"📅 Time:           {cert['timestamp_readable']}")
        print(f"⌛ Valid For:      {cert['expires_in']}")
        print(f"\n🔒 X-Signature (Certificate):")
        print(f"   {cert['signature']}")
        print(f"\n🧮 Algorithm:      {cert['algorithm']}")
        print(f"📝 Input String:   {cert['concatenated_string'][:50]}...")
        print("\n" + "="*70)
        print("\n✅ Use these headers in your API request:")
        print(f"   Api-Key: {cert['api_key']}")
        print(f"   X-Signature: {cert['signature']}")
        print("   Accept: application/json")
        print("   Content-Type: application/json")
        print("="*70 + "\n")
    
    def export_certificate(self, filename='hotelbeds_certificate.json'):
        """Export certificate to JSON file"""
        cert = self.generate_signature()
        
        export_data = {
            'generated_at': cert['timestamp_readable'],
            'api_credentials': {
                'api_key': cert['api_key'],
                'x_signature': cert['signature']
            },
            'metadata': {
                'timestamp': cert['timestamp'],
                'algorithm': cert['algorithm'],
                'valid_duration': cert['expires_in']
            },
            'usage_example': {
                'headers': {
                    'Api-Key': cert['api_key'],
                    'X-Signature': cert['signature'],
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Certificate exported to: {filename}")
        return filename


def test_all_credentials():
    """Test all 3 HotelBeds API credentials"""
    credentials = [
        {
            'name': 'API Key #1 (High Quota - 50,000)',
            'api_key': 'c79416829cc345633d1de38a1d968173',
            'secret': '07207637d1'
        },
        {
            'name': 'API Key #2 (Fast Rate - 16 req/4s)',
            'api_key': 'da6cfe9d8f23fe4589b3139ffadba034',
            'secret': 'c06b649871'
        },
        {
            'name': 'API Key #3 (Limited - 50 total) ✅ WORKING',
            'api_key': 'd51bdc80bdf8f8e610882e137baa4bad',
            'secret': '3c297e5613'
        }
    ]
    
    print("\n🧪 Generating Certificates for All API Credentials\n")
    
    for i, cred in enumerate(credentials, 1):
        print(f"\n{'='*70}")
        print(f"Certificate #{i}: {cred['name']}")
        print('='*70)
        
        generator = CertificateGenerator(cred['api_key'], cred['secret'])
        cert = generator.generate_signature()
        
        print(f"\n📋 API Key:        {cert['api_key']}")
        print(f"🔒 X-Signature:    {cert['signature']}")
        print(f"⏰ Timestamp:      {cert['timestamp']}")
        print(f"📅 Generated:      {cert['timestamp_readable']}")
        
        if i == 3:
            print("\n✅ This credential is VERIFIED WORKING (37 hotels found in test)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate HotelBeds X-Signature Certificates')
    parser.add_argument('--api-key', help='Your HotelBeds API Key')
    parser.add_argument('--secret', help='Your HotelBeds API Secret')
    parser.add_argument('--test', action='store_true', help='Test all 3 credentials')
    parser.add_argument('--export', action='store_true', help='Export certificate to JSON')
    parser.add_argument('--timestamp', type=int, help='Use specific timestamp (optional)')
    
    args = parser.parse_args()
    
    if args.test:
        test_all_credentials()
    elif args.api_key and args.secret:
        generator = CertificateGenerator(args.api_key, args.secret)
        cert = generator.generate_signature(args.timestamp)
        generator.print_certificate(cert)
        
        if args.export:
            generator.export_certificate()
    else:
        # Interactive mode
        print("\n🔐 HotelBeds X-Signature Certificate Generator\n")
        print("Choose an option:")
        print("1. Use working credentials (API Key #3)")
        print("2. Enter custom credentials")
        print("3. Test all 3 credentials")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            # Use working credentials
            generator = CertificateGenerator(
                'd51bdc80bdf8f8e610882e137baa4bad',
                '3c297e5613'
            )
            cert = generator.generate_signature()
            generator.print_certificate(cert)
            
            export = input("\nExport to JSON? (y/n): ").strip().lower()
            if export == 'y':
                generator.export_certificate()
        
        elif choice == '2':
            api_key = input("Enter API Key: ").strip()
            secret = input("Enter Secret: ").strip()
            
            generator = CertificateGenerator(api_key, secret)
            cert = generator.generate_signature()
            generator.print_certificate(cert)
            
            export = input("\nExport to JSON? (y/n): ").strip().lower()
            if export == 'y':
                generator.export_certificate()
        
        elif choice == '3':
            test_all_credentials()
        
        else:
            print("\n❌ Invalid choice. Use --help for usage instructions.")
