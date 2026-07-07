import os
import logging
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests
from apscheduler.schedulers.background import BackgroundScheduler

ev_data_cache = [
    {"AddressInfo": {"Title": "Tata Power HQ", "AddressLine1": "Bombay House", "StateOrProvince": "Maharashtra", "Latitude": 18.93, "Longitude": 72.83}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 3, "PowerKW": 50}], "DateLastStatusUpdate": "2024-05-20T10:00:00Z"},
    {"AddressInfo": {"Title": "Zeon Surat", "AddressLine1": "NH48", "StateOrProvince": "Gujarat", "Latitude": 21.17, "Longitude": 72.83}, "OperatorInfo": {"Title": "Zeon Charging"}, "Connections": [{"LevelID": 3, "PowerKW": 60}], "DateLastStatusUpdate": "2024-05-19T14:30:00Z"},
    {"AddressInfo": {"Title": "Statiq Delhi", "AddressLine1": "Connaught Place", "StateOrProvince": "Delhi", "Latitude": 28.63, "Longitude": 77.21}, "OperatorInfo": {"Title": "Statiq"}, "Connections": [{"LevelID": 2, "PowerKW": 15}], "DateLastStatusUpdate": "2024-05-20T08:00:00Z"}
]

def fetch_ev_data():
    global ev_data_cache
    api_key = os.environ.get("OCM_API_KEY")
    if not api_key: return
    try:
        url = f"https://api.openchargemap.io/v3/poi/?output=json&countrycode=IN&maxresults=50&compact=true&verbose=false&key={api_key}"
        response = requests.get(url, timeout=45)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                ev_data_cache = data
    except Exception as e:
        logging.error(f"API Failed: {e}")

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
