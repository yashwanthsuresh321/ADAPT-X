import os
import time
import threading
import logging
import docker
import json

from storage.postgres import PostgresStorage
from collector.web import WebParser
from collector.ssh import SSHParser
from collector.internal import InternalParser
from collector.database import DatabaseParser
from collector.cowrie import CowrieParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("telemetry-collector")

storage = PostgresStorage()

parsers = {
    "adaptx-web": WebParser(),
    "adaptx-ssh": SSHParser(),
    "adaptx-db": DatabaseParser(),
    "adaptx-internal": InternalParser()
}

def process_docker_stream(container_name: str, parser):
    client = docker.from_env()
    while True:
        try:
            container = client.containers.get(container_name)
            logger.info(f"Starting log stream for {container_name}")
            for log_line in container.logs(stream=True, follow=True, tail=0):
                line_str = log_line.decode('utf-8').strip()
                if not line_str:
                    continue
                try:
                    event = parser.parse(line_str)
                    if event:
                        storage.store_event(event)
                except Exception as e:
                    logger.error(f"Error parsing log from {container_name}: {e}")
        except docker.errors.NotFound:
            logger.warning(f"Container {container_name} not found. Retrying in 10s...")
            time.sleep(10)
        except Exception as e:
            logger.error(f"Stream error on {container_name}: {e}. Retrying in 5s...")
            time.sleep(5)

def process_cowrie_file(file_path: str, parser):
    while not os.path.exists(file_path):
        logger.warning(f"{file_path} not found. Waiting...")
        time.sleep(10)
    
    logger.info(f"Tailing {file_path}")
    with open(file_path, 'r') as f:
        # Seek to the end
        f.seek(0, 2)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            try:
                event = parser.parse(line)
                if event:
                    storage.store_event(event)
            except Exception as e:
                logger.error(f"Error parsing cowrie log: {e}")

if __name__ == "__main__":
    logger.info("Initializing Telemetry Collector...")
    storage.connect()

    threads = []
    
    # Start docker log tailing threads
    for container_name, parser in parsers.items():
        t = threading.Thread(target=process_docker_stream, args=(container_name, parser), daemon=True)
        t.start()
        threads.append(t)
    
    # Start cowrie log tailing thread
    cowrie_log_path = os.environ.get("COWRIE_LOG_PATH", "/cowrie_logs/cowrie.json")
    cowrie_t = threading.Thread(target=process_cowrie_file, args=(cowrie_log_path, CowrieParser()), daemon=True)
    cowrie_t.start()
    threads.append(cowrie_t)

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down telemetry collector...")
        storage.close()
