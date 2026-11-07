import os, time, httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

KEY = os.getenv("FOOTBALL_API_KEY", "")
BASE = "https://api.football-data.org/v4"
app = FastAPI()
cache = {}

async def get(path, params=None, ttl=300):
    k = (path, tuple(sorted((params or {}).items())))
    now = time.time()
    if k in cache and now - cache[k][0] < ttl:
        return cache[k][1]
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get(BASE + path, params=params, headers={"X-Auth-Token": KEY})
    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text)
    cache[k] = (now, r.json())
    return cache[k][1]

@app.get("/api/live")
async def live():
    return await get("/matches", {"status": "IN_PLAY,PAUSED"}, ttl=30)

@app.get("/api/{code}/matches")
async def matches(code: str, status: str = "FINISHED"):
    d = await get(f"/competitions/{code}/matches", {"status": status}, ttl=120)
    m = d["matches"]
    m = m[-30:][::-1] if status == "FINISHED" else m[:30]
    return {"matches": m}

@app.get("/api/{code}/standings")
async def standings(code: str):
    return await get(f"/competitions/{code}/standings")

@app.get("/api/{code}/scorers")
async def scorers(code: str):
    return await get(f"/competitions/{code}/scorers", {"limit": 20})

@app.get("/api/match/{mid}")
async def match(mid: int):
    return await get(f"/matches/{mid}", ttl=30)

@app.get("/")
async def index():
    return FileResponse("static/index.html")

app.mount("/static", StaticFiles(directory="static"), name="static")
