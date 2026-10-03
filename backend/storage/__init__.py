"""
Same switch pattern as db/__init__.py. Everywhere else does
`import storage` and calls `storage.upload_file(...)` — never knowing
whether that saved to local disk or Supabase Storage.

Uses the same USE_MOCK_DB flag as the database, since in a hackathon
you're moving both together — but if you ever want file storage to
switch independently of the DB, split this into its own flag in
config.py.
"""

import config

if config.USE_MOCK_DB:
    from storage.mock_storage import *  # noqa: F401,F403
else:
    from storage.supabase_storage import *  # noqa: F401,F403