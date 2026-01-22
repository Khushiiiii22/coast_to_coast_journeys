"""
PayPal Payment Service
Handles PayPal payment processing, order creation, and verification
"""
import requests
import base64
import json
from datetime import datetime

class PayPalService:
    """Service for PayPal payment integration"""
    
    def __init__(self, client_id, client_secret, mode='sandbox'):
        """
        Initialize PayPal client
        
        Args:
            client_id: PayPal Client ID
            client_secret: PayPal Client Secret
            mode: 'sandbox' or 'live'
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.mode = mode
        
        # Set API base URL based on mode
        if mode == 'live':
            self.base_url = 'https://api-m.paypal.com'
        else:
            self.base_url = 'https://api-m.sandbox.paypal.com'
        
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self):
        """
        Get OAuth 2.0 access token from PayPal
        
        Returns:
            str: Access token
        """
        # Check if we have a valid token
        if self.access_token and self.token_expires_at:
            if datetime.now().timestamp() < self.token_expires_at:
                return self.access_token
        
        # Get new token
        url = f'{self.base_url}/v1/oauth2/token'
        
        # Create Basic Auth header
        credentials = f'{self.client_id}:{self.client_secret}'
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {'grant_type': 'client_credentials'}
        
        try:
            # Debug logging
            print(f"PayPal auth attempt to: {url}")
            print(f"Client ID length: {len(self.client_id)}")
            
            response = requests.post(url, headers=headers, data=data)
            
            # Log response for debugging
            print(f"PayPal auth response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"PayPal auth error response: {response.text}")
            
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Set expiration (usually 9 hours, we'll refresh after 8)
            expires_in = token_data.get('expires_in', 28800)  # Default 8 hours
            self.token_expires_at = datetime.now().timestamp() + (expires_in - 3600)
            
            print("✅ PayPal authentication successful")
            return self.access_token
        except requests.exceptions.HTTPError as e:
            error_msg = f'PayPal HTTP error: {e}'
            if hasattr(e.response, 'text'):
                error_msg += f' - Response: {e.response.text}'
            print(error_msg)
            return None
        except Exception as e:
            print(f'PayPal auth error: {e}')
            return None
    
    def create_order(self, amount, currency='USD', description='Hotel Booking'):
        """
        Create a PayPal order
        
        Args:
            amount: Amount in decimal (e.g., 100.00)
            currency: Currency code (USD, EUR, INR, etc.)
            description: Order description
        
        Returns:
            dict: Order details including order_id
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to authenticate with PayPal'}
            
            url = f'{self.base_url}/v2/checkout/orders'
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            # Convert INR to USD if needed (PayPal doesn't support INR directly)
            if currency == 'INR':
                amount = round(amount / 83, 2)  # Approximate conversion
                currency = 'USD'
            
            order_data = {
                'intent': 'CAPTURE',
                'purchase_units': [{
                    'description': description,
                    'amount': {
                        'currency_code': currency,
                        'value': f'{amount:.2f}'
                    }
                }],
                'application_context': {
                    'return_url': 'http://localhost:5000/payment-success.html',
                    'cancel_url': 'http://localhost:5000/payment-checkout.html'
                }
            }
            
            response = requests.post(url, headers=headers, json=order_data)
            response.raise_for_status()
            
            order = response.json()
            
            # Get approval URL
            approval_url = None
            for link in order.get('links', []):
                if link.get('rel') == 'approve':
                    approval_url = link.get('href')
                    break
            
            return {
                'success': True,
                'order_id': order['id'],
                'approval_url': approval_url,
                'status': order['status']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def capture_order(self, order_id):
        """
        Capture/complete a PayPal order after customer approval
        
        Args:
            order_id: PayPal order ID
        
        Returns:
            dict: Capture response
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to authenticate with PayPal'}
            
            url = f'{self.base_url}/v2/checkout/orders/{order_id}/capture'
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            
            capture_data = response.json()
            
            return {
                'success': True,
                'order_id': capture_data['id'],
                'status': capture_data['status'],
                'data': capture_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_order_details(self, order_id):
        """
        Get PayPal order details
        
        Args:
            order_id: PayPal order ID
        
        Returns:
            dict: Order details
        """
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {'success': False, 'error': 'Failed to authenticate with PayPal'}
            
            url = f'{self.base_url}/v2/checkout/orders/{order_id}'
            
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            order_data = response.json()
            
            return {
                'success': True,
                'data': order_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
