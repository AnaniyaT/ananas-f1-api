from fastapi import FastAPI

from pathlib import Path
import sys 
sys.path.append(str(Path(__file__).parent))

import json
import uvicorn
from scraper.Scraper import Scraper
import os
from dotenv import load_dotenv

from db import Database
from utils import Utils

load_dotenv()
dbPath = os.getenv("DB_PATH")
port = os.getenv("PORT")

print("Database path", dbPath)
print("PORT", port)

if not port:
    port = 3000

app = FastAPI() 
db = Database(path=dbPath)
scraper = Scraper(dbPath=dbPath)

db.initialize()

@app.get("/")
async def root():
    return { "message": "Hello there mate!" }

@app.get("/races")
async def getRaces():
    races = db.races.getAll()
    
    return races

@app.post("/scrape/races")
async def scrapeRaces(year: int = 2024, round: int = None):
    if not round:
        await scraper.saveAllRaces(year)
    else:
        await scraper.saveRace(year, round)
        
    return f"Scraped {'round ' + str(round) if round else 'all races'} of season {year} successfully"

if __name__ == "__main__":
    print("Running on port:", port)
    uvicorn.run("main:app", host="0.0.0.0", port=int(port))
