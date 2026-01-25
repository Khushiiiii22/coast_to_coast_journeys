from flask import Blueprint, request, jsonify, current_app
import datetime

visa_bp = Blueprint('visa', __name__, url_prefix='/api/visa')

@visa_bp.route('/submit', methods=['POST'])
def submit_visa_application():
    """
    Handle visa application submission.
    Since SMTP is not configured, this will log the email content.
    """
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        # Extract data
        full_name = data.get('fullName')
        email = data.get('email')
        phone = data.get('phone')
        nationality = data.get('nationality')
        destination = data.get('destination')
        visa_type = data.get('visaType')
        travel_date = data.get('travelDate')
        prev_visa = data.get('prevVisa')
        additional_info = data.get('additionalInfo')

        # Validate required fields
        if not all([full_name, email, phone, nationality, destination, visa_type]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Construct Email Content
        subject = f"New Visa Application: {full_name} - {destination}"
        body = f"""
        NEW VISA APPLICATION RECEIVED
        -----------------------------
        Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        APPLICANT DETAILS:
        Name: {full_name}
        Email: {email}
        Phone: {phone}
        Nationality: {nationality}
        
        VISA REQUEST:
        Destination: {destination}
        Visa Type: {visa_type}
        Expected Travel Date: {travel_date or 'Not specified'}
        Previous Visa: {prev_visa or 'N/A'}
        
        ADDITIONAL INFO:
        {additional_info or 'None'}
        
        -----------------------------
        Please contact the applicant to proceed.
        """

        # Log the "Email" (Simulate sending)
        print("\n" + "="*50)
        print(f"📧 SENDING EMAIL to admin@c2cjourneys.com")
        print(f"Subject: {subject}")
        print(body)
        print("="*50 + "\n")

        # In a real app with Supabase, we could also save this to a 'visa_inquiries' table
        # For now, just success
        
        return jsonify({
            'success': True, 
            'message': 'Application received successfully',
            'application_id': f"VISA-{int(datetime.datetime.now().timestamp())}"
        })

    except Exception as e:
        print(f"Error processing visa application: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
