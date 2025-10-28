import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


def log_crm_heartbeat():
    """Logs a CRM heartbeat and verifies the GraphQL endpoint using gql client."""
    log_file = "/tmp/crm_heartbeat_log.txt"
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    # Append base log
    with open(log_file, "a") as f:
        f.write(message + "\n")

    # Configure GraphQL client transport
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=False,         # Disable SSL verification if using localhost
        retries=3,            # Retry on transient errors
        timeout=5             # 5-second timeout
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    # Define GraphQL query
    query = gql("{ hello }")

    # Try sending query
    try:
        response = client.execute(query)
        hello_value = response.get("hello", "No response")

        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL hello OK: {hello_value}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} GraphQL check error: {e}\n")
