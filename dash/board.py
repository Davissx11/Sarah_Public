#! /usr/bin/env python

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from dash.open_meteo import open_meteo_fetch_forecast

app = FastAPI()


@app.get("/forecast/{zip_code}")
async def get_forecast(zip_code: str) -> dict[str, float]:
    return dict(open_meteo_fetch_forecast(zip_code))


@app.get("/favicon.ico")
async def favicon() -> FileResponse:
    return FileResponse("dash/asset/weather-app-7477790.ico", media_type="image/x-icon")


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse("/forecast/94025")


if __name__ == "__main__":
    app.mount("/static", StaticFiles(directory="dash/asset"), name="static")
    uvicorn.run("dash.board:app", host="127.0.0.1", port=8000, reload=True)
