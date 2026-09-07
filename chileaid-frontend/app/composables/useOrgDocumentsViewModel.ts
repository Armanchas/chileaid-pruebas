import { ref } from 'vue'
import { orgDocumentService, type OrgDocumentDTO } from '~/services/orgDocumentService'
import { resolveDocumentTipo } from '~/utils/documentType'

/**
 * VIEW-MODEL — Estado reactivo para la sección de documentos de la organización.
 *
 * Orquesta el flujo de subida en dos pasos (presigned URL → S3 → guardar registro)
 * y mantiene la lista de documentos existentes.
 */
export function useOrgDocumentsViewModel() {
  const documents = ref<OrgDocumentDTO[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const isUploading = ref(false)
  const uploadError = ref<string | null>(null)
  const uploadSuccess = ref(false)

  async function loadDocuments(): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      documents.value = await orgDocumentService.listDocuments()
    } catch {
      error.value = 'No se pudieron cargar los documentos.'
    } finally {
      isLoading.value = false
    }
  }

  async function uploadDocument(file: File): Promise<void> {
    isUploading.value = true
    uploadError.value = null
    uploadSuccess.value = false

    const tipo = resolveDocumentTipo(file.name)
    if (!tipo) {
      uploadError.value = 'Solo se aceptan archivos PDF o JPG.'
      isUploading.value = false
      return
    }

    try {
      const { presignedPost, objectKey } = await orgDocumentService.getUploadUrl(file.name, tipo)
      await orgDocumentService.uploadToS3(presignedPost, file)
      const saved = await orgDocumentService.saveDocument(file.name, objectKey, tipo)
      documents.value.push(saved)
      uploadSuccess.value = true
    } catch (e) {
      uploadError.value =
        e instanceof Error ? e.message : 'No se pudo subir el documento. Inténtalo de nuevo.'
    } finally {
      isUploading.value = false
    }
  }

  return {
    documents,
    isLoading,
    error,
    isUploading,
    uploadError,
    uploadSuccess,
    loadDocuments,
    uploadDocument
  }
}
