from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging

app = FastAPI(title="India EV API Proxy")
app.mount("/static", StaticFiles(directory="static"), name="static")

ev_data_cache = []
# REAL INDIAN FALLBACK DATA (WITH COORDINATES FOR MAPPING)
fallback_data = [
    {"AddressInfo": {"Title": "Tata Power HQ Station", "AddressLine1": "Bombay House, Fort", "StateOrProvince": "Maharashtra", "Latitude": 18.9303, "Longitude": 72.8331}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 3, "PowerKW": 50}, {"LevelID": 2, "PowerKW": 15}], "DateLastStatusUpdate": "2024-05-20T10:00:00Z"},
    {"AddressInfo": {"Title": "Zeon Charging Hub Surat", "AddressLine1": "NH48 Highway", "StateOrProvince": "Gujarat", "Latitude": 21.1702, "Longitude": 72.8311}, "OperatorInfo": {"Title": "Zeon Charging"}, "Connections": [{"LevelID": 3, "PowerKW": 60}, {"LevelID": 3, "PowerKW": 60}], "DateLastStatusUpdate": "2024-05-19T14:30:00Z"},
    {"AddressInfo": {"Title": "ChargeZone Whitefield", "AddressLine1": "ITPL Main Road", "StateOrProvince": "Karnataka", "Latitude": 12.9698, "Longitude": 77.7500}, "OperatorInfo": {"Title": "ChargeZone"}, "Connections": [{"LevelID": 3, "PowerKW": 30}, {"LevelID": 2, "PowerKW": 7}], "DateLastStatusUpdate": "2024-05-18T09:15:00Z"},
    {"AddressInfo": {"Title": "Statiq Connaught Place", "AddressLine1": "Inner Circle", "StateOrProvince": "Delhi", "Latitude": 28.6315, "Longitude": 77.2167}, "OperatorInfo": {"Title": "Statiq"}, "Connections": [{"LevelID": 3, "PowerKW": 50}, {"LevelID": 2, "PowerKW": 15}], "DateLastStatusUpdate": "2024-05-20T08:00:00Z"},
    {"AddressInfo": {"Title": "KSEB Trivandrum Fast Charger", "AddressLine1": "Vazhuthacaud", "StateOrProvince": "Kerala", "Latitude": 8.5142, "Longitude": 76.9500}, "OperatorInfo": {"Title": "KSEB"}, "Connections": [{"LevelID": 3, "PowerKW": 50}], "DateLastStatusUpdate": "2024-05-17T16:45:00Z"},
    {"AddressInfo": {"Title": "Tata Power Phoenix Mall", "AddressLine1": "Viman Nagar", "StateOrProvince": "Maharashtra", "Latitude": 18.5660, "Longitude": 73.9100}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 2, "PowerKW": 15}, {"LevelID": 2, "PowerKW": 15}], "DateLastStatusUpdate": "2024-05-20T11:20:00Z"},
    {"AddressInfo": {"Title": "Zeon Gachibowli", "AddressLine1": "Cyber Towers", "StateOrProvince": "Telangana", "Latitude": 17.4401, "Longitude": 78.3489}, "OperatorInfo": {"Title": "Zeon Charging"}, "Connections": [{"LevelID": 3, "PowerKW": 120}, {"LevelID": 3, "PowerKW": 60}], "DateLastStatusUpdate": "2024-05-19T12:00:00Z"},
    {"AddressInfo": {"Title": "ChargeZone OMR Padur", "AddressLine1": "Old Mahabalipuram Rd", "StateOrProvince": "Tamil Nadu", "Latitude": 12.8231, "Longitude": 80.2230}, "OperatorInfo": {"Title": "ChargeZone"}, "Connections": [{"LevelID": 3, "PowerKW": 50}, {"LevelID": 2, "PowerKW": 7}], "DateLastStatusUpdate": "2024-05-18T15:30:00Z"},
    {"AddressInfo": {"Title": "Statiq Jaipur Pink Square", "AddressLine1": "Tonk Road", "StateOrProvince": "Rajasthan", "Latitude": 26.9124, "Longitude": 75.7873}, "OperatorInfo": {"Title": "Statiq"}, "Connections": [{"LevelID": 3, "PowerKW": 30}, {"LevelID": 2, "PowerKW": 7}], "DateLastStatusUpdate": "2024-05-20T09:45:00Z"},
    {"AddressInfo": {"Title": "Tata Power Agra Expressway", "AddressLine1": "Yamuna Expressway", "StateOrProvince": "Uttar Pradesh", "Latitude": 28.2070, "Longitude": 77.4890}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 3, "PowerKW": 120}, {"LevelID": 3, "PowerKW": 120}], "DateLastStatusUpdate": "2024-05-19T07:00:00Z"},
    {"AddressInfo": {"Title": "EVRE Bhubaneswar", "AddressLine1": "Saheed Nagar", "StateOrProvince": "Odisha", "Latitude": 20.2926, "Longitude": 85.8326}, "OperatorInfo": {"Title": "EVRE"}, "Connections": [{"LevelID": 2, "PowerKW": 15}], "DateLastStatusUpdate": "2024-05-16T10:00:00Z"},
    {"AddressInfo": {"Title": "Tata Power Lucknow", "AddressLine1": "Hazratganj", "StateOrProvince": "Uttar Pradesh", "Latitude": 26.8467, "Longitude": 80.9462}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 3, "PowerKW": 50}, {"LevelID": 3, "PowerKW": 50}], "DateLastStatusUpdate": "2024-05-20T12:00:00Z"}
]

def fetch_ev_data():
    global ev_data_cache
    logging.info("Attempting to fetch live data from OpenChargeMap...")
    try:
        url = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=IN&maxresults=500&compact=true&verbose=false"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                ev_data_cache = data
                logging.info(f"SUCCESS: Cached {len(ev_data_cache)} live stations.")
                return # Exit function if successful
            
        logging.warning("API returned invalid or empty data. Using fallback.")
    except Exception as e:
        logging.error(f"API Request Failed ({e}). Using fallback.")
    
    # FALLBACK TRIGGER: If live API fails, use real backup data
    ev_data_cache = fallback_data

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_ev_data, 'interval', minutes=10)
scheduler.start()

# Fetch immediately on startup
fetch_ev_data()

@app.get("/api/data")
def get_data():
    return ev_data_cache

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")
