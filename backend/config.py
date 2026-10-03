import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Default to mock if not explicitly set to "false", or if Supabase
# credentials aren't filled in yet — so this never crashes on missing
# creds, it just quietly falls back to the mock DB.
_use_mock_flag = os.environ.get("USE_MOCK_DB", "true").lower()
USE_MOCK_DB = _use_mock_flag != "false" or not SUPABASE_URL or not SUPABASE_KEY