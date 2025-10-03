import logging
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from config import Settings
from routes.chat import router as chat_router
from routes.maps import router as maps_router

# Configure logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = FastAPI(
    title="HeyPico Maps API",
    description="Maps + LLM Chat API powered by Ollama",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(maps_router, prefix="/maps", tags=["maps"])

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "HeyPico Maps API",
        "version": "1.0.0",
        "docs": "/docs",
        "demo": "/ui"
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/ui", response_class=HTMLResponse)
def demo_ui():
    """Simple demo UI for testing the API"""
    return HTMLResponse(
        content="""
<!DOCTYPE html>
<html>
<head>
    <title>HeyPico Maps Demo</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        .row { display: flex; gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); flex: 1; }
        input, select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; margin: 4px 0; }
        label { display:block; margin-top:8px; font-size: 14px; }
        pre { background: #f8f9fa; padding: 12px; border-radius: 6px; font-size: 13px; line-height: 1.5; max-height: 300px; overflow-y: auto; }
        button { margin-top: 12px; padding: 10px 14px; border: 0; border-radius: 6px; background:#111827; color:white; cursor:pointer; }
        h2, h3 { margin-top: 0; color: #333; }
    </style>
</head>
<body>
    <h2>HeyPico – Maps + Chat Demo</h2>
    <p>Use the form below to try Chat Directions and Chat Places. The response will show a summary with links. The embed map appears on the right.</p>
    <div class="row">
        <div class="card">
            <h3>Chat Directions</h3>
            <label>Origin<input id="dir-origin" placeholder="Jakarta" /></label>
            <label>Destination<input id="dir-dest" placeholder="Bandung" /></label>
            <label>Mode
                <select id="dir-mode">
                    <option value="driving" selected>driving</option>
                    <option value="walking">walking</option>
                    <option value="bicycling">bicycling</option>
                    <option value="transit">transit</option>
                </select>
            </label>
            <button onclick="onDirections()">Send</button>
            <pre id="dir-out"></pre>
        </div>

        <div class="card">
            <h3>Chat Places</h3>
            <label>Query<input id="pl-query" placeholder="coffee near BSD" /></label>
            <label>Location (optional, lat,lng)<input id="pl-loc" placeholder="-6.302,106.653" /></label>
            <label>Radius (m)<input id="pl-rad" type="number" value="5000" /></label>
            <button onclick="onPlaces()">Send</button>
            <pre id="pl-out"></pre>
        </div>
    </div>

    <script>
        const API = location.origin;

        async function onDirections() {
            const origin = document.getElementById('dir-origin').value || 'Jakarta';
            const destination = document.getElementById('dir-dest').value || 'Bandung';
            const mode = document.getElementById('dir-mode').value || 'driving';
            const out = document.getElementById('dir-out');
            out.textContent = 'Loading...';
            
            try {
                const res = await fetch(API + '/chat/directions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ origin, destination, mode })
                });
                const data = await res.json();
                out.textContent = data.content || JSON.stringify(data);
            } catch (err) {
                out.textContent = 'Error: ' + err.message;
            }
        }

        async function onPlaces() {
            const query = document.getElementById('pl-query').value || 'coffee near BSD';
            const location = document.getElementById('pl-loc').value.trim();
            const radius = parseInt(document.getElementById('pl-rad').value || '5000', 10);
            const out = document.getElementById('pl-out');
            out.textContent = 'Loading...';
            
            try {
                const body = { query, radius };
                if (location) body.location = location;
                
                const res = await fetch(API + '/chat/places', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body)
                });
                const data = await res.json();
                out.textContent = data.content || JSON.stringify(data);
            } catch (err) {
                out.textContent = 'Error: ' + err.message;
            }
        }
    </script>
</body>
</html>
        """,
        status_code=200
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
