"""
mock_storage.py
----------------
TEMPORARY local-disk file storage. Saves uploaded photos to
static/uploads/ and returns a full, absolute URL (not just a relative
path) — needed because photos are loaded by things running on a
different origin entirely (e.g. the Unity WebGL game), so a relative
path like "/static/uploads/x.jpg" would resolve against the wrong
website and 404. A relative path only works when the thing loading it
is on the exact same website as the backend.
Fine for local dev/demo — not for production or team-shared access
(files only exist on whichever machine ran the upload).
"""

import os
import uuid
from flask import request

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def upload_file(file_bytes, filename, content_type=None):
    ext = os.path.splitext(filename)[1] or ""
    unique_name = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(UPLOAD_DIR, unique_name)

    with open(path, "wb") as f:
        f.write(file_bytes)

    # request.host_url gives whatever address was actually used to reach
    # this server (e.g. "http://127.0.0.1:5000/" locally, or your real
    # deployed address later) — so the returned link always works no
    # matter which website/app is asking for the photo.
    return request.host_url.rstrip("/") + f"/static/uploads/{unique_name}"