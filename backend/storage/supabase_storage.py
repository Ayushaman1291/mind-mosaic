"""
supabase_storage.py
---------------------
Real file storage using Supabase Storage.

Requires a bucket named "photos" to exist in your Supabase project
(Dashboard -> Storage -> New bucket -> name it "photos" -> make it
public, since these are family photos being displayed back in the app,
not sensitive documents).
"""

import uuid
import os
from supabase_client import supabase

BUCKET = "photos"


def upload_file(file_bytes, filename, content_type=None):
    ext = os.path.splitext(filename)[1] or ""
    unique_name = f"{uuid.uuid4().hex}{ext}"

    supabase.storage.from_(BUCKET).upload(
        unique_name,
        file_bytes,
        {"content-type": content_type or "application/octet-stream"},
    )

    return supabase.storage.from_(BUCKET).get_public_url(unique_name)