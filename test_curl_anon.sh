URL=$(grep SUPABASE_URL .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
KEY=$(grep SUPABASE_ANON_KEY .env | cut -d '=' -f2 | tr -d '"' | tr -d "'")
curl -X POST "$URL/rest/v1/hotel_bookings" \
-H "apikey: $KEY" \
-H "Authorization: Bearer $KEY" \
-H "Content-Type: application/json" \
-d '{
  "partner_order_id": "test_curl_anon_123",
  "hotel_id": "test",
  "hotel_name": "Test",
  "check_in": "2027-01-01",
  "check_out": "2027-01-02",
  "rooms": 1,
  "guests": [],
  "total_amount": 100,
  "currency": "USD",
  "status": "created"
}'
