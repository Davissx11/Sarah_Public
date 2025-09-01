import datetime as dt
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from wikipedia import get_page

CONTACT_URL = "https://sector6.net/jhanley741/wiki-contact.html"


def _ymd(d: dt.datetime) -> str:
    return d.strftime("%Y%m%d")


def get_pageviews(title: str, days: int = 30) -> int:
    headers = {
        "accept": "application/json",
        "user-agent": CONTACT_URL,
    }
    tz = ZoneInfo("America/Los_Angeles")
    end_date = dt.datetime.now(tz=tz)
    start_date = end_date - timedelta(days=days)
    base_url = (
        "https://wikimedia.org/api/rest_v1/metrics/"
        "pageviews/per-article/en.wikipedia.org/all-access/user"
    )
    url = f"{base_url}/{title}/daily/{_ymd(start_date)}/{_ymd(end_date)}"
    # e.g. .../Potassium_chloride/daily/20250801/20250831

    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    d = resp.json()
    items = d["items"]
    return sum(item["views"] for item in items)


def popular(chem: str) -> int:

    pg = get_page(chem)
    assert " " in f"{pg.title}"
    title = Path(pg.url).name
    assert title == chem

    return get_pageviews(chem)
