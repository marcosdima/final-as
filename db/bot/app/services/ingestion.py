import re
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.embeddings import embed_texts
from app.models import DocumentoMetadata, DocumentoVectorial
from app.schemas import DocumentoIngestRequest, DocumentoIngestResponse


def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    Divide un texto en fragmentos respetando oraciones y párrafos.
    """
    clean_text = re.sub(r"\r\n|\r", "\n", text).strip()
    if not clean_text:
        return []

    if len(clean_text) <= chunk_size:
        return [clean_text]

    paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = ""

    for p in paragraphs:
        if len(current_chunk) + len(p) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{p}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            # Si el párrafo individual es mayor a chunk_size, se parte por ventana
            if len(p) > chunk_size:
                start = 0
                while start < len(p):
                    end = min(start + chunk_size, len(p))
                    chunks.append(p[start:end].strip())
                    start += chunk_size - chunk_overlap
                current_chunk = ""
            else:
                current_chunk = p

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


async def ingest_document(
    db: AsyncSession,
    request: DocumentoIngestRequest
) -> DocumentoIngestResponse:
    """
    Registra metadatos, fragmenta el contenido, calcula embeddings y almacena en PostgreSQL.
    """
    # 1. Determinar fragmentos
    if request.fragmentos and len(request.fragmentos) > 0:
        chunks = [f.strip() for f in request.fragmentos if f.strip()]
    elif request.contenido_completo:
        chunks = chunk_text(
            request.contenido_completo,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
    else:
        chunks = [request.titulo]

    # 2. Generar embeddings vectoriales
    embeddings = embed_texts(chunks)

    # 3. Insertar metadatos principales
    doc_meta = DocumentoMetadata(
        titulo=request.titulo,
        tipo_documento=request.tipo_documento,
        carrera=request.carrera,
        activo=True
    )
    db.add(doc_meta)
    await db.flush()  # Obtener el id generado

    # 4. Insertar cada fragmento en documentos_vectoriales
    for idx, (chunk_str, emb_vec) in enumerate(zip(chunks, embeddings)):
        chunk_metadata = {
            "titulo": request.titulo,
            "tipo_documento": request.tipo_documento,
            "carrera": request.carrera,
            "chunk_index": idx,
            "total_chunks": len(chunks)
        }
        if request.metadata_adicional:
            chunk_metadata.update(request.metadata_adicional)

        vector_record = DocumentoVectorial(
            documento_id=doc_meta.id,
            contenido=chunk_str,
            meta=chunk_metadata,
            embedding=emb_vec
        )
        db.add(vector_record)

    await db.commit()
    await db.refresh(doc_meta)

    return DocumentoIngestResponse(
        documento_id=doc_meta.id,
        titulo=doc_meta.titulo,
        tipo_documento=doc_meta.tipo_documento,
        carrera=doc_meta.carrera,
        fragmentos_creados=len(chunks),
        mensaje="Documento fragmentado, vectorizado e indexado correctamente."
    )
