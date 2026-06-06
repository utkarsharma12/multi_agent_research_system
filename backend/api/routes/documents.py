"""
Documents API routes — upload PDFs and manage the indexed document library.
"""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import Document
from database.schemas import DocumentResponse
from rag.vector_store import add_documents
from services.pdf_loader import extract_text_from_pdf, chunk_text

router = APIRouter(prefix="/api/documents", tags=["documents"])

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentResponse:
    """
    Upload a PDF file, extract its text, chunk it,
    embed the chunks into ChromaDB, and save metadata to the DB.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    # Save the file
    file_id = str(uuid.uuid4())
    safe_name = f"{file_id}_{file.filename}"
    file_path = UPLOAD_DIR / safe_name

    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")

    # Extract text chunks
    try:
        full_text = extract_text_from_pdf(str(file_path))
        chunks = chunk_text(full_text)
    except Exception as e:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Failed to parse PDF: {e}")

    if not chunks:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail="No text could be extracted from the PDF.")

    # Index into ChromaDB
    metadatas = [
        {
            "source": "pdf",
            "file_name": file.filename,
            "file_id": file_id,
            "chunk_index": str(i),
        }
        for i in range(len(chunks))
    ]
    try:
        add_documents(chunks, metadatas)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to index document: {e}")

    # Save to relational DB
    doc = Document(
        title=file.filename.replace(".pdf", "").replace("_", " "),
        source="pdf",
        file_path=str(file_path),
        embedding_id=file_id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return DocumentResponse.model_validate(doc)


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db)) -> list[DocumentResponse]:
    """Return all indexed documents ordered by most recent."""
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [DocumentResponse.model_validate(d) for d in docs]


@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db)) -> dict:
    """Delete a document from the DB (and its file if it exists)."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove file
    if doc.file_path and os.path.exists(doc.file_path):
        try:
            os.remove(doc.file_path)
        except OSError:
            pass

    db.delete(doc)
    db.commit()
    return {"message": "Document deleted successfully."}
