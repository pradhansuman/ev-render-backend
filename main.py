from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging

app = FastAPI(title="India EV API Proxy")
app.mount("/static", StaticFiles(directory="static"), name="static")

ev_data_cache = []

def fetch_ev_data():
    logging.info("Fetching fresh EV data from OpenChargeMap...")
    try:
        url = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=IN&maxresults=1000&compact=true&verbose=false"
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            global ev_data_cache
            ev_data_cache = response.json()
            logging.info(f"Successfully cached {len(ev_data_cache)} stations.")
    except Exception as e:
        logging.error(f"Failed to fetch data - {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_ev_data, 'interval', minutes=5)
scheduler.start()
fetch_ev_data()

@app.get("/api/data")
def get_data():
    return ev_data_cache

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")
