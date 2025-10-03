# 📋 HeyPico Maps - Complete Product Knowledge

## 🎯 **Product Overview**

**HeyPico Maps** adalah aplikasi Maps Assistant yang mengintegrasikan **Google Maps API** dengan **Local LLM (Ollama)** untuk memberikan respons cerdas tentang navigasi dan pencarian tempat.

### **Core Value Proposition:**
- ✅ **AI-Powered Maps**: Kombinasi Google Maps dengan AI lokal untuk pengalaman yang lebih interaktif
- ✅ **Privacy-First**: Menggunakan LLM lokal (Ollama) tanpa mengirim data ke cloud
- ✅ **Multi-Modal Transport**: Mendukung berbagai mode transportasi (driving, walking, bicycling, transit)
- ✅ **Real-time Route Planning**: Integrasi langsung dengan Google Maps API
- ✅ **Modern UI/UX**: Interface responsif dengan animasi dan glassmorphism design

---

## 🏗️ **System Architecture**

### **Technology Stack:**
```
Frontend (Web) → FastAPI (Backend) → Google Maps API
                      ↓
               Ollama (Local LLM) ← Redis (Rate Limiting)
```

### **Container Services:**
1. **API Container** (`heypico_api:8000`)
   - FastAPI backend
   - Python 3.11-slim
   - Rate limiting & CORS

2. **Web Container** (`heypico_web:3000`)
   - Nginx static server  
   - Modern HTML/CSS/JS frontend

3. **Ollama Container** (`heypico_ollama:11434`)
   - Local LLM server
   - Default model: llama3.2:3b
   - Auto-initialization

4. **Redis Container** (`heypico_redis`)
   - Rate limiting storage
   - Session management

5. **OpenWebUI Container** (`heypico_openwebui:3001`)
   - Alternative AI interface
   - Direct Ollama access

---

## 🔗 **API Endpoints & Features**

### **Base API Information:**
- **Base URL**: `http://localhost:8000`
- **Documentation**: `http://localhost:8000/docs`
- **Rate Limit**: 60 requests/minute per IP
- **CORS**: Enabled for all origins

### **1. Core Chat Endpoints**

#### **GET /chat/models**
- **Purpose**: List available Ollama models
- **Response**: Array of model objects
- **Example**: `[{"name": "llama3.2:3b", "size": "2GB", ...}]`

#### **POST /chat**
- **Purpose**: General AI chat
- **Request**: `{"prompt": "string", "model": "optional"}`
- **Response**: `{"model": "string", "content": "string"}`
- **Rate Limited**: ✅

#### **POST /chat/directions**
- **Purpose**: AI-powered route planning
- **Request**: 
  ```json
  {
    "origin": "Jakarta",
    "destination": "Bandung", 
    "mode": "driving",
    "model": "llama3.2:3b"
  }
  ```
- **Response**: Formatted route with:
  - 📏 Distance calculation
  - ⏱️ Duration (multi-leg parsing)
  - 🚗/🚶/🚴/🚌 Transportation icons
  - 🤖 AI summary
  - 🔗 Google Maps links
- **Features**:
  - Multi-segment route support
  - Accurate duration calculation
  - Transportation mode icons
  - Fallback to Google Maps

#### **POST /chat/places**
- **Purpose**: AI-powered place search
- **Request**:
  ```json
  {
    "query": "coffee shops near BSD",
    "location": "-6.2,106.8",
    "radius": 5000,
    "model": "llama3.2:3b"
  }
  ```
- **Response**: 
  - 🔍 Search results (top 5)
  - 🤖 AI recommendations
  - 📍 Place details
  - 🔗 Embed map links

### **2. Direct Maps API**

#### **POST /maps/directions**
- **Purpose**: Raw Google Maps directions
- **Response**: `DirectionsResult` with polyline & legs
- **No AI Processing**: Direct API response

#### **POST /maps/places**
- **Purpose**: Raw Google Maps places search
- **Response**: `PlacesResult` with place items
- **No AI Processing**: Direct API response

#### **GET /maps/directions/view**
- **Purpose**: Embedded map view for routes
- **Parameters**: `origin`, `destination`, `mode`, `zoom`
- **Response**: HTML iframe with Google Maps embed
- **Features**: Auto-focus on route, responsive design

#### **GET /maps/places/view**
- **Purpose**: Embedded map view for places
- **Parameters**: `q` (query), `location`, `zoom`
- **Response**: HTML iframe with Google Maps embed

### **3. System Endpoints**

#### **GET /**
- **Purpose**: API information
- **Response**: Version, docs links, demo links

#### **GET /health**
- **Purpose**: Health check
- **Response**: `{"status": "healthy"}`

#### **GET /ui**
- **Purpose**: Demo UI for API testing
- **Response**: HTML interface for testing endpoints

---

## 🎨 **Frontend Features**

### **User Interface Components:**

#### **1. Navigation Header**
- **HeyPico Maps** branding with gradient logo
- **API Demo** button → Opens FastAPI docs
- **OpenWebUI** button → Opens alternative AI interface
- **Responsive design** with mobile support

