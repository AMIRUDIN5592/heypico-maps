# Google Maps Embed API Parameters

## Supported Parameters by API Type

### 1. Directions API (`/maps/directions/view`)
**Endpoint**: `https://www.google.com/maps/embed/v1/directions`

✅ **Supported Parameters:**
- `key` - API key (required)
- `origin` - Starting point (required)
- `destination` - End point (required)
- `mode` - Transportation mode (driving, walking, bicycling, transit)
- `zoom` - Map zoom level (1-20)
- `region` - Country code for regional bias (e.g., "ID" for Indonesia)
- `language` - Language code (e.g., "id" for Indonesian)
- `units` - Distance units (metric/imperial)
- `avoid` - Features to avoid (tolls, highways, ferries)

### 2. Search/Places API (`/maps/places/view`)
**Endpoint**: `https://www.google.com/maps/embed/v1/search`

✅ **Supported Parameters:**
- `key` - API key (required)
- `q` - Search query (required)
- `zoom` - Map zoom level (1-20)
- `center` - Center point for search (lat,lng)
- `region` - Country code for regional bias (e.g., "ID")
- `language` - Language code (e.g., "id")

❌ **NOT Supported for Search:**
- ~~`units`~~ - Not supported in search API
- ~~`avoid`~~ - Not applicable for places
- ~~`mode`~~ - Not applicable for places

## Current Implementation

### Directions Parameters:
```python
params = {
    "key": settings.GOOGLE_MAPS_API_KEY,
    "origin": origin,
    "destination": destination,
    "mode": mode,
    "zoom": str(zoom),
    "region": "ID",
    "language": "id",
    "units": "metric"
}
# Add avoid=tolls only for driving mode
if mode == "driving":
    params["avoid"] = "tolls"
```

### Places Parameters:
```python
params = {
    "key": settings.GOOGLE_MAPS_API_KEY,
    "q": q,
    "zoom": str(zoom),
    "region": "ID",
    "language": "id"
    # units parameter removed - not supported
}
if location:
    params["center"] = location
```

## Error Prevention

- All parameters are filtered with `if v` to exclude empty values
- API-specific parameter sets prevent invalid parameter errors
- Proper URL encoding with `quote_plus()`

## References

- [Google Maps Embed API - Directions](https://developers.google.com/maps/documentation/embed/get-started#directions_mode)
- [Google Maps Embed API - Search](https://developers.google.com/maps/documentation/embed/get-started#search_mode)