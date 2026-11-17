import io
import re
from typing import List, Optional

from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings import embed_texts_async
from app.institute_models import Career
from app.models import DocumentChunk, DocumentMetadata
from app.schemas import DocumentIngestRequest, DocumentIngestResponse

DOC_TYPE_TO_DB = {
    "study_plan": "plan_estudio",
    "regulation": "reglamento",
    "prerequisites": "correlatividades",
    "resolution": "resolucion",
    "other": "otro",
}
DOC_TYPE_FROM_DB = {v: k for k, v in DOC_TYPE_TO_DB.items()}


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """Split plain text into overlapping chunks respecting paragraph boundaries."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")
    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be >= 0 and strictly less than chunk_size")

    clean_text = re.sub(r"\r\n|\r", "\n", text).strip()
    if not clean_text:
        return []

    if len(clean_text) <= chunk_size:
        return [clean_text]

    paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
    chunks: List[str] = []
    current_chunk = ""
    step = chunk_size - chunk_overlap

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{paragraph}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            if len(paragraph) > chunk_size:
                start = 0
                while start < len(paragraph):
                    end = min(start + chunk_size, len(paragraph))
                    segment = paragraph[start:end].strip()
                    if segment:
                        chunks.append(segment)
                    if end >= len(paragraph):
                        break
                    start += step
                current_chunk = ""
            else:
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract plain text from raw PDF bytes for chunking and indexing."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages_text = []
    for page in reader.pages:
        text = (page.extract_text() or "").strip()
        if text:
            pages_text.append(text)
    return "\n\n".join(pages_text)


async def ingest_document(
    db: AsyncSession,
    request: DocumentIngestRequest,
) -> DocumentIngestResponse:
    """Validate career FK, chunk text, generate embeddings, and persist vectors."""
    career_name: Optional[str] = None
    if request.career_id is not None:
        career_row = (
            await db.execute(
                select(Career).where(Career.id == request.career_id, Career.active == True)
            )
        ).scalar_one_or_none()
        if not career_row:
            raise LookupError(f"Active career with id={request.career_id} not found.")
        career_name = career_row.name

    if request.chunks and len(request.chunks) > 0:
        chunks = [c.strip() for c in request.chunks if c.strip()]
    elif request.full_content and request.full_content.strip():
        chunks = chunk_text(
            request.full_content,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
    else:
        raise ValueError("Document contains no valid text to vectorize.")

    if not chunks:
        raise ValueError("No non-empty chunks were produced from the provided content.")

    embeddings = await embed_texts_async(chunks)
    db_doc_type = DOC_TYPE_TO_DB[request.document_type]

    doc_meta = DocumentMetadata(
        title=request.title,
        document_type=db_doc_type,
        career_id=request.career_id,
        active=True,
    )
    db.add(doc_meta)
    await db.flush()

    for idx, (chunk_str, emb_vec) in enumerate(zip(chunks, embeddings)):
        chunk_metadata = {
            "title": request.title,
            "document_type": request.document_type,
            "career_id": request.career_id,
            "career": career_name,
            "chunk_index": idx,
            "total_chunks": len(chunks),
        }
        if request.additional_metadata:
            chunk_metadata.update(request.additional_metadata)

        vector_record = DocumentChunk(
            document_id=doc_meta.id,
            content=chunk_str,
            meta=chunk_metadata,
            embedding=emb_vec,
        )
        db.add(vector_record)

    await db.commit()
    await db.refresh(doc_meta)

    return DocumentIngestResponse(
        document_id=doc_meta.id,
        title=doc_meta.title,
        document_type=request.document_type,
        career_id=doc_meta.career_id,
        career_name=career_name,
        chunks_created=len(chunks),
        message="Document chunked, vectorized, and indexed successfully.",
    )
