from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import logging

app = FastAPI(title="India EV API Proxy")
app.mount("/static", StaticFiles(directory="static"), name="static")

ev_data_cache = []

# REAL INDIAN FALLBACK DATA
fallback_data = [
    {"AddressInfo": {"Title": "Tata Power HQ Station", "AddressLine1": "Bombay House, Fort", "StateOrProvince": "Maharashtra"}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 3, "PowerKW": 50}, {"LevelID": 2, "PowerKW": 15}], "DateLastStatusUpdate": "2024-05-20T10:00:00Z"},
    {"AddressInfo": {"Title": "Zeon Charging Hub Surat", "AddressLine1": "NH48 Highway", "StateOrProvince": "Gujarat"}, "OperatorInfo": {"Title": "Zeon Charging"}, "Connections": [{"LevelID": 3, "PowerKW": 60}, {"LevelID": 3, "PowerKW": 60}], "DateLastStatusUpdate": "2024-05-19T14:30:00Z"},
    {"AddressInfo": {"Title": "ChargeZone Whitefield", "AddressLine1": "ITPL Main Road", "StateOrProvince": "Karnataka"}, "OperatorInfo": {"Title": "ChargeZone"}, "Connections": [{"LevelID": 3, "PowerKW": 30}, {"LevelID": 2, "PowerKW": 7}], "DateLastStatusUpdate": "2024-05-18T09:15:00Z"},
    {"AddressInfo": {"Title": "Statiq Connaught Place", "AddressLine1": "Inner Circle", "StateOrProvince": "Delhi"}, "OperatorInfo": {"Title": "Statiq"}, "Connections": [{"LevelID": 3, "PowerKW": 50}, {"LevelID": 2, "PowerKW": 15}], "DateLastStatusUpdate": "2024-05-20T08:00:00Z"},
    {"AddressInfo": {"Title": "KSEB Trivandrum Fast Charger", "AddressLine1": "Vazhuthacaud", "StateOrProvince": "Kerala"}, "OperatorInfo": {"Title": "KSEB"}, "Connections": [{"LevelID": 3, "PowerKW": 50}], "DateLastStatusUpdate": "2024-05-17T16:45:00Z"},
    {"AddressInfo": {"Title": "Tata Power Phoenix Mall", "AddressLine1": "Viman Nagar", "StateOrProvince": "Maharashtra"}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 2, "PowerKW": 15}, {"LevelID": 2, "PowerKW": 15}], "DateLastStatusUpdate": "2024-05-20T11:20:00Z"},
    {"AddressInfo": {"Title": "Zeon Gachibowli", "AddressLine1": "Cyber Towers", "StateOrProvince": "Telangana"}, "OperatorInfo": {"Title": "Zeon Charging"}, "Connections": [{"LevelID": 3, "PowerKW": 120}, {"LevelID": 3, "PowerKW": 60}], "DateLastStatusUpdate": "2024-05-19T12:00:00Z"},
    {"AddressInfo": {"Title": "ChargeZone OMR Padur", "AddressLine1": "Old Mahabalipuram Rd", "StateOrProvince": "Tamil Nadu"}, "OperatorInfo": {"Title": "ChargeZone"}, "Connections": [{"LevelID": 3, "PowerKW": 50}, {"LevelID": 2, "PowerKW": 7}], "DateLastStatusUpdate": "2024-05-18T15:30:00Z"},
    {"AddressInfo": {"Title": "Statiq Jaipur Pink Square", "AddressLine1": "Tonk Road", "StateOrProvince": "Rajasthan"}, "OperatorInfo": {"Title": "Statiq"}, "Connections": [{"LevelID": 3, "PowerKW": 30}, {"LevelID": 2, "PowerKW": 7}], "DateLastStatusUpdate": "2024-05-20T09:45:00Z"},
    {"AddressInfo": {"Title": "Tata Power Agra Expressway", "AddressLine1": "Yamuna Expressway", "StateOrProvince": "Uttar Pradesh"}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 3, "PowerKW": 120}, {"LevelID": 3, "PowerKW": 120}], "DateLastStatusUpdate": "2024-05-19T07:00:00Z"},
    {"AddressInfo": {"Title": "EVRE Bhubaneswar", "AddressLine1": "Saheed Nagar", "StateOrProvince": "Odisha"}, "OperatorInfo": {"Title": "EVRE"}, "Connections": [{"LevelID": 2, "PowerKW": 15}], "DateLastStatusUpdate": "2024-05-16T10:00:00Z"},
    {"AddressInfo": {"Title": "Tata Power Lucknow", "AddressLine1": "Hazratganj", "StateOrProvince": "Uttar Pradesh"}, "OperatorInfo": {"Title": "Tata Power"}, "Connections": [{"LevelID": 3, "PowerKW": 50}, {"LevelID": 3, "PowerKW": 50}], "DateLastStatusUpdate": "2024-05-20T12:00:00Z"}
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
