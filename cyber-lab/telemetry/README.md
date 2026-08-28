# ADAPT-X Telemetry Collector

The Telemetry Collector is the core of Phase 1.3 in the ADAPT-X project. It transforms raw log output from the cyber lab services (Web, Internal, SSH, Database, Cowrie) into normalized events stored in PostgreSQL.

## Architecture

The telemetry collector runs as a Python daemon inside the `adaptx-telemetry` container. It relies on:
1. **Docker Logs**: `/var/run/docker.sock` is mounted as read-only. The collector uses the Docker Python SDK to stream raw stdout/stderr logs from `adaptx-web`, `adaptx-internal`, `adaptx-ssh`, and `adaptx-db`.
2. **Cowrie Logs**: `./honeypot/logs/` is mounted as read-only. The collector tails `cowrie.json`.

**Security Note**: Docker socket access is privileged and restricted to read-only mode to prevent the collector from modifying the host or spawning new containers. No remote API endpoints are exposed.

## Pipeline
1. **Collector**: Listens to sources asynchronously.
2. **Parsers**: Specific logic in `collector/*.py` applies regex or JSON parsing to transform raw strings into `TelemetryEvent` objects.
3. **Normalizer**: Uses Pydantic (`normalization.schema`) to guarantee fields like `timestamp` (UTC), `source_ip`, `event_type`, etc.
4. **Storage**: Uses `storage.postgres` to insert into `telemetry_events`. Deduplication relies on generating a deterministic UUID from the raw log line (`base.generate_deterministic_uuid`).

## Schema

See `cyber-lab/database/init/02-telemetry.sql`.

## Testing

Run unit tests directly inside the container:
```bash
docker exec adaptx-telemetry pytest tests/
```
