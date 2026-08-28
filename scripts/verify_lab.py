import subprocess
import json
import urllib.request
import urllib.error
import socket
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

def get_container_ip(container_name):
    output = run_cmd(f"docker inspect -f '{{{{range .NetworkSettings.Networks}}}}{{{{.IPAddress}}}}{{{{end}}}}' {container_name}")
    return output if output else None

def test_tcp(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def test_http(ip, port, endpoint):
    url = f"http://{ip}:{port}{endpoint}"
    try:
        response = urllib.request.urlopen(url, timeout=2)
        return response.getcode() == 200
    except urllib.error.URLError:
        return False

def main():
    print("Starting ADAPT-X Lab Verification...\n")
    all_passed = True

    # Check Docker
    if check_docker():
        print("[PASS] Docker")
    else:
        print("[FAIL] Docker - Docker is not available or not running.")
        all_passed = False

    # Check Network
    if check_network():
        print("[PASS] Network")
    else:
        print("[FAIL] Network - adaptx_network is not correctly configured (Expected 10.10.10.0/24)")
        all_passed = False

    # Note: On Windows hosts, the internal Docker IP (10.10.10.X) might not be directly reachable 
    # from the host script depending on Docker Desktop configuration. The most accurate way to verify
    # reachability is from *inside* another container on the same network.
    # Therefore we will launch a temporary tester container on the network.
    
    print("\nRunning connectivity tests from within the lab network...")
    for svc_name, svc_info in SERVICES.items():
        ip = svc_info["ip"]
        port = svc_info["port"]
        
        # We use a temporary alpine container attached to the network to test connections
        if svc_info["type"] == "http":
            cmd = f"docker run --rm --network {NETWORK_NAME} curlimages/curl -s -f --connect-timeout 2 http://{ip}:{port}{svc_info['endpoint']}"
            if run_cmd(cmd) is not None:
                print(f"[PASS] {svc_name.replace('-', ' ').title()}")
            else:
                print(f"[FAIL] {svc_name.replace('-', ' ').title()} - HTTP Check Failed")
                all_passed = False
        else:
            cmd = f"docker run --rm --network {NETWORK_NAME} alpine nc -z -w 2 {ip} {port}"
            if run_cmd(cmd) is not None:
                print(f"[PASS] {svc_name.replace('-', ' ').title()}")
            else:
                print(f"[FAIL] {svc_name.replace('-', ' ').title()} - TCP Check Failed")
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
