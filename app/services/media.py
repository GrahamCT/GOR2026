import mimetypes
import os
import shutil

from dotenv import load_dotenv
from fastapi import UploadFile

load_dotenv()

STORAGE_CONN = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
MEDIA_CONTAINER = os.getenv("MEDIA_CONTAINER")
MEDIA_BASE_URL = os.getenv("MEDIA_BASE_URL")

LOCAL_MEDIA_DIR = "app/static"
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".svg"}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
CACHE_CONTROL = "public, max-age=31536000"


def media_url(path: str) -> str:
    """Turn a DB image path (e.g. partners/logo_x.png) into a full URL."""
    if not path:
        return ""
    if path.startswith(("http://", "https://")):
        return path
    base = MEDIA_BASE_URL or "/static/"
    return base.rstrip("/") + "/" + path.lstrip("/")


def validate_image(upload: UploadFile) -> None:
    """Raise ValueError if the upload isn't an allowed image type or is too large."""
    ext = os.path.splitext(upload.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"{upload.filename}: only {', '.join(sorted(ALLOWED_EXTENSIONS))} allowed")
    upload.file.seek(0, os.SEEK_END)
    size = upload.file.tell()
    upload.file.seek(0)
    if size > MAX_UPLOAD_BYTES:
        raise ValueError(f"{upload.filename}: larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB")


def upload_image(upload: UploadFile, blob_path: str) -> None:
    """Save to Azure Blob Storage, or to app/static locally if storage isn't configured."""
    if STORAGE_CONN and MEDIA_CONTAINER:
        from azure.storage.blob import BlobServiceClient, ContentSettings

        content_type = mimetypes.guess_type(blob_path)[0] or "application/octet-stream"
        client = BlobServiceClient.from_connection_string(STORAGE_CONN)
        blob = client.get_blob_client(container=MEDIA_CONTAINER, blob=blob_path)
        blob.upload_blob(
            upload.file,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type, cache_control=CACHE_CONTROL),
        )
        return

    dest = os.path.join(LOCAL_MEDIA_DIR, blob_path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        shutil.copyfileobj(upload.file, f)
