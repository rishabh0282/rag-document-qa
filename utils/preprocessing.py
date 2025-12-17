"""
Small preprocessing helpers.
"""
import re
from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split `text` into chunks of up to `chunk_size` tokens with `overlap` tokens between chunks.

    Raises:
        ValueError: if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    tokens = text.split()
    if not tokens:
        return []

    chunks: List[str] = []
    start = 0
    step = chunk_size - overlap
    while start < len(tokens):
        end = start + chunk_size
        chunk = tokens[start:end]
        chunks.append(" ".join(chunk))
        start += step
    return chunks


def clean_text(text: str) -> str:
    """
    Normalize whitespace in `text` and trim leading/trailing spaces.
    """
    return re.sub(r"\s+", " ", text).strip()