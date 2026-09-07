"""Schemas Pydantic para la gestión de documentos de organizaciones (RF-03)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class DocumentUploadURLRequest(BaseModel):
    nombre_archivo: str = Field(alias="nombreArchivo")
    tipo: str  # "pdf" | "jpg"

    model_config = ConfigDict(populate_by_name=True)


class PresignedPostData(BaseModel):
    url: str
    fields: dict[str, str]


class DocumentUploadURLResponse(BaseModel):
    presigned_post: PresignedPostData = Field(alias="presignedPost")
    object_key: str = Field(alias="objectKey")

    model_config = ConfigDict(populate_by_name=True)


class SaveDocumentRequest(BaseModel):
    nombre_archivo: str = Field(alias="nombreArchivo")
    object_key: str = Field(alias="objectKey")
    tipo: str  # "pdf" | "jpg"

    model_config = ConfigDict(populate_by_name=True)


class OrgDocumentDTO(BaseModel):
    id: str
    nombre_archivo: str = Field(alias="nombreArchivo")
    tipo: str
    url: str  # presigned download URL (expires in 1 h)

    model_config = ConfigDict(populate_by_name=True)
