from typing import List, Dict, Any

def extract_activity_features(events: List[Dict[Any, Any]]) -> Dict[str, Any]:
    if not events:
        return {
            "command_count": 0,
            "unique_command_count": 0,
            "unique_resources": 0
        }
        
    commands = set()
    resources = set()
    command_count = 0
    
    for event in events:
        cmd = event.get("command")
        if cmd:
            commands.add(cmd)
            command_count += 1
            
        res = event.get("resource")
        if res:
            resources.add(res)
            
    return {
        "command_count": command_count,
        "unique_command_count": len(commands),
        "unique_resources": len(resources)
    }
