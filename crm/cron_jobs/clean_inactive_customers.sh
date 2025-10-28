#!/bin/bash

# Path to your Django project directory (where manage.py is located)
PROJECT_DIR="/Users/richmondsode/Projects/Back_End/alx-backend-python/alx-backend-graphql_crm/alx_backend_graphql"
LOG_FILE="/tmp/customer_cleanup_log.txt"

# Activate the virtual environment
source "$PROJECT_DIR/../../cenv/bin/activate"

# Run the Django shell command to delete inactive customers
COUNT=$(python "$PROJECT_DIR/manage.py" shell -c "
from datetime import date, timedelta
from crm.models import Customer
one_year_ago = date.today() - timedelta(days=365)
deleted, _ = Customer.objects.filter(order__isnull=True, created_at__lt=one_year_ago).delete()
print(deleted)
")

# Log the count with timestamp
echo \"$(date '+%Y-%m-%d %H:%M:%S') - Deleted $COUNT inactive customers\" >> \"$LOG_FILE\"
