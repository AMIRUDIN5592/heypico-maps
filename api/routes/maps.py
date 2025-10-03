from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from urllib.parse import quote_plus
from models.schemas import (DirectionsRequest, DirectionsResult, PlacesRequest, PlacesResult)
from services.maps_service import directions, text_search_places, build_gmaps_directions_url, normalize_mode
from deps import get_rate_limiter
from config import get_settings
router = APIRouter(tags=["maps"])

@router.post("/directions", response_model=DirectionsResult, dependencies=[Depends(get_rate_limiter)])
async def get_directions(req: DirectionsRequest):
    try:
        poly_legs = await directions(req.origin, req.destination, req.mode)
        url = build_gmaps_directions_url(req.origin, req.destination, req.mode)
        if not poly_legs:
            # fallback: no route found – still return url so user can open Maps
            return DirectionsResult(overview_polyline=None, legs=[], maps_url=url)
        poly, legs = poly_legs
        return DirectionsResult(overview_polyline=poly, legs=legs, maps_url=url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Directions error: {e}")

@router.post("/places", response_model=PlacesResult, dependencies=[Depends(get_rate_limiter)])
async def search_places(req: PlacesRequest):
    try:
        items = await text_search_places(req.query, req.location, req.radius)
        return PlacesResult(items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Places error: {e}")

@router.get("/directions/view", response_class=HTMLResponse, dependencies=[Depends(get_rate_limiter)])
async def directions_view(
    origin: str = Query(..., description="Origin address or coordinates"),
    destination: str = Query(..., description="Destination address or coordinates"),
    mode: str = Query("driving", description="driving|walking|bicycling|transit"),
    zoom: int = Query(10, ge=3, le=20),  # Lower default zoom for better route overview
    avoid: str | None = Query(
        None,
        description="Optional avoid settings for driving only: 'tolls', 'highways', or 'ferries'"
    ),
):
    """Tampilkan peta rute dalam iframe (Google Maps Embed API)."""
    settings = get_settings()
    if not settings.GOOGLE_MAPS_API_KEY:
        return HTMLResponse(
            content="""
            <html><body>
              <p>GOOGLE_MAPS_API_KEY belum di-set. Tambahkan ke .env untuk menampilkan peta ter-embed.</p>
            </body></html>
            """,
            status_code=200,
        )
    mode = normalize_mode(mode)
    # Enhanced parameters for better auto-focus (directions-specific)
    params = {
        "key": settings.GOOGLE_MAPS_API_KEY,
        "origin": origin,
        "destination": destination,
        "mode": mode,
        "zoom": str(zoom),
        "region": "ID",  # Indonesia region for better local results
        "language": "en",  # English language
        "units": "metric"  # Use metric units (supported in directions)
    }

    # Respect optional avoid preference (do not set by default to allow toll roads)
    if mode == "driving" and avoid:
        params["avoid"] = avoid

    # Build URL with proper encoding
    src_params = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items() if v])
    src = f"https://www.google.com/maps/embed/v1/directions?{src_params}"
    return HTMLResponse(
        content=f"""
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Route: {origin} → {destination}</title>
        </head>
        <body style="margin:0;padding:0;background:#000;">
          <iframe width="100%" height="100%" 
                  style="border:0; position:fixed; inset:0; background:#000;"
                  loading="eager" 
                  allowfullscreen
                  referrerpolicy="no-referrer-when-downgrade"
                  src="{src}"></iframe>
          <script>
            window.addEventListener('load', function() {{
              if (window.parent !== window) {{
                window.parent.postMessage({{
                  type: 'directions-loaded',
                  origin: '{origin}',
                  destination: '{destination}',
                  mode: '{mode}'
                }}, '*');
              }}
            }});
          </script>
        </body>
        </html>
        """,
        status_code=200,
    )

@router.get("/places/view", response_class=HTMLResponse, dependencies=[Depends(get_rate_limiter)])
async def places_view(
    q: str = Query(..., description="Kata kunci pencarian"),
    location: str | None = Query(None, description="lat,lng (opsional untuk pusat peta)"),
    zoom: int = Query(14, ge=3, le=20),  # Higher zoom for places to show more detail
):
    """Display place search results in iframe (Google Maps Embed API)."""
    settings = get_settings()
    if not settings.GOOGLE_MAPS_API_KEY:
        return HTMLResponse(
            content="""
            <html><body>
              <p>GOOGLE_MAPS_API_KEY belum di-set. Tambahkan ke .env untuk menampilkan peta ter-embed.</p>
            </body></html>
            """,
            status_code=200,
        )
    # Enhanced parameters for better search focus (places-specific)
    params = {
        "key": settings.GOOGLE_MAPS_API_KEY,
        "q": q,
        "zoom": str(zoom),
        "region": "ID",  # Indonesia region
        "language": "en"  # English language  
        # Note: 'units' parameter not supported in search API
    }
    
    # Add center if provided for more precise search
    if location:
        params["center"] = location
    
    # Build URL with proper encoding
    src_params = "&".join([f"{k}={quote_plus(str(v))}" for k, v in params.items()])
    src = f"https://www.google.com/maps/embed/v1/search?{src_params}"
    return HTMLResponse(
        content=f"""
        <html>
        <head>
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Places: {q}</title>
        </head>
        <body style="margin:0;padding:0;background:#000;">
          <iframe width="100%" height="100%" 
                  style="border:0; position:fixed; inset:0; background:#000;"
                  loading="eager" 
                  allowfullscreen
                  referrerpolicy="no-referrer-when-downgrade"
                  src="{src}"></iframe>
          <script>
            window.addEventListener('load', function() {{
              if (window.parent !== window) {{
                window.parent.postMessage({{
                  type: 'places-loaded',
                  query: '{q}',
                  location: '{location or ""}'
                }}, '*');
              }}
            }});
          </script>
        </body>
        </html>
        """,
        status_code=200,
    )
