import datetime
import requests

def log_crm_heartbeat():
    """Logs a CRM heartbeat and optionally checks the GraphQL endpoint."""
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Append log message
    with open(log_file, "a") as f:
        f.write(message + "\n")

    # Optionally check GraphQL endpoint (hello query)
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL hello OK\n")
        else:
            with open(log_file, "a") as f:
                f.write(f"{timestamp} GraphQL hello FAILED ({response.status_code})\n")
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL check error: {e}\n")
