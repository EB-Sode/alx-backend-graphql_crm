✅ crm/README.md
# CRM Celery Integration

This guide explains how to set up and run Celery with Celery Beat to generate a **weekly CRM report** using GraphQL data.

---

## 🧩 Prerequisites

Before running the Celery tasks, make sure you have:

- Python 3.9+
- Redis installed and running (as the Celery message broker)
- Django project properly configured with GraphQL endpoint (`/graphql`)

---

## ⚙️ 1. Install Redis and Dependencies

### 🐧 On macOS (using Homebrew)
```bash
brew install redis
brew services start redis

🐧 On Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

✅ Verify Redis is running
redis-cli ping


Expected output:

PONG


Then install Python dependencies (inside your virtual environment):

pip install -r requirements.txt

⚙️ 2. Run Migrations

Make sure your database is up to date:

python manage.py migrate

🚀 3. Start Celery Worker

In one terminal window, run:

celery -A crm worker -l info


This starts the Celery worker process that executes asynchronous tasks.

⏰ 4. Start Celery Beat Scheduler

In another terminal window, run:

celery -A crm beat -l info


Celery Beat schedules the weekly report task automatically.

🧾 5. Verify CRM Report Logs

Each scheduled task generates a CRM report and logs it to:

/tmp/crm_report_log.txt


To view the logs:

cat /tmp/crm_report_log.txt


Expected log format:

2025-10-28 08:00:00 - Report: 120 customers, 452 orders, 98500.75 revenue

