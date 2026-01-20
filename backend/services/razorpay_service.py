"""
Razorpay Payment Service
Handles payment processing, order creation, and verification
"""
import razorpay
import hmac
import hashlib
import time

class RazorpayService:
    """Service for Razorpay payment integration"""
    
    def __init__(self, key_id, key_secret):
        """
        Initialize Razorpay client
        
        Args:
            key_id: Razorpay Key ID (rzp_test_xxx or rzp_live_xxx)
            key_secret: Razorpay Key Secret
        """
        self.client = razorpay.Client(auth=(key_id, key_secret))
        self.key_id = key_id
        self.key_secret = key_secret
    
    def create_order(self, amount, currency='INR', receipt=None, notes=None):
        """
        Create a Razorpay order
        
        Args:
            amount: Amount in smallest currency unit (paise for INR, cents for USD)
            currency: Currency code (INR, USD, etc.)
            receipt: Optional receipt ID
            notes: Optional dict of notes
        
        Returns:
            dict: Order details including order_id
        """
        try:
            # Amount should be in paise (multiply by 100 for INR)
            if currency == 'INR':
                amount_paise = int(amount * 100)
            else:
                amount_paise = int(amount * 100)  # For USD cents
            
            data = {
                'amount': amount_paise,
                'currency': currency,
                'receipt': receipt or f'order_{int(time.time())}',
                'notes': notes or {}
            }
            
            order = self.client.order.create(data=data)
            
            return {
                'success': True,
                'order_id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'receipt': order['receipt'],
                'status': order['status']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verify payment signature to ensure payment authenticity
        
        Args:
            razorpay_order_id: Order ID from Razorpay
            razorpay_payment_id: Payment ID from Razorpay
            razorpay_signature: Signature from Razorpay
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Create signature verification string
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            
            # Generate expected signature
            expected_signature = hmac.new(
                self.key_secret.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, razorpay_signature)
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    def capture_payment(self, payment_id, amount, currency='INR'):
        """
        Capture a payment (for authorized payments)
        
        Args:
            payment_id: Payment ID to capture
            amount: Amount to capture (in smallest unit)
            currency: Currency code
        
        Returns:
            dict: Payment capture response
        """
        try:
            if currency == 'INR':
                amount_paise = int(amount * 100)
            else:
                amount_paise = int(amount * 100)
            
            payment = self.client.payment.capture(
                payment_id,
                amount_paise
            )
            
            return {
                'success': True,
                'payment_id': payment['id'],
                'amount': payment['amount'],
                'status': payment['status']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def fetch_payment(self, payment_id):
        """
        Fetch payment details
        
        Args:
            payment_id: Payment ID
        
        Returns:
            dict: Payment details
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            return {
                'success': True,
                'data': payment
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_refund(self, payment_id, amount=None, notes=None):
        """
        Create a refund
        
        Args:
            payment_id: Payment ID to refund
            amount: Amount to refund (None for full refund)
            notes: Optional refund notes
        
        Returns:
            dict: Refund details
        """
        try:
            data = {}
            
            if amount is not None:
                # Partial refund
                data['amount'] = int(amount * 100)  # Convert to paise
            
            if notes:
                data['notes'] = notes
            
            refund = self.client.payment.refund(payment_id, data)
            
            return {
                'success': True,
                'refund_id': refund['id'],
                'amount': refund['amount'],
                'status': refund['status']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def fetch_refund(self, refund_id):
        """
        Fetch refund details
        
        Args:
            refund_id: Refund ID
        
        Returns:
            dict: Refund details
        """
        try:
            refund = self.client.refund.fetch(refund_id)
            return {
                'success': True,
                'data': refund
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
