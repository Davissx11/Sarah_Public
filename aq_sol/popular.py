import datetime as dt
from datetime import timedelta
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


def popular(chem: str) -> bool:

    assert get_pageviews(chem) > 0

    p = get_page(chem)
    assert p

    return True
