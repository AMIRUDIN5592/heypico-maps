from pydantic import BaseModel, Field
from typing import Optional, List

# ----- Chat -----
class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="User prompt")
    model: Optional[str] = Field(None, description="Optional Ollama model name, e.g. 'llama3.2:3b'")

class ChatResponse(BaseModel):
    model: str
    content: str

# ----- Maps: Directions -----
class DirectionsRequest(BaseModel):
    origin: str = Field(..., description="Alamat/koordinat asal (e.g. 'Jakarta')")
    destination: str = Field(..., description="Alamat/koordinat tujuan")
    mode: Optional[str] = Field("driving", description="driving|walking|bicycling|transit")
    model: Optional[str] = Field(None, description="Optional LLM model for summarization")

class DirectionsLeg(BaseModel):
    distance_text: str
    duration_text: str
    start_address: str
    end_address: str

class DirectionsResult(BaseModel):
    overview_polyline: Optional[str] = None
    legs: List[DirectionsLeg] = []
    maps_url: str

# ----- Maps: Places (simple textsearch/nearby) -----
class PlacesRequest(BaseModel):
    query: str = Field(..., description="Kata kunci tempat, contoh: 'coffee near BSD'")
    location: Optional[str] = Field(None, description="lat,lng (opsional)")
    radius: Optional[int] = Field(5000, description="radius meter (opsional)")
    model: Optional[str] = Field(None, description="Optional LLM model for summarization")

class PlaceItem(BaseModel):
    name: str
    address: Optional[str] = None
    place_id: Optional[str] = None

class PlacesResult(BaseModel):
    items: List[PlaceItem]
