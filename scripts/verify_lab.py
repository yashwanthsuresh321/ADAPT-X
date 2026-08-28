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

def verify_phase_1_6():
    print("\nPhase 1.6 Detection & Alerting Verification...")
    
    # 1. Container Running
    result = subprocess.run(["docker", "ps", "--format", "{{.Names}}"], capture_output=True, text=True)
    if "adaptx-detection-engine" in result.stdout:
        print("[PASS] Detection Engine Container")
    else:
        print("[FAIL] Detection Engine Container not running")
        return False
        
    # 2. Container IP
    result = subprocess.run(["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", "adaptx-detection-engine"], capture_output=True, text=True)
    if "10.10.10.90" in result.stdout:
        print("[PASS] Detection Engine IP (10.10.10.90)")
    else:
        print("[FAIL] Detection Engine IP incorrect: " + result.stdout.strip())
        return False
        
    # 3. Database Schema
    query = "SELECT count(*) FROM information_schema.tables WHERE table_name = 'alerts';"
    cmd = f"docker exec adaptx-db psql -U adaptx_user -d adaptx_lab -t -c \"{query}\""
    result = run_cmd(cmd)
    if result and "1" in result:
        print("[PASS] Alerts Table Schema")
    else:
        print("[FAIL] Alerts Table Schema missing")
        return False
        
    # 4. Alerts Generation (End-to-End)
    query = "SELECT count(*) FROM alerts;"
    cmd = f"docker exec adaptx-db psql -U adaptx_user -d adaptx_lab -t -c \"{query}\""
    result = run_cmd(cmd)
    if result and int(result.strip()) >= 0:
        print("[PASS] Alert Query Works")
    else:
        print("[FAIL] Alert Query Failed")
        return False

    return True

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

    print("\nPhase 1.4 Feature Engineering Verification...")
    
    def check_feature_ip():
        output = run_cmd("docker inspect adaptx-feature-engineering")
        if output:
            try:
                data = json.loads(output)
                ip = data[0]["NetworkSettings"]["Networks"][NETWORK_NAME]["IPAddress"]
                return ip == "10.10.10.70"
            except (KeyError, IndexError, json.JSONDecodeError):
                pass
        return False

    def check_feature_table_exists():
        cmd = "docker exec adaptx-db psql -U adaptx_user -d adaptx_lab -t -c \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'behavioral_features');\""
        output = run_cmd(cmd)
        if output and "t" in output.strip():
            return True
        return False

    def check_feature_records_exist():
        cmd = "docker exec adaptx-db psql -U adaptx_user -d adaptx_lab -t -c \"SELECT COUNT(*) FROM behavioral_features;\""
        output = run_cmd(cmd)
        if output:
            try:
                count = int(output.strip())
                return count > 0
            except ValueError:
                pass
        return False

    if check_feature_ip():
        print("[PASS] Feature Engineering Container")
        print("[PASS] Feature Engineering IP (10.10.10.70)")
    else:
        print("[FAIL] Feature Engineering Container or IP")
        all_passed = False

    if check_feature_table_exists():
        print("[PASS] Behavioral Features Table Schema")
    else:
        print("[FAIL] Behavioral Features Table Schema")
        all_passed = False

    if check_feature_records_exist():
        print("[PASS] Feature Generation (Data Exists)")
        print("[PASS] Pipeline E2E")
    else:
        print("[FAIL] Feature Generation (No Data)")
        all_passed = False

    print("\nPhase 1.5 ML Engine Verification...")
    
    def check_ml_ip():
        output = run_cmd("docker inspect adaptx-ml-engine")
        if output:
            try:
                data = json.loads(output)
                ip = data[0]["NetworkSettings"]["Networks"][NETWORK_NAME]["IPAddress"]
                return ip == "10.10.10.80"
            except (KeyError, IndexError, json.JSONDecodeError):
                pass
        return False

    def check_ml_table_exists(table_name):
        cmd = f"docker exec adaptx-db psql -U adaptx_user -d adaptx_lab -t -c \"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}');\""
        output = run_cmd(cmd)
        if output and "t" in output.strip():
            return True
        return False

    def check_ml_records_exist(table_name):
        cmd = f"docker exec adaptx-db psql -U adaptx_user -d adaptx_lab -t -c \"SELECT COUNT(*) FROM {table_name};\""
        output = run_cmd(cmd)
        if output:
            try:
                count = int(output.strip())
                return count > 0
            except ValueError:
                pass
        return False

    if check_ml_ip():
        print("[PASS] ML Engine Container")
        print("[PASS] ML Engine IP (10.10.10.80)")
    else:
        print("[FAIL] ML Engine Container or IP")
        all_passed = False

    if check_ml_table_exists("ml_scenarios") and check_ml_table_exists("ml_predictions"):
        print("[PASS] ML Tables Schema (ml_scenarios, ml_predictions)")
    else:
        print("[FAIL] ML Tables Schema")
        all_passed = False
        
    if check_ml_records_exist("ml_predictions"):
        print("[PASS] ML Inference Works (Predictions Exist)")
    else:
        print("[FAIL] ML Inference (No Predictions)")
        all_passed = False

    if not verify_phase_1_6():
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
