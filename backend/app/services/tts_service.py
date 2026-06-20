import os
from dotenv import load_dotenv
load_dotenv()

import base64
import httpx

DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")

async def generate_speech(text: str) -> str:
    """Returns base64 encoded audio string using Deepgram TTS."""
    if not DEEPGRAM_API_KEY or DEEPGRAM_API_KEY == "DUMMY_KEY":
        return ""
        
    url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload, timeout=15.0)
        
    if response.status_code == 200:
        return base64.b64encode(response.content).decode("utf-8")
    else:
        print(f"Deepgram TTS Error: {response.text}")
        return ""
