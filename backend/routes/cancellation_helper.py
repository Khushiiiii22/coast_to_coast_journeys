def format_cancellation_policies(rate):
    """
    Parse and format cancellation policies from rate data
    Adds explicit UTC+0 indication as requested
    """
    cancellation_info = {
        'is_free_cancellation': False,
        'free_cancellation_formatted': None,
        'policies': []
    }
    
    # Safely get payment options and penalties
    payment_options = rate.get('payment_options', {})
    if not payment_options:
        return cancellation_info
        
    penalties = payment_options.get('cancellation_penalties', {})
    if not penalties:
        return cancellation_info
        
    # Check for free cancellation deadline
    free_cancel_limit = penalties.get('free_cancellation_before')
    
    if free_cancel_limit:
        cancellation_info['is_free_cancellation'] = True
        try:
            # Parse datetime e.g. "2025-10-21T08:59:00"
            dt = datetime.strptime(free_cancel_limit, "%Y-%m-%dT%H:%M:%S")
            # Format nicely with UTC indication
            cancellation_info['free_cancellation_formatted'] = {
                'datetime': dt.strftime("%d %b %Y, %H:%M (UTC+0)"),
                'raw': free_cancel_limit
            }
        except Exception:
             cancellation_info['free_cancellation_formatted'] = {
                'datetime': f"{free_cancel_limit} (UTC+0)",
                'raw': free_cancel_limit
            }
    
    # process detailed policies
    raw_policies = penalties.get('policies', [])
    formatted_policies = []
    
    for policy in raw_policies:
        p_start = policy.get('start_at')
        p_end = policy.get('end_at')
        amount = policy.get('amount_charge', '0.00')
        
        policy_type = 'unknown'
        
        # Determine policy type
        try:
            amt_float = float(amount)
            if amt_float == 0:
                policy_type = 'free'
            elif p_start:
                # If it starts at the free cancel limit, it's the penalty phase
                if p_end is None:
                    policy_type = 'full_penalty'
                else:
                    policy_type = 'partial_penalty'
            else:
                # Fallback if no start date but amount > 0
                policy_type = 'full_penalty'
        except:
            pass
            
        # Format dates
        start_fmt = None
        end_fmt = None
        try:
            if p_start:
                s_dt = datetime.strptime(p_start, "%Y-%m-%dT%H:%M:%S")
                start_fmt = s_dt.strftime("%d %b %Y %H:%M (UTC+0)")
            if p_end:
                e_dt = datetime.strptime(p_end, "%Y-%m-%dT%H:%M:%S")
                end_fmt = e_dt.strftime("%d %b %Y %H:%M (UTC+0)")
        except:
            pass
            
        formatted_policies.append({
            'type': policy_type,
            'start_formatted': start_fmt,
            'end_formatted': end_fmt,
            'penalty_amount': amount,
            'currency': rate.get('currency_code', 'USD')
        })
        
    cancellation_info['policies'] = formatted_policies
    return cancellation_info
