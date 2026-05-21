from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Optional

from openai import OpenAI


SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png"}


VISION_PROMPT = """
Eres un parser legal multimodal. Extrae el texto completo del contrato escaneado.
Reglas:
- Conserva títulos, numeración de cláusulas, partes, fechas, montos, porcentajes y plazos.
- No inventes texto que no aparezca en la imagen.
- Corrige únicamente errores obvios de OCR cuando el contexto legal lo permita.
- Devuelve solo el texto estructurado, sin comentarios externos.
""".strip()


def validate_image_path(image_path: str | Path) -> Path:
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"No existe la imagen: {path}")
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Formato no soportado: {path.suffix}. Usar JPEG/PNG.")
    if path.stat().st_size == 0:
        raise ValueError(f"La imagen está vacía: {path}")
    return path


def encode_image_to_data_url(image_path: str | Path) -> str:
    path = validate_image_path(image_path)
    mime_type = mimetypes.guess_type(path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def parse_contract_image(
    image_path: str | Path,
    *,
    model: str = "gpt-4o",
    client: Optional[OpenAI] = None,
) -> str:
    """Parse a contract image into faithful structured text using GPT-4o Vision."""

    data_url = encode_image_to_data_url(image_path)
    client = client or OpenAI()

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": VISION_PROMPT},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
        temperature=0,
    )
    text = getattr(response, "output_text", None)
    if not text:
        raise RuntimeError("La API no devolvió texto parseado para la imagen.")
    return text.strip()