#### **2. Main Content Grid**

##### **Direction Panel**
- **Origin/Destination** input fields
- **Transportation Mode** selector:
  - 🚗 Driving (default)
  - 🚶 Walking  
  - 🚴 Bicycling
  - 🚌 Transit
- **Model Selection** dropdown (Ollama models)
- **Get Directions** button with loading states

##### **Places Panel** 
- **Search Query** input
- **Location** (optional lat,lng)
- **Radius** selector (1-10km)
- **Model Selection** dropdown
- **Search Places** button with loading states

#### **3. Results Display**
- **Animated responses** with typewriter effect
- **Markdown rendering** for formatted content
- **Link handling** for Google Maps integration
- **Error states** with user-friendly messages
- **Loading indicators** during API calls

#### **4. Developer Credit**
- **Enhanced styling** with glassmorphism effect
- **Interactive animations** (ripple effects, hover)
- **Gradient background** with backdrop blur
- **Responsive positioning** (bottom-right)
- **Click interactions** with toast notifications

### **Design System:**

#### **Color Scheme:**
```css
--bg: #0b1220 (Dark blue background)
--card: rgba(255,255,255,0.08) (Translucent cards)
--border: rgba(255,255,255,0.15) (Subtle borders)
--text: #e6edf3 (Light text)
--muted: #a6b3c2 (Secondary text)
--primary: #7c3aed (Purple accent)
--primary-2: #06b6d4 (Cyan accent)
```

#### **Animations:**
- **Gradient Shift**: Background animation (15s loop)
- **Fade In Up**: Container entrance animation
- **Button Hover**: Scale & glow effects
- **Loading States**: Pulse animations
- **Developer Credit**: Slide-in, bounce, ripple effects

#### **Responsive Design:**
- **Mobile-first** approach
- **Fluid typography** scaling
- **Touch-friendly** button sizes
- **Collapsible panels** on small screens

---

## 🔧 **External Integrations**

### **1. Google Maps API**
- **Service**: Google Maps Platform
- **Endpoints Used**:
  - **Directions API**: Route calculation
  - **Places API**: Location search
  - **Embed API**: Map visualization
- **API Key**: Required (set in `.env`)
- **Language**: English (forced)
- **Features**:
  - Multi-modal routing
  - Real-time traffic data
  - Place search with ratings
  - Embedded map views

### **2. Ollama (Local LLM)**
- **Service**: Local AI inference server
- **Default Model**: llama3.2:3b (2GB)
- **Features**:
  - **No internet required** for AI
  - **Privacy-preserving** (local processing)
  - **Model management** (pull/list)
  - **Streaming responses** (if needed)
- **Initialization**: Auto-pulls default model on startup
- **Performance**: Optimized timeouts (30s max)

### **3. Redis**
- **Service**: In-memory data store
- **Purpose**: Rate limiting storage
- **Features**:
  - **Per-IP rate limiting** (60 req/min)
  - **Session management**
  - **Fast response caching**
- **Configuration**: Default Redis 7-alpine

---

## 📊 **Business Logic & Features**

### **1. Route Planning Intelligence**

#### **Transportation Mode Normalization:**
```python
Synonyms = {
    "drive/car/mobil/auto" → "driving",
    "jalan/foot/pejalan" → "walking", 
    "sepeda/bike/bicycle/cycling" → "bicycling",
    "public/bus/train/kereta/angkutan umum" → "transit"
}
```

#### **Duration Calculation:**
- **Multi-leg parsing**: Sums all route segments
- **Format conversion**: "2 hours 46 mins" → proper calculation
- **Error handling**: Fallback to Google's raw response

#### **Distance Calculation:**
- **Metric conversion**: Handles km format
- **Precision**: 1 decimal place
- **Multi-segment**: Sums all legs

### **2. Place Search Intelligence**

#### **Search Optimization:**
- **Top 10 results** from Google Places
- **AI filtering**: LLM selects best options
- **Relevance ranking**: Distance + rating factors
- **Fallback handling**: Shows raw results if AI fails

#### **Location Context:**
- **Optional geo-targeting**: lat,lng support
- **Radius filtering**: 1-10km range
- **Query enhancement**: Natural language processing

### **3. AI Enhancement Strategy**

#### **Hybrid Approach:**
1. **Fast Maps Data** (always works)
2. **AI Enhancement** (best effort)
3. **Graceful Degradation** (fallback to maps-only)

#### **Performance Optimization:**
- **Parallel processing**: Maps + AI simultaneously
- **Timeout management**: 30s max for AI
- **Retry logic**: Limited retries for reliability
- **Caching**: Response optimization

---

## 🔐 **Security & Configuration**

### **Environment Variables:**
```env
GOOGLE_MAPS_API_KEY=your_api_key_here
RATE_LIMIT_PER_MINUTE=60
OLLAMA_BASE_URL=http://ollama:11434
API_BASE_URL=http://localhost:8000
APP_ENV=production
TZ=Asia/Jakarta
```

