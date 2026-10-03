# MindMosaic Backend (Flask)

Backend for the MindMosaic elderly cognitive-support platform.
Works **right now** against an in-memory mock database, and switches
to real Supabase with **one config change** — no route code changes.

## Run it (mock DB — works immediately, no setup)

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # defaults to USE_MOCK_DB=true
python app.py
```

Server runs at `http://127.0.0.1:5000`. Check `GET /api/health` — it
tells you which DB backend is active.

Data in mock mode lives in memory and **resets every time you restart
the server**. That's expected — it's a placeholder, not the real thing.

## Switching to Supabase once it's ready

1. Your DB teammate creates a Supabase project at supabase.com and
   runs `schema.sql` (included here) in the Supabase SQL editor.
2. Get `Project URL` and the `service_role` key from
   **Supabase Dashboard → Settings → API**.
3. In `.env`:
   ```
   USE_MOCK_DB=false
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-service-role-key
   ```
4. Restart the server. That's it — every route now hits real Postgres.

Never commit `.env` or the service_role key. Use `service_role` on the
backend only; if frontend ever talks to Supabase directly (it
shouldn't need to — it should go through this API) it'd use the
`anon` key instead, which has row-level-security restrictions.

## How the swap works

```
routes/*.py  -->  import db  -->  db/__init__.py picks a backend
                                     |
                          USE_MOCK_DB=true?  USE_MOCK_DB=false?
                                |                    |
                        db/mock_db.py        db/supabase_db.py
                     (in-memory dicts)      (real Supabase calls)
```

Both `db/mock_db.py` and `db/supabase_db.py` expose the **exact same
function names and arguments** (`create_user`, `get_medicines`,
`record_game_result`, etc.). Routes only ever call `db.something(...)`
and have no idea which backend is behind it. This means:

- You can build and test the whole API today, before Supabase exists.
- Frontend can integrate against you today too — the JSON responses
  don't change when the backend switches.
- When your DB teammate is ready, flip `USE_MOCK_DB=false`, done.

## Project layout

```
app.py                -> creates Flask app, registers blueprints, exposes /api/health
config.py               -> reads .env, decides mock vs Supabase
schema.sql               -> SQL for DB teammate to run in Supabase
db/
  __init__.py            -> THE SWITCH — picks mock_db or supabase_db
  mock_db.py              -> temporary in-memory backend
  supabase_db.py           -> real Supabase backend
routes/
  registration.py        -> user signup, medicines
  reminders.py             -> daily reminders + medicine timetable
  games.py                  -> family quiz + memory shuffle
  photos.py                  -> photos & memories
  dashboard.py                -> caregiver dashboard / performance metrics
```

## API contract (for frontend)

Base URL: `http://127.0.0.1:5000/api`. All responses JSON.

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/registration/` | Create user `{name, birthday, medicines: [{name,time}]}` |
| GET | `/registration/<user_id>` | Get user + medicines |
| GET | `/registration/` | List all users |
| GET | `/reminders/<user_id>` | Get medicines + reminders |
| POST | `/reminders/<user_id>` | Add reminder `{text, time}` |
| PATCH | `/reminders/<user_id>/<reminder_id>/done` | Mark reminder done |
| GET | `/games/family-quiz/<user_id>/questions` | Get family members for quiz |
| POST | `/games/family-quiz/<user_id>/family-member` | Add family member `{name, relation, photo_url}` |
| POST | `/games/family-quiz/<user_id>/submit` | Submit result `{score, accuracy, time_taken, attempts}` |
| GET | `/games/memory-shuffle/<user_id>/cards` | Get photos for memory game |
| POST | `/games/memory-shuffle/<user_id>/submit` | Submit result (same shape as above) |
| GET | `/photos/<user_id>` | List memories |
| POST | `/photos/<user_id>` | Add memory `{photo_url, caption}` |
| GET | `/dashboard/<user_id>/summary` | Avg score/accuracy/games played |
| GET | `/dashboard/<user_id>/history?game=` | Full score history, optional game filter |

## Open questions to settle with the team

- **Photo upload**: `/photos` currently expects a `photo_url` string.
  If UI needs raw file upload, tell me — swap to Supabase Storage.
- **Auth**: none yet. Confirm whether the hackathon scope needs login,
  or `user_id` in the URL is enough for the demo.
- **AI/ML hook point**: `routes/games.py` has a `TODO(AIML)` comment
  for adaptive difficulty / personalized question selection.
