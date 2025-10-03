import httpx
from typing import Optional
import logging
from config import get_settings


async def generate_with_ollama(prompt: str, model: Optional[str] = None, max_retries: int = 2) -> str:
    settings = get_settings()
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload = {
        "model": model or settings.OLLAMA_MODEL, 
        "prompt": prompt, 
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 150,  # Shorter responses for faster generation
            "top_k": 10,
            "top_p": 0.9
        }
    }

    for attempt in range(max_retries + 1):
        try:
            # Flexible timeout - longer for first attempt, shorter for retries
            timeout = 60 if attempt == 0 else 30
            async with httpx.AsyncClient(timeout=timeout) as client:
                r = await client.post(url, json=payload)
                r.raise_for_status()
                data = r.json()
                response = data.get("response", "").strip()
                if response:  # Only return non-empty responses
                    return response
        except (httpx.TimeoutException, httpx.ReadTimeout) as e:
            logging.warning(f"Ollama timeout attempt {attempt + 1}/{max_retries + 1} ({timeout}s): {e}")
            if attempt == max_retries:
                # Don't raise exception - let caller handle fallback
                return ""
        except Exception as e:
            logging.error(f"Ollama error attempt {attempt + 1}/{max_retries + 1}: {e}")
            if attempt == max_retries:
                # Don't raise exception - let caller handle fallback  
                return ""
    
    return ""
