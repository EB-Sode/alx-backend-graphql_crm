#!/usr/bin/env python3
import datetime
import logging
# import requests
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(message)s")

# Define GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=False,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date range (orders within last 7 days)
today = datetime.date.today()
seven_days_ago = today - datetime.timedelta(days=7)

# GraphQL query for pending orders
query = gql(
    """
    query GetRecentOrders($startDate: Date!, $endDate: Date!) {
      orders(filter: {orderDate_Gte: $startDate, orderDate_Lte: $endDate, status: "PENDING"}) {
        id
        customer {
          email
        }
        orderDate
      }
    }
    """
)

# Execute query
params = {"startDate": str(seven_days_ago), "endDate": str(today)}
try:
    result = client.execute(query, variable_values=params)
    orders = result.get("orders", [])
    for order in orders:
        order_id = order["id"]
        email = order["customer"]["email"]
        logging.info(f"Order ID: {order_id}, Customer Email: {email}")
except Exception as e:
    logging.error(f"Error fetching orders: {e}")

print("Order reminders processed!")
