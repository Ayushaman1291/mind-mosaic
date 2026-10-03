"""
This is the ONLY file that decides which database backend is active.
Everywhere else in the app does `import db` and calls `db.get_user(...)`,
`db.create_user(...)`, etc. — never knowing or caring whether that's
hitting the mock in-memory store or real Supabase.

To switch from mock to Supabase once your teammate's project is ready:
  1. Fill in SUPABASE_URL and SUPABASE_KEY in .env
  2. Set USE_MOCK_DB=false in .env
That's it — no code changes anywhere else.
"""

import config

if config.USE_MOCK_DB:
    from db.mock_db import *  # noqa: F401,F403
else:
    from db.supabase_db import *  # noqa: F401,F403