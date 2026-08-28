from typing import List, Dict, Any

def extract_temporal_features(events: List[Dict[Any, Any]]) -> Dict[str, Any]:
    if not events:
        return {
            "window_start": None,
            "window_end": None,
            "event_count": 0,
            "session_duration": 0.0,
            "events_per_minute": 0.0
        }
        
    start_time = events[0]["timestamp"]
    end_time = events[-1]["timestamp"]
    duration = (end_time - start_time).total_seconds()
    
    event_count = len(events)
    
    if duration > 0:
        events_per_minute = event_count / (duration / 60.0)
    else:
        events_per_minute = float(event_count) # all events happened instantly
        
    return {
        "window_start": start_time,
        "window_end": end_time,
        "event_count": event_count,
        "session_duration": duration,
        "events_per_minute": events_per_minute
    }
