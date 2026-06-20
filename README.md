# Healthcare Voice Appointment Assistant

A production-ready voice assistant built for scheduling healthcare appointments using FastAPI, Next.js, Gemini, and Deepgram.

## Features
- Voice-first interface with an animated avatar.
- Real-time Speech-to-Text via Deepgram.
- Natural conversation and function calling via Gemini 2.5 Flash.
- Automated appointment booking with double-booking prevention via SQLite.
- Text-to-Speech playback using browser native SpeechSynthesis (easy to upgrade to Cartesia/Google TTS).
- Post-call summary extraction.

## Project Structure
- `backend/`: FastAPI application handling logic, SQLite DB, LLM processing, and STT/TTS.
- `frontend/`: Next.js 14 App Router with Tailwind CSS and React hooks for audio capture.

## Setup Instructions

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
Fill in `.env` with your API keys.

Start the backend:
```bash
uvicorn app.main:app --reload --port 8000
```
API Docs will be available at `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the application at `http://localhost:3000`.

## Deployment
- **Backend**: Can be deployed on Render, Heroku, or AWS Elastic Beanstalk using Docker or straight WSGI/ASGI via `uvicorn`. Ensure SQLite is either swapped for PostgreSQL or attached to persistent storage.
- **Frontend**: Best deployed on Vercel or Netlify. Connect the GitHub repo and deploy the Next.js app. Configure the `NEXT_PUBLIC_BACKEND_URL` (if added) to point to your deployed backend.

## Assessment Notes
- Architecture simplified to a single `POST /conversation` endpoint to optimize latency and minimize points of failure for the rapid assessment.
- Avatar implemented using CSS animations to avoid heavy external UI library dependencies, providing a smooth and fast UX.
- Tool calling happens server-side, preventing client-side injection vulnerabilities.
