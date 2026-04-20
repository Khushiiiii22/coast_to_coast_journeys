import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from routes.cancellation_helper import format_cancellation_policies

def test_cancellation_parsing():
    print("🔍 Testing Cancellation Policy Parsing...")
    
    # Mock ETG response based on Mikhail's update
    # Note: free_cancellation_before is in penalties
    mock_rate = {
        'payment_options': {
            'cancellation_penalties': {
                'free_cancellation_before': '2026-05-20T00:00:00',
                'policies': []
            }
        },
        'currency_code': 'USD'
    }
    
    print("\n[Input] Rate with free_cancellation_before: 2026-05-20T00:00:00")
    result = format_cancellation_policies(mock_rate)
    
    # Assertions
    assert result['is_free_cancellation'] == True, "❌ is_free_cancellation should be True"
    assert result['free_cancellation_before'] == '2026-05-20T00:00:00', "❌ free_cancellation_before key missing or incorrect"
    assert '20 May 2026' in result['free_cancellation_formatted']['datetime'], "❌ Formatted date missing or incorrect"
    
    print("✅ Case 1 Passed: free_cancellation_before correctly parsed and exposed.")

    # Test Case 2: from_orig_time (local property time)
    mock_rate_local = {
        'payment_options': {
            'cancellation_penalties': {
                'from_orig_time': '2026-05-15T12:00:00',
                'policies': []
            }
        }
    }
    print("\n[Input] Rate with from_orig_time: 2026-05-15T12:00:00")
    result_local = format_cancellation_policies(mock_rate_local)
    assert result_local['is_free_cancellation'] == True
    assert result_local['from_orig_time'] == '2026-05-15T12:00:00'
    print("✅ Case 2 Passed: from_orig_time correctly parsed and exposed.")

    # Test Case 3: Totally non-refundable
    mock_non_ref = {
        'payment_options': {
            'cancellation_penalties': {
                'policies': [{'amount_charge': '100.00', 'start_at': '2026-01-01T00:00:00'}]
            }
        }
    }
    print("\n[Input] Non-refundable rate")
    result_non_ref = format_cancellation_policies(mock_non_ref)
    assert result_non_ref['is_free_cancellation'] == False
    assert result_non_ref['free_cancellation_before'] is None
    print("✅ Case 3 Passed: Non-refundable rate correctly handled.")

    print("\n🚀 All cancellation parsing tests passed!")

if __name__ == "__main__":
    try:
        test_cancellation_parsing()
    except AssertionError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
