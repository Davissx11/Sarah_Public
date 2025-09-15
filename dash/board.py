#! /usr/bin/env python

import os
from pprint import pp

import httpx
import uvicorn
from fastapi import FastAPI

app = FastAPI()


OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_API_BASE_URL = "http://api.weatherapi.com/v1/current.json"

OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
assert len(OPENWEATHER_API_KEY) == 32
WEATHER_API_KEY = os.environ["WEATHER_API_KEY"]
assert len(WEATHER_API_KEY) == 31


def open_weather_fetch_forecast(zip_code: str) -> dict[str, float]:
    assert len(zip_code) == 5, zip_code
    params = {
        "zip": zip_code,
        "appid": OPENWEATHER_API_KEY,
        "units": "imperial",  # or 'metric' for Celsius
    }
    response = httpx.get(OPENWEATHER_BASE_URL, params=params)
    response.raise_for_status()
    payload = dict(response.json())
    hourly = list(payload["list"])
    hour_to_temp = {d["dt_txt"]: float(d["main"]["temp"]) for d in hourly}
    return hour_to_temp


def open_meteo_fetch_forecast(zip_code: str, country_code: str) -> dict:  # type: ignore
    params = {
        "postal_code": zip_code,
        "country": country_code,
        "hourly": "temperature_2m",  # Request hourly temperature
    }
    response = httpx.get(OPEN_METEO_BASE_URL, params=params)
    print(response.status_code, type(response), 1)
    print(response.text, 2)
    pp(dict(response.headers))
    response.raise_for_status()
    print(response)
    return dict(response.json())


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
    return open_weather_fetch_forecast(zip_code)


if __name__ == "__main__":
    uvicorn.run("dash.board:app", host="127.0.0.1", port=8000, reload=True)
