import sys
sys.path.append('/Users/priyeshsrivastava/Travel production/backend')
from routes.cancellation_helper import format_cancellation_policies

rate = {
  "payment_options": {
    "payment_types": [
      {
        "cancellation_penalties": {
          "policies": [
            {
              "start_at": "2026-05-26T00:00:00",
              "amount_charge": "100.00",
            }
          ],
          "free_cancellation_before": "2026-05-26T00:00:00"
        }
      }
    ]
  }
}
print(format_cancellation_policies(rate))
