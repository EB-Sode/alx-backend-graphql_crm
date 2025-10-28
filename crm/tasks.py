import datetime
import requests
from celery import shared_task

GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"
LOG_FILE = "/tmp/crm_report_log.txt"


@shared_task
def generate_crm_report():
    """Generates a CRM report using GraphQL data and logs it with a timestamp."""
    query = """
    {
        totalCustomers
        totalOrders
        totalRevenue
    }
    """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        response = requests.post(GRAPHQL_ENDPOINT, json={"query": query}, timeout=10)

        if response.status_code == 200:
            data = response.json().get("data", {})
            customers = data.get("totalCustomers", 0)
            orders = data.get("totalOrders", 0)
            revenue = data.get("totalRevenue", 0.0)

            log_message = (
                f"{timestamp} - Report: {customers} customers, "
                f"{orders} orders, {revenue} revenue\n"
            )

        else:
            log_message = f"{timestamp} - ERROR: GraphQL returned {response.status_code}\n"

    except Exception as e:
        log_message = f"{timestamp} - ERROR: {e}\n"

    # Write to log file (append mode)
    with open(LOG_FILE, "a") as f:
        f.write(log_message)

    return "CRM Report logged successfully."
