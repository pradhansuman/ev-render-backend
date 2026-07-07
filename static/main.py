import os
import logging
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests
from apscheduler.schedulers.background import BackgroundScheduler

# PRE-LOAD fallback data so the map NEVER shows 0
ev_data_cache = [{"AddressInfo": {"Title": "Tata Power HQ", "AddressLine1": "Bombay House", "StateOrProvince": "Maharashtra", "Latitude": 18.93, "Longitude": 72.83}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 3, "PowerKW": 50}], "DateLastStatusUpdate": "2024-05-20T10:00:00Z"}]def fetch_ev_data():
    global ev_data_cache
    try:
        url = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=IN&maxresults=5000&compact=true&verbose=false"
        api_key = os.environ.get("OCM_API_KEY")
        if api_key:
            url += f"&key={api_key}"
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                ev_data_cache = data
                logging.info(f"SUCCESS: Updated cache with {len(ev_data_cache)} stations.")
    except Exception as e:
        logging.error(f"API Failed: {e}")

# Run in background thread so it NEVER freezes the server
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_ev_data, 'interval', minutes=10)
scheduler.start()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/api/data")
def get_data():
    return ev_data_cache

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")