### **Security Features:**
- **Rate Limiting**: 60 requests/minute per IP
- **CORS Protection**: Configurable origins
- **Input Validation**: Pydantic schemas
- **Error Handling**: No sensitive data exposure
- **Health Checks**: System monitoring

### **Privacy Features:**
- **Local AI**: No data sent to external AI services
- **Anonymous Usage**: No user tracking
- **Minimal Logging**: Only error logging
- **Self-hosted**: Complete control over data

---

## 🚀 **Deployment & Operations**

### **Docker Compose Setup:**
```yaml
Services: api, web, ollama, ollama-init, openwebui, redis
Networks: Internal network isolation
Volumes: ollama_models, openwebui_data
Restart: unless-stopped (production ready)
```

### **Port Mapping:**
- `3000` → Web Frontend
- `8000` → API Backend  
- `3001` → OpenWebUI
- `11434` → Ollama (internal)
- `6379` → Redis (internal)

### **System Requirements:**
- **CPU**: 2+ cores recommended
- **RAM**: 4GB+ (for LLM)
- **Storage**: 5GB+ (models + data)
- **Network**: Internet for Google Maps API

### **Monitoring:**
- **Health endpoint**: `/health`
- **API documentation**: `/docs`
- **Model status**: `/chat/models`
- **Container logs**: Docker logging

---

## 📈 **Performance Metrics**

### **Response Times:**
- **Maps API**: ~500ms average
- **AI Processing**: ~2-5s average
- **Combined (Maps+AI)**: ~3-6s average
- **Fallback (Maps only)**: ~1s average

### **Throughput:**
- **Rate Limit**: 60 requests/minute/IP
- **Concurrent Users**: Limited by system resources
- **Model Performance**: Depends on hardware

### **Reliability:**
- **Uptime Target**: 99.9%
- **Error Handling**: Graceful degradation
- **Fallback Strategy**: Always show maps data
- **Auto-recovery**: Container restart policies

---

## 🎯 **Use Cases & User Scenarios**

### **Primary Use Cases:**

1. **Smart Route Planning**
   - User asks: "Best route from Jakarta to Bandung by car"
   - System provides: Distance, time, AI summary, map links

2. **Intelligent Place Discovery**
   - User asks: "Coffee shops near BSD City"
   - System provides: Top recommendations, AI filtering, map view

3. **Multi-modal Transportation**
   - User compares: Driving vs walking vs transit
   - System provides: Mode-specific routes with appropriate icons

4. **Embedded Map Integration**
   - User clicks map links
   - System provides: Interactive embedded Google Maps

### **Target Users:**
- **Developers**: Testing API integrations
- **End Users**: Route planning and place discovery
- **Businesses**: Location-based services
- **Researchers**: AI + Maps integration studies

---

## 🔄 **Future Enhancement Opportunities**

### **Potential Features:**
- **Voice Interface**: Speech-to-text integration
- **Real-time Traffic**: Live traffic updates
- **Offline Maps**: Cached map data
- **User Preferences**: Saved locations and routes
- **Analytics Dashboard**: Usage statistics
- **Multi-language**: Localization support
- **Mobile App**: Native iOS/Android apps
- **API Keys Management**: User authentication

### **Technical Improvements:**
- **Model Optimization**: Smaller, faster LLMs
- **Response Caching**: Redis-based caching
- **Load Balancing**: Multi-instance deployment
- **Database Integration**: Persistent data storage
- **Microservices**: Service decomposition
- **CI/CD Pipeline**: Automated deployment

---

## 📞 **Support & Maintenance**

### **Developer Information:**
- **Developer**: Amirudin
- **Contact**: Available via application footer
- **Version**: 1.0.0
- **Last Updated**: October 2025

### **Documentation:**
- **API Docs**: `http://localhost:8000/docs`
- **Source Code**: Available in project repository
- **Configuration**: Environment-based settings
- **Troubleshooting**: Health check endpoints

### **Known Limitations:**
- **Google Maps API**: Requires valid API key
- **LLM Performance**: Hardware dependent
- **Rate Limiting**: Per-IP restrictions
- **Internet Dependency**: Maps API requires connection

---

## 🏆 **Key Differentiators**

### **What makes HeyPico Maps unique:**

1. **🤖 Local AI Integration**: Privacy-first AI without cloud dependency
2. **⚡ Hybrid Architecture**: Fast maps data + intelligent AI enhancement
3. **🎨 Modern UI/UX**: Glassmorphism design with smooth animations  
4. **🔧 Developer-Friendly**: Complete API documentation and demo UI
5. **🔒 Privacy-Focused**: No user tracking or data collection
6. **📱 Responsive Design**: Works on all devices and screen sizes
7. **🌍 Multi-Modal**: Comprehensive transportation mode support
8. **🚀 Production-Ready**: Docker-based deployment with monitoring

---

*This product knowledge document provides comprehensive information about HeyPico Maps for technical teams, stakeholders, and end users. For specific implementation details, refer to the source code and API documentation.*