import httpx
from typing import List, Optional
from urllib.parse import urlencode, quote_plus
from config import get_settings
from models.schemas import DirectionsLeg, PlaceItem


ALLOWED_MODES = {"driving", "walking", "bicycling", "transit"}

def normalize_mode(mode: Optional[str]) -> str:
    if not mode:
        return "driving"
    m = mode.strip().lower()
    synonyms = {
        "drive": "driving",
        "car": "driving",
        "mobil": "driving",
        "auto": "driving",
        "jalan": "walking",
        "foot": "walking",
        "pejalan": "walking",
        "sepeda": "bicycling",
        "bike": "bicycling",
        "bicycle": "bicycling",
        "cycling": "bicycling",
        "public": "transit",
        "bus": "transit",
        "train": "transit",
        "kereta": "transit",
        "angkutan umum": "transit",
    }
    m = synonyms.get(m, m)
    return m if m in ALLOWED_MODES else "driving"


def build_gmaps_directions_url(origin: str, destination: str, mode: str) -> str:
    # URL share (tanpa API Key) – memudahkan user buka langsung di Google Maps
    base = "https://www.google.com/maps/dir/?api=1"
    mode = normalize_mode(mode)
    q = urlencode({"origin": origin, "destination": destination, "travelmode": mode})
    return f"{base}&{q}"

async def directions(origin: str, destination: str, mode: str):
    """
    Panggil Directions API untuk ambil polyline & ringkasan legs.
    """
    settings = get_settings()
    mode = normalize_mode(mode)
    params = {
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "key": settings.GOOGLE_MAPS_API_KEY,
    }
    url = f"{settings.GOOGLE_MAPS_BASE_URL}/directions/json"

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    routes = data.get("routes", [])
    if not routes:
        return None

    first = routes[0]
    poly = first.get("overview_polyline", {}).get("points")
    legs_raw = first.get("legs", [])

    legs: List[DirectionsLeg] = []
    for leg in legs_raw:
        legs.append(
            DirectionsLeg(
                distance_text=leg["distance"]["text"],
                duration_text=leg["duration"]["text"],
                start_address=leg.get("start_address", ""),
                end_address=leg.get("end_address", "")
            )
        )
    return poly, legs

async def text_search_places(query: str, location: Optional[str], radius: Optional[int]) -> List[PlaceItem]:
    """
    Gunakan Places Text Search. Jika Anda ingin Nearby Search, cukup ganti endpoint.
    """
    settings = get_settings()
    params = {"query": query, "key": settings.GOOGLE_MAPS_API_KEY}
    if location:
        params["location"] = location
    if radius:
        params["radius"] = radius

    url = f"{settings.GOOGLE_MAPS_BASE_URL}/place/textsearch/json"

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    results = data.get("results", [])
    items: List[PlaceItem] = []
    for row in results[:10]:
        items.append(
            PlaceItem(
                name=row.get("name", ""),
                address=row.get("formatted_address"),
                place_id=row.get("place_id"),
            )
        )
    return items
