try:
    import stripe
except ImportError:
    stripe = None

import logging

class StripeService:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        if stripe and secret_key:
            stripe.api_key = secret_key
            logging.info("Stripe API configured")
        
    def create_checkout_session(self, amount, currency, reference_id, success_url, cancel_url):
        """Create a Stripe checkout session for a payment"""
        try:
            # Stripe expects amounts in cents for USD, etc.
            # Convert decimal amount to integer smallest currency unit
            amount_in_cents = int(float(amount) * 100)
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': currency.lower(),
                        'product_data': {
                            'name': f'Booking Reference: {reference_id}',
                        },
                        'unit_amount': amount_in_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                adaptive_pricing={"enabled": False},
                success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}&booking_id=" + reference_id,
                cancel_url=cancel_url,
                client_reference_id=reference_id
            )
            return {
                'status': 'success',
                'id': session.id,
                'url': session.url
            }
        except Exception as e:
            logging.error(f"Error creating Stripe checkout session: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
            
    def verify_session(self, session_id):
        """Verify if a checkout session was completed successfully"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            return {
                'status': 'success',
                'payment_status': session.payment_status,
                'booking_id': session.client_reference_id
            }
        except Exception as e:
            logging.error(f"Error verifying Stripe session: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

# Create a singleton instance that will be configured in app.py
stripe_service = None

def init_stripe(secret_key):
    global stripe_service
    stripe_service = StripeService(secret_key)
    return stripe_service
