from typing import List, Dict, Any
from datetime import timedelta
import os
import logging

logger = logging.getLogger("sessions.sessionizer")

def sessionize_events(events: List[Dict[Any, Any]]) -> List[Dict[Any, Any]]:
    """
    Groups events primarily by session_id (if present) or source_ip.
    Implements a configurable timeout window.
    Returns a list of session dictionaries.
    """
    if not events:
        return []
        
    timeout_seconds = int(os.environ.get("SESSION_TIMEOUT_SECONDS", "300"))
    timeout = timedelta(seconds=timeout_seconds)
    
    # Sort events by timestamp
    events.sort(key=lambda x: x["timestamp"])
    
    # We will build sessions grouped by a logical key.
    # Key: session_id if exists, otherwise source_ip + source (optional)
    # We'll just use (source_ip) as the primary group if session_id isn't there, 
    # but wait, if it's the same attacker they might hit multiple services from same IP.
    # We want to group by (source_ip) to see cross-service activity!
    # If a specific session_id exists (e.g. cowrie), we can also group by that, 
    # but grouping by source_ip is more holistic for cross-service.
    # Let's use source_ip as the primary grouping key if available.
    # If source_ip is empty, we group by session_id.
    # If both empty, group by source (fallback).
    
    active_sessions = {}
    completed_sessions = []
    
    for event in events:
        ip = event.get("source_ip")
        sid = event.get("session_id")
        
        if ip:
            group_key = f"ip_{ip}"
        elif sid:
            group_key = f"sid_{sid}"
        else:
            group_key = f"src_{event['source']}"
            
        ts = event["timestamp"]
        
        if group_key not in active_sessions:
            active_sessions[group_key] = [event]
        else:
            last_event = active_sessions[group_key][-1]
            last_ts = last_event["timestamp"]
            
            if ts - last_ts <= timeout:
                active_sessions[group_key].append(event)
            else:
                # Timeout exceeded, close session and start new
                completed_sessions.append({
                    "group_key": group_key,
                    "events": active_sessions[group_key]
                })
                active_sessions[group_key] = [event]
                
    for group_key, session_events in active_sessions.items():
        if session_events:
            completed_sessions.append({
                "group_key": group_key,
                "events": session_events
            })
            
    return completed_sessions
