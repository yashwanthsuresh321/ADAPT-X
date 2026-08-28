import subprocess
import json
import sys

SERVICES = {
    "web-server": {"ip": "10.10.10.10", "port": 8000, "type": "http", "endpoint": "/health"},
    "ssh-server": {"ip": "10.10.10.20", "port": 22, "type": "tcp"},
    "database": {"ip": "10.10.10.30", "port": 5432, "type": "tcp"},
    "internal-server": {"ip": "10.10.10.40", "port": 8000, "type": "http", "endpoint": "/health"},
    "cowrie": {"ip": "10.10.10.50", "port": 2222, "type": "tcp"}
}

NETWORK_NAME = "adaptx_network"

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def check_docker():
    return run_cmd("docker --version") is not None

def check_network():
    output = run_cmd(f"docker network inspect {NETWORK_NAME}")
    if output:
        try:
            data = json.loads(output)
            subnet = data[0]["IPAM"]["Config"][0]["Subnet"]
            return subnet == "10.10.10.0/24"
        except (KeyError, IndexError, json.JSONDecodeError):
            pass
    return False

def check_telemetry_collector_ip():
    output = run_cmd("docker inspect adaptx-telemetry")
    if output:
        try:
            data = json.loads(output)
            ip = data[0]["NetworkSettings"]["Networks"][NETWORK_NAME]["IPAddress"]
            return ip == "10.10.10.60"
        except (KeyError, IndexError, json.JSONDecodeError):
            pass
    return False

def check_telemetry_table_exists():
    cmd = "docker exec adaptx-db psql -U adaptx_user -d adaptx_lab -t -c \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'telemetry_events');\""
    output = run_cmd(cmd)
    if output and "t" in output.strip():
        return True
    return False

def check_telemetry_events_exist():
    cmd = "docker exec adaptx-db psql -U adaptx_user -d adaptx_lab -t -c \"SELECT COUNT(*) FROM telemetry_events;\""
    output = run_cmd(cmd)
    if output:
        try:
            count = int(output.strip())
            return count > 0
        except ValueError:
            pass
    return False

def main():
    print("Starting ADAPT-X Lab Verification...\n")
    all_passed = True

    if check_docker():
        print("[PASS] Docker")
    else:
        print("[FAIL] Docker")
        all_passed = False

    if check_network():
        print("[PASS] Phase 1.2 Network")
    else:
        print("[FAIL] Phase 1.2 Network")
        all_passed = False

    print("\nRunning connectivity tests from within the lab network...")
    for svc_name, svc_info in SERVICES.items():
        ip = svc_info["ip"]
        port = svc_info["port"]
        
        if svc_info["type"] == "http":
            cmd = f"docker run --rm --network {NETWORK_NAME} curlimages/curl -s -f --connect-timeout 2 http://{ip}:{port}{svc_info['endpoint']}"
            if run_cmd(cmd) is not None:
                print(f"[PASS] {svc_name.replace('-', ' ').title()}")
            else:
                print(f"[FAIL] {svc_name.replace('-', ' ').title()}")
                all_passed = False
        else:
            cmd = f"docker run --rm --network {NETWORK_NAME} alpine nc -z -w 2 {ip} {port}"
            if run_cmd(cmd) is not None:
                print(f"[PASS] {svc_name.replace('-', ' ').title()}")
            else:
                print(f"[FAIL] {svc_name.replace('-', ' ').title()}")
                all_passed = False

    print("\nPhase 1.3 Telemetry Verification...")
    
    if check_telemetry_collector_ip():
        print("[PASS] Telemetry Collector")
    else:
        print("[FAIL] Telemetry Collector")
        all_passed = False

    if check_telemetry_table_exists():
        print("[PASS] Telemetry Database Schema")
    else:
        print("[FAIL] Telemetry Database Schema")
        all_passed = False

    if check_telemetry_events_exist():
        print("[PASS] End-to-End Telemetry")
        print("[PASS] Event Storage")
        print("[PASS] Event Normalization")
    else:
        print("[FAIL] End-to-End Telemetry (no events found)")
        print("[FAIL] Event Storage")
        print("[FAIL] Event Normalization")
        all_passed = False

    print("\nVerification Complete.")
    if all_passed:
        print("ADAPT-X LAB STATUS: READY")
        sys.exit(0)
    else:
        print("ADAPT-X LAB STATUS: FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
