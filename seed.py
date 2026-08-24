import random
from datetime import datetime, timedelta
from main import SessionLocal, LogRecord

print("Initializing Enterprise Data Seeder...")
db = SessionLocal()

statuses = [200, 200, 200, 200, 200, 200, 200, 200, 401, 403, 500, 503]
messages = {
    200: "GET /api/v1/telemetry - success",
    401: "POST /admin/config - unauthorized access attempt",
    403: "GET /settings/security - forbidden",
    500: "POST /api/payment - internal server database timeout",
    503: "GET /api/v1/users - service unavailable"
}

# This simulates exactly what Gemini outputs so your UI parses it beautifully!
simulated_gemini_response = """A system exception occurred during the request execution, causing the server to return an error status to the client.

Root Cause: The primary database node experienced a connection timeout due to an unexpectedly high volume of concurrent queries, exhausting the available connection pool.

Next Step: Immediately increase the database connection pool size limit and restart the affected worker nodes to flush stale connections."""

logs_to_add = []
print("Generating 1,250 realistic logs...")

for _ in range(1250):
    status = random.choice(statuses)
    is_anomaly = status >= 500 or status in [401, 403]
    
    # Generate a random time within the last 48 hours
    random_minutes = random.randint(1, 2880) 
    log_time = (datetime.now() - timedelta(minutes=random_minutes)).strftime("%Y-%m-%d %H:%M:%S")
    
    log = LogRecord(
        timestamp=log_time,
        ip_address=f"{random.randint(10, 192)}.{random.randint(0, 255)}.1.{random.randint(1, 255)}",
        status=status,
        message=messages[status],
        is_anomaly=is_anomaly,
        ai_explanation=simulated_gemini_response if is_anomaly else None
    )
    logs_to_add.append(log)

db.add_all(logs_to_add)
db.commit()
db.close()

print("✅ Success! 1,250 logs have been injected into log_analyzer.db")