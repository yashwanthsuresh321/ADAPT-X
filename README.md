# ADAPT-X

**AI-Driven Adaptive Cyber Deception and Attack Prediction Framework**

ADAPT-X is a cybersecurity platform designed to detect, understand, predict, and respond to attacker behavior using adaptive cyber deception. The long-term system will transform cyber deception from a static monitoring mechanism into an adaptive AI-assisted defensive mechanism.

## Phase 1.2 — Initial Cyber Lab Infrastructure

This phase establishes the foundational Docker-based cyber lab with isolated networking and distinct target services. It deliberately excludes AI, advanced prediction, and adaptive deception features, providing a clean baseline for telemetry collection in later phases.

### Phase 1.3: Telemetry Collection (Closed)
- Deployed Telemetry Collector (`10.10.10.60`)
- Implemented robust `telemetry_events` PostgreSQL storage
- Ensured idempotency against duplicate logs

### Phase 1.4: Behavioral Feature Engineering (Closed)
- Deployed Feature Engineering service (`10.10.10.70`)
- Transformed raw telemetry into structured JSONB behavior sequences
- Populated `behavioral_features` table

### Phase 1.5: AI/ML Behavioral Baseline (Closed)
- Deployed ML Engine container (`10.10.10.80`)
- Generated synthetic laboratory ground truth in `ml_scenarios`
- Built Scikit-Learn `RandomForestClassifier` pipeline
- Established end-to-end inference stored in `ml_predictions`

### Architecture

The lab consists of five distinct services:
- **Web Server** (10.10.10.10) - A simple FastAPI web service.
- **SSH Server** (10.10.10.20) - An OpenSSH server acting as the real target SSH service with a test user (`testuser`).
- **PostgreSQL Database** (10.10.10.30) - Contains a synthetic organizational database structure.
- **Internal Server** (10.10.10.40) - A simulated internal enterprise API.
- **Cowrie Honeypot** (10.10.10.50) - The deception/honeypot SSH service running the official Cowrie image.

### Network

The network uses an isolated Docker bridge network `adaptx_network` with the subnet `10.10.10.0/24`. All services have static IPs within this subnet and communicate strictly inside the isolated network.

### Requirements

- Docker
- Docker Compose

### Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Start the lab:
   ```bash
   cd cyber-lab
   docker compose up -d
   ```

### Verification

Run the verification script to check that all components are running correctly:
```bash
python scripts/verify_lab.py
```

### Logs

Logs for each service can be inspected using standard Docker commands:
```bash
docker compose -f cyber-lab/docker-compose.yml logs -f <service_name>
```

Cowrie honeypot logs are also persisted to `cyber-lab/honeypot/logs`.

### Security Notes

- **Isolated Lab:** This environment is designed for controlled academic experimentation. It must **not** be exposed to the public internet.
- **Synthetic Data:** The PostgreSQL database contains entirely synthetic data. No real personal or sensitive information is used.
- **No Public Exposure:** The target services and the honeypot are intentionally bound to the internal network only. Do not add host port mappings that would expose them externally.
- **No Real Credentials:** Do not use real organizational credentials for the SSH server or PostgreSQL database.
- **Kali Integration:** A Kali Linux VM will be connected to the isolated network in a later phase to perform controlled attack scenarios. It is not currently required for this phase.

### Current Limitations

- AI models, machine learning, attack prediction, and adaptive deception are **not** implemented in this phase.
- Zeek and Suricata network monitoring are **not** implemented yet.
- The web dashboard is **not** included.
