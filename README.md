# MindMosaic

**🔗 Live demo:** https://mind-mosaic-frontend.onrender.com

> Built for Smart India Hackathon 2026 by Team **Mind Alchemists**.

MindMosaic is a dementia-support platform for elderly users in North East India. It helps with daily medicine reminders, preserving family memories through photos, and gentle cognitive activities — in multiple regional languages.

> **Note:** The live demo is hosted on Render's free tier, which spins down after 15 minutes of inactivity. The first request after idling may take 30–60 seconds to wake up — this is expected, not a bug.

## Features

- Username-based registration and login
- Medicine and reminder scheduling, with optional notes and dosage
- Family member photo gallery with captions
- Two cognitive games (Memory Shuffle, Family Memory) built in Unity, served as WebGL
- Activity history and performance tracking
- Multi-language support covering North Eastern Indian languages
- Caregiver dashboard (in progress)

## Tech stack

- **Backend:** Flask REST API (`backend/`) — swappable mock in-memory DB / Supabase (Postgres) data layer
- **Frontend:** Flask + Jinja2 server-rendered app (`frontend/`) that calls the backend API
- **Games:** Unity WebGL builds (`web-game/`), served as static files
- **ML:** Difficulty prediction model for games (`MindMosaic_ML/`) — trained, not yet wired into gameplay
- **Deployment:** Render (two separate web services — backend and frontend)

## Repository structure

mind-mosaic/
├── backend/ Flask REST API (auth, reminders, photos, games, dashboard)
├── frontend/ Flask + Jinja2 app that renders the UI and calls the backend
├── web-game/ Unity WebGL builds for the cognitive games
└── MindMosaic_ML/ Difficulty-prediction model and training notebooks


## Running locally

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python app.py              # runs on http://127.0.0.1:5000
```

**Frontend** (in a separate terminal):
```bash
cd frontend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py              # runs on http://127.0.0.1:5001
```

Open `http://127.0.0.1:5001` in your browser.

## Team

Mind Alchemists — Smart India Hackathon 2026

