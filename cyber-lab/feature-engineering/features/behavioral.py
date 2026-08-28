from typing import List, Dict, Any
from features.temporal import extract_temporal_features
from features.network import extract_network_features
from features.authentication import extract_authentication_features
from features.activity import extract_activity_features
import uuid

def compile_behavioral_features(session_id: str, group_key: str, events: List[Dict[Any, Any]]) -> Dict[str, Any]:
    """
    Orchestrates the compilation of features and behavior_sequence.
    """
    if not events:
        return {}
        
    source_ip = events[0].get("source_ip", "")
    
    # Ordered event sequence for Markov/Transformer models
    behavior_sequence = []
    for event in events:
        # e.g., "ssh_server.connect"
        source = event.get("source", "unknown")
        action = event.get("action", "unknown")
        behavior_sequence.append(f"{source}.{action}")
        
    temp_feats = extract_temporal_features(events)
    net_feats = extract_network_features(events)
    auth_feats = extract_authentication_features(events)
    act_feats = extract_activity_features(events)
    
    # Merge them into feature vector
    feature_vector = {**temp_feats, **net_feats, **auth_feats, **act_feats}
    # Convert datetime objects to string in feature vector for JSON serialization
    feature_vector["window_start"] = feature_vector["window_start"].isoformat()
    feature_vector["window_end"] = feature_vector["window_end"].isoformat()
    
    # Generate deterministic feature_id based on session_id and window_start
    # session_id here might be empty, so we use group_key + window_start
    sid = session_id if session_id else group_key
    unique_string = f"{sid}_{feature_vector['window_start']}"
    feature_id = uuid.uuid5(uuid.NAMESPACE_DNS, unique_string)
    
    return {
        "feature_id": str(feature_id),
        "session_id": sid,
        "source_ip": source_ip,
        "window_start": temp_feats["window_start"],
        "window_end": temp_feats["window_end"],
        "event_count": temp_feats["event_count"],
        "session_duration": temp_feats["session_duration"],
        "events_per_minute": temp_feats["events_per_minute"],
        
        "unique_destinations": net_feats["unique_destinations"],
        "unique_destination_ports": net_feats["unique_destination_ports"],
        "unique_protocols": net_feats["unique_protocols"],
        "unique_services": net_feats["unique_services"],
        "service_transition_count": net_feats["service_transition_count"],
        "cross_service_activity": net_feats["cross_service_activity"],
        
        "authentication_attempts": auth_feats["authentication_attempts"],
        "authentication_failures": auth_feats["authentication_failures"],
        "authentication_successes": auth_feats["authentication_successes"],
        "authentication_failure_rate": auth_feats["authentication_failure_rate"],
        
        "command_count": act_feats["command_count"],
        "unique_command_count": act_feats["unique_command_count"],
        "unique_resources": act_feats["unique_resources"],
        
        "behavior_sequence": behavior_sequence,
        "feature_vector": feature_vector
    }
