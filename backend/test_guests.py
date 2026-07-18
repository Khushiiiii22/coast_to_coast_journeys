import sys
sys.path.append('/Users/priyeshsrivastava/Travel production/backend')
from services.etg_service import etg_service

guests = etg_service.format_guests_for_search(
    adults=2,
    children_ages=[8],
    rooms=[{'adults': 2, 'children': 1, 'childAges': [8]}]
)
print("Guests list:", guests)
