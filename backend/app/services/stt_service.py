import os
from dotenv import load_dotenv
load_dotenv()

import httpx
from fastapi import UploadFile

# Global client keeps the connection pool alive to prevent repeated SSL handshakes
http_client = httpx.AsyncClient()

DEEPGRAM_API_KEY = os.environ.get("DEEPGRAM_API_KEY")

async def transcribe_audio(file: UploadFile) -> str:
    if not DEEPGRAM_API_KEY or DEEPGRAM_API_KEY == "DUMMY_KEY":
        # Fallback if no key
        return "This is a fallback transcription since no Deepgram key is set."
        
    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true"
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": file.content_type or "audio/wav"
    }
    
    content = await file.read()
    
    response = await http_client.post(url, headers=headers, content=content, timeout=10.0)
        
    if response.status_code == 200:
        data = response.json()
        return data['results']['channels'][0]['alternatives'][0]['transcript']
    else:
        raise Exception(f"Deepgram STT Error: {response.text}")
