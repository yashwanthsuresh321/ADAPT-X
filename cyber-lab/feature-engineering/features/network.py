from typing import List, Dict, Any

def extract_network_features(events: List[Dict[Any, Any]]) -> Dict[str, Any]:
    if not events:
        return {
            "unique_destinations": 0,
            "unique_destination_ports": 0,
            "unique_protocols": 0,
            "unique_services": 0,
            "service_transition_count": 0,
            "cross_service_activity": False
        }
        
    destinations = set()
    ports = set()
    protocols = set()
    services = set()
    
    service_transitions = 0
    last_service = None
    
    for event in events:
        dest_ip = event.get("destination_ip")
        if dest_ip:
            destinations.add(dest_ip)
            
        port = event.get("destination_port")
        if port:
            ports.add(port)
            
        proto = event.get("protocol")
        if proto:
            protocols.add(proto)
            
        source_service = event.get("source")
        if source_service:
            services.add(source_service)
            if last_service and last_service != source_service:
                service_transitions += 1
            last_service = source_service
            
    return {
        "unique_destinations": len(destinations),
        "unique_destination_ports": len(ports),
        "unique_protocols": len(protocols),
        "unique_services": len(services),
        "service_transition_count": service_transitions,
        "cross_service_activity": len(services) > 1
    }
