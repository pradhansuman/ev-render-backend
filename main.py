import os
import requests
import logging
from fastapi import FastAPI
from fastapi.responses import FileResponse
def fetch_ev_data():
    global ev_data_cache
    logging.info("Attempting to fetch live data with API Key...")
    try:
        # Base URL for India, asking for 5,000 results
        url = "https://api.openchargemap.io/v3/poi/?output=json&countrycode=IN&maxresults=5000&compact=true&verbose=false"
        
        # Securely grab the key from Render's Environment Variables
        api_key = os.environ.get("OCM_API_KEY")
        
        if api_key:
            url += f"&key={api_key}"
            logging.info("API Key detected. Requesting premium data limit...")
        else:
            logging.warning("No API Key found in environment. Using public limits.")

        # 30 second timeout since we are asking for more data
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                ev_data_cache = data
                logging.info(f"SUCCESS: Cached {len(ev_data_cache)} live stations.")
                return 
            
        logging.warning("API returned invalid or empty data. Using fallback.")
    except Exception as e:
        logging.error(f"API Request Failed ({e}). Using fallback.")
    
    # FALLBACK TRIGGER
    ev_data_cache = fallback_data
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
