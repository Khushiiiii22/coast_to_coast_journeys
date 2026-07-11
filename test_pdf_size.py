import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from services.pdf_service import PDFService
pdf_service = PDFService('/Users/priyeshsrivastava/Travel production/backend/templates')
invoice = pdf_service.generate_invoice({'booking_id': 'TEST-123'})
print(f"Invoice PDF size: {len(invoice)} bytes")
