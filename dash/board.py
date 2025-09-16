#! /usr/bin/env python

import os

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()


OPEN_WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1/current.json"

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
# assert len(OPENWEATHER_API_KEY) == 32
# assert len(WEATHER_API_KEY) == 31


def open_weather_fetch_forecast(zip_code: str) -> dict[str, float]:
    assert len(zip_code) == 5, zip_code
    params = {
        "zip": zip_code,
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial",  # or 'metric' for Celsius
    }
    response = httpx.get(OPEN_WEATHER_BASE_URL, params=params)
    response.raise_for_status()
    payload = dict(response.json())
    hourly = list(payload["list"])
    return {d["dt_txt"]: round(d["main"]["temp"], 1) for d in hourly}


def open_meteo_fetch_forecast(zip_code: str, country_code: str = "US") -> dict:  # type: ignore
    assert country_code == "US"
    assert zip_code == "94025", zip_code
    lat, lng = 37.4528, -122.1833

    params = {
        "latitude": f"{lat}",
        "longitude": f"{lng}",
        "hourly": "temperature_2m",
        "timezone": "auto",
    }
    response = httpx.get(OPEN_METEO_BASE_URL, params=params)
    response.raise_for_status()
    payload = response.json()
    hourly_data = payload["hourly"]
    return {
        dt: round(temp, 1)
        for dt, temp in zip(
            hourly_data["time"],
            hourly_data["temperature_2m"],
            strict=False,
        )
    }


def weather_api_fetch_forecast(zip_code: str, country_code: str = "US") -> dict:  # type: ignore
    params = {
        "key": WEATHER_API_KEY,
        "q": f"{zip_code},{country_code}",
        "aqi": "yes",
        "days": "1",  # Number of days to forecast
        "hour": "1",  # Get hourly forecasts
    }
    response = httpx.get(WEATHER_API_BASE_URL, params=params)
    print(response.status_code, type(response), 1)
    print(response.text, 2)
    response.raise_for_status()
    return dict(response.json())


@app.get("/forecast/{zip_code}")
async def get_forecast(zip_code: str) -> dict[str, float]:
    return open_meteo_fetch_forecast(zip_code)


@app.get("/favicon.ico")
async def favicon() -> FileResponse:
    return FileResponse("dash/asset/weather-app-7477790.ico", media_type="image/x-icon")


if __name__ == "__main__":
    app.mount("/static", StaticFiles(directory="dash/asset"), name="static")
    uvicorn.run("dash.board:app", host="127.0.0.1", port=8000, reload=True)
