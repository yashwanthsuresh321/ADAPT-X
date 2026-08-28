from typing import List, Dict, Any

def extract_authentication_features(events: List[Dict[Any, Any]]) -> Dict[str, Any]:
    if not events:
        return {
            "authentication_attempts": 0,
            "authentication_failures": 0,
            "authentication_successes": 0,
            "authentication_failure_rate": None
        }
        
    attempts = 0
    failures = 0
    successes = 0
    
    for event in events:
        # Check if event represents authentication
        event_type = event.get("event_type", "")
        action = event.get("action", "")
        status = event.get("status", "")
        
        # In our schema, ssh_connection connect, or db connect failures
        # Or cowrie login attempts (often logged as login action)
        # We also specifically parse 'failed' or 'success' status
        if action in ["connect", "login", "authenticate"]:
            # If the event_type is connection related and we have success/failed status
            if status in ["success", "failed"]:
                attempts += 1
                if status == "success":
                    successes += 1
                else:
                    failures += 1
                    
    rate = None
    if attempts > 0:
        rate = failures / float(attempts)
        
    return {
        "authentication_attempts": attempts,
        "authentication_failures": failures,
        "authentication_successes": successes,
        "authentication_failure_rate": rate
    }
