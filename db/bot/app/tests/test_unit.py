import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.schemas.documents import DocumentIngestRequest
from app.services.ingestion import chunk_text


def test_chunk_text_normal_and_invalid_overlap():
    text = "First paragraph with institutional details.\n\nSecond paragraph with course rules."
    chunks = chunk_text(text, chunk_size=120, chunk_overlap=20)
    assert len(chunks) == 1

    long_para = "A" * 250
    windowed = chunk_text(long_para, chunk_size=100, chunk_overlap=20)
    assert len(windowed) >= 3

    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_text(long_para, chunk_size=100, chunk_overlap=100)

    with pytest.raises(ValueError, match="chunk_overlap"):
        chunk_text(long_para, chunk_size=100, chunk_overlap=150)


def test_ingest_schema_validation():
    with pytest.raises(ValueError):
        DocumentIngestRequest(
            title="Regulation without content",
            document_type="regulation",
        )

    with pytest.raises(ValueError):
        DocumentIngestRequest(
            title="Invalid overlap",
            document_type="regulation",
            full_content="Valid sample text long enough for validation.",
            chunk_size=100,
            chunk_overlap=100,
        )


def test_password_and_jwt_roundtrip():
    hashed = hash_password("secret.password")
    assert verify_password("secret.password", hashed)
    assert not verify_password("wrong.password", hashed)

    token = create_access_token(user_id=8, email="mdimatteo@alumno.isft189.edu.ar", role="STUDENT")
    payload = decode_access_token(token)
    assert payload["sub"] == "8"
    assert payload["role"] == "STUDENT"
