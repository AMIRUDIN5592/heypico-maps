from fastapi import APIRouter, Depends, HTTPException
import logging
from urllib.parse import quote_plus
from typing import List, Dict, Any
import httpx
from config import get_settings
from models.schemas import ChatRequest, ChatResponse
from services.ollama_service import generate_with_ollama
from services.maps_service import directions as maps_directions, text_search_places as maps_places, build_gmaps_directions_url, normalize_mode
from models.schemas import DirectionsRequest, PlacesRequest
from deps import get_rate_limiter

router = APIRouter(tags=["chat"])

@router.get("/models")
async def list_models() -> List[Dict[str, Any]]:
    """Return available local Ollama models (tags)."""
    settings = get_settings()
    url = f"{settings.OLLAMA_BASE_URL}/api/tags"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json() or {}
        # Ollama returns {"models": [{"name": "llama3.2:3b", ...}, ...]}
        return data.get("models", [])

@router.post("", response_model=ChatResponse, dependencies=[Depends(get_rate_limiter)])
async def chat(req: ChatRequest):
    try:
        content = await generate_with_ollama(req.prompt, model=req.model)
        return ChatResponse(model=req.model or "ollama", content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {e}")

@router.post("/directions", response_model=ChatResponse, dependencies=[Depends(get_rate_limiter)])
async def chat_directions(req: DirectionsRequest):
    try:
        settings = get_settings()
        safe_mode = normalize_mode(req.mode or "driving")
        
        # STEP 1: Always try to get maps data first (this is fast and reliable)
        poly_legs = await maps_directions(req.origin, req.destination, safe_mode)
        url = build_gmaps_directions_url(req.origin, req.destination, safe_mode)
        
        # HTML view link (embed) for quick open in browser
        view_link_path = (
            f"/maps/directions/view?origin={quote_plus(req.origin)}&destination={quote_plus(req.destination)}&mode={quote_plus(safe_mode)}"
        )
        view_link = settings.API_BASE_URL.rstrip('/') + view_link_path
        
        # If no route found, return immediately with Google Maps link
        if not poly_legs:
            summary = (
                "🗺️ Route not found via Google Maps API.\n\n"
                "📍 Namun Anda masih bisa cek rute manual di:\n"
                f"- Google Maps: {url}\n"
                f"- View on Map (embed): {view_link}\n\n"
                "💡 Tips: Check location spelling or use more specific names."
            )
            return ChatResponse(model="maps+fallback", content=summary)
        poly, legs = poly_legs
        # Buat prompt singkat untuk LLM berdasarkan legs
        steps = "\n".join([f"- {leg.start_address} → {leg.end_address} ({leg.distance_text}, {leg.duration_text})" for leg in legs])
        prompt = (
            "Ringkas rute ini dalam 3-4 kalimat singkat:\n"
            f"{steps}\n"
            "Answer in English."
        )
        # Calculate basic route info first (guaranteed to work)
        try:
            total_distance = sum([float(leg.distance_text.replace(' km', '').replace(',', '.')) for leg in legs if 'km' in leg.distance_text])
        except:
            total_distance = 0
            
        # Calculate total duration by parsing and summing all legs
        def parse_duration(duration_text):
            """Parse duration text like '2 hours 46 mins' or '1 hour 15 mins' to total minutes"""
            import re
            # Remove any extra characters and normalize
            text = duration_text.lower().replace('hours', 'hour').replace('mins', 'min').replace('minutes', 'min')
            
            # Extract hours and minutes
            hours = 0
            minutes = 0
            
            # Look for hour patterns
            hour_match = re.search(r'(\d+)\s*hours?', text)
            if hour_match:
                hours = int(hour_match.group(1))
            
            # Look for minute patterns
            min_match = re.search(r'(\d+)\s*mins?', text)
            if min_match:
                minutes = int(min_match.group(1))
            
            return hours * 60 + minutes
        
        def format_duration(total_minutes):
            """Format total minutes back to readable format"""
            if total_minutes < 60:
                return f"{total_minutes} min"
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if minutes == 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} min"
        
        # Sum all leg durations
        total_minutes = 0
        try:
            for leg in legs:
                total_minutes += parse_duration(leg.duration_text)
            total_duration = format_duration(total_minutes)
        except:
            total_duration = legs[0].duration_text if legs else "Unknown"
        
        # Transportation mode icons and labels
        mode_info = {
            'driving': {'icon': '🚗', 'label': 'driving'},
            'walking': {'icon': '🚶', 'label': 'walking'},
            'bicycling': {'icon': '🚴', 'label': 'bicycling'},
            'transit': {'icon': '🚌', 'label': 'public transit'}
        }
        mode_data = mode_info.get(safe_mode, {'icon': '🚗', 'label': safe_mode})
        
        # Create reliable base content with route data
        base_content = (
            f"🗺️ **Route Found: {req.origin} → {req.destination}**\n\n"
            f"📏 **Distance**: ~{total_distance:.1f} km\n"
            f"⏱️ **Estimated time**: {total_duration}\n"
            f"{mode_data['icon']} **Transportation mode**: {mode_data['label']}\n\n"
            f"**Route Details:**\n{steps}\n\n"
            "✅ **Route found successfully** - see details on Google Maps or embed map."
        )
        
        # Try LLM enhancement but don't block if it fails
        try:
            # Much shorter prompt for faster processing
            simple_prompt = f"Summary: route from {req.origin} to {req.destination}, {total_distance:.1f}km. 1-2 sentences only. English."
            llm_content = await generate_with_ollama(simple_prompt, model=req.model, max_retries=0)
            if llm_content and len(llm_content.strip()) > 5:
                content = f"🤖 **AI Summary**: {llm_content}\n\n{base_content}"
            else:
                content = base_content
        except Exception as le:
            logging.info(f"LLM enhancement failed, using base content: {le}")
            content = base_content
        content_with_links = (
            content
            + "\n\nQuick Links:\n"
            + f"- [Google Maps]({url})\n"
            + f"- [View on Map (embed)]({view_link})\n"
            + "\nRaw links (fallback):\n"
            + url + "\n" + view_link
        )
        return ChatResponse(model="maps+llm", content=content_with_links)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat directions error: {e}")

@router.post("/places", response_model=ChatResponse, dependencies=[Depends(get_rate_limiter)])
async def chat_places(req: PlacesRequest):
    try:
        settings = get_settings()
        
        # STEP 1: Always try to get places data first (this is fast and reliable)
        items = await maps_places(req.query, req.location, req.radius)
        
        # Build view link (include optional center if provided)
        view_link = settings.API_BASE_URL.rstrip("/") + f"/maps/places/view?q={quote_plus(req.query)}"
        if req.location:
            view_link += f"&location={quote_plus(req.location)}"
            
        # If no places found, return immediately with search link
        if not items:
            return ChatResponse(
                model="maps+fallback",
                content=(
                    f"🔍 No places found for '{req.query}'.\n\n"
                    "📍 Try looking on the map or change keywords:\n"
                    f"[Lihat di peta (embed)]({view_link})\n\n"
                    "💡 Tips: Gunakan kata kunci yang lebih umum atau ubah lokasi pencarian.\n\n"
                    f"Raw link: {view_link}"
                ),
            )
        # Create reliable base content with places data (guaranteed to show results)
        top_places = items[:5]  # Show top 5 places
        listing = "\n".join([f"• **{it.name}** {f'— {it.address}' if it.address else ''}" for it in top_places])
        
        base_content = (
            f"🔍 **Search '{req.query}' - {len(items)} places found!**\n\n"
            f"📍 **Top {len(top_places)} Recommendations:**\n{listing}\n\n"
            f"✅ **Results available** - view all on embed map."
        )
        
        # Try LLM enhancement but don't block if it fails
        try:
            # Much shorter prompt for faster processing
            top_names = [it.name for it in items[:3]]
            simple_prompt = f"From: {', '.join(top_names)}. Choose 2 best, brief reason. English, 1-2 sentences."
            llm_content = await generate_with_ollama(simple_prompt, model=req.model, max_retries=0)
            if llm_content and len(llm_content.strip()) > 5:
                content = f"🤖 **AI Recommendations**: {llm_content}\n\n{base_content}"
            else:
                content = base_content
        except Exception as le:
            logging.info(f"LLM enhancement failed, using base content: {le}")
            content = base_content
        content_with_links = (
            content
            + "\n\n[View on Map (embed)](" + view_link + ")"
            + "\nRaw link: " + view_link
        )
        return ChatResponse(model="maps+llm", content=content_with_links)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat places error: {e}")
