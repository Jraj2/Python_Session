import pathlib
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, EMBEDDING_DIMENSIONS

_client = genai.Client(api_key=GEMINI_API_KEY)
_MODEL = "gemini-embedding-2"

_IMAGE_MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
_VIDEO_MIME = {".mp4": "video/mp4", ".mov": "video/quicktime", ".avi": "video/x-msvideo", ".webm": "video/webm"}


def embed_text(text: str) -> list[float]:
    result = _client.models.embed_content(
        model=_MODEL,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    return result.embeddings[0].values


def embed_image(path: str) -> list[float]:
    p = pathlib.Path(path)
    mime_type = _IMAGE_MIME.get(p.suffix.lower(), "image/jpeg")
    part = types.Part.from_bytes(data=p.read_bytes(), mime_type=mime_type)
    result = _client.models.embed_content(
        model=_MODEL,
        contents=part,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    return result.embeddings[0].values


def embed_video(path: str) -> list[float]:
    p = pathlib.Path(path)
    mime_type = _VIDEO_MIME.get(p.suffix.lower(), "video/mp4")
    part = types.Part.from_bytes(data=p.read_bytes(), mime_type=mime_type)
    result = _client.models.embed_content(
        model=_MODEL,
        contents=part,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    return result.embeddings[0].values
