"""Lógica de negocio para la gestión de documentos de organizaciones (RF-03).

Flujo en dos pasos: la org pide una URL firmada de subida (presigned POST),
sube el archivo directamente desde el navegador a S3, y luego notifica al
backend para que guarde el registro (POST /org/documents).
"""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DocumentType, OrganizationDocument
from app.schemas.document import (
    DocumentUploadURLResponse,
    OrgDocumentDTO,
    PresignedPostData,
)
from app.services.storage_service import (
    generate_presigned_download_url,
    generate_presigned_upload_url,
)


def _to_dto(doc: OrganizationDocument) -> OrgDocumentDTO:
    url = generate_presigned_download_url(doc.ruta) or ""
    return OrgDocumentDTO(
        id=str(doc.id),
        nombre_archivo=doc.nombre_archivo,
        tipo=doc.tipo.value,
        url=url,
    )


def get_upload_url(
    org_id: uuid.UUID,
    nombre_archivo: str,
    tipo: str,
) -> DocumentUploadURLResponse:
    """Genera una URL firmada de subida directa a S3 para el navegador."""
    object_key = f"orgs/{org_id}/{uuid.uuid4()}_{nombre_archivo}"
    presigned = generate_presigned_upload_url(object_key)
    if presigned is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo generar la URL de subida. Inténtalo más tarde.",
        )
    return DocumentUploadURLResponse(
        presigned_post=PresignedPostData(
            url=presigned["url"],
            fields={k: str(v) for k, v in presigned["fields"].items()},
        ),
        object_key=object_key,
    )


def save_document(
    db: Session,
    org_id: uuid.UUID,
    nombre_archivo: str,
    object_key: str,
    tipo: str,
) -> OrgDocumentDTO:
    """Guarda el registro de un documento tras una subida exitosa a S3."""
    try:
        doc_tipo = DocumentType(tipo)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Tipo de documento inválido: '{tipo}'. Usa 'pdf' o 'jpg'.",
        )
    doc = OrganizationDocument(
        organization_id=org_id,
        nombre_archivo=nombre_archivo,
        ruta=object_key,
        tipo=doc_tipo,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return _to_dto(doc)


def list_org_documents(db: Session, org_id: uuid.UUID) -> list[OrgDocumentDTO]:
    """Devuelve todos los documentos de una organización con URLs firmadas de descarga."""
    docs = db.scalars(
        select(OrganizationDocument)
        .where(OrganizationDocument.organization_id == org_id)
        .order_by(OrganizationDocument.created_at)
    ).all()
    return [_to_dto(doc) for doc in docs]
