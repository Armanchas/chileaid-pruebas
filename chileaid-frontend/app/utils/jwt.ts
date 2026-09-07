/**
 * Helper de JWT (solo lectura del payload).
 *
 * El frontend NO valida la firma del token (eso es responsabilidad del backend):
 * únicamente decodifica el payload (segunda parte del JWT, base64url) para leer
 * claims como `role` u `organization_id`. Nunca lanza: ante cualquier problema
 * devuelve `null` para que el llamador decida el fallback.
 */

/**
 * Decodifica el payload de un JWT y lo devuelve como objeto plano. Retorna `null`
 * si el token está malformado o el payload no es un objeto JSON válido.
 */
export function decodeJwtPayload(token: string): Record<string, unknown> | null {
  try {
    const payloadSegment = token.split('.')[1]
    if (!payloadSegment) return null

    // base64url → base64 + padding para que el decodificador lo acepte.
    const base64 = payloadSegment.replace(/-/g, '+').replace(/_/g, '/')
    const padded = base64.padEnd(
      base64.length + ((4 - (base64.length % 4)) % 4),
      '='
    )

    const parsed: unknown = JSON.parse(base64ToUtf8(padded))
    return typeof parsed === 'object' && parsed !== null
      ? (parsed as Record<string, unknown>)
      : null
  } catch {
    return null
  }
}

/** Decodifica base64 a string UTF-8, tanto en el cliente (atob) como en SSR (Buffer). */
function base64ToUtf8(base64: string): string {
  if (typeof atob === 'function') {
    const binary = atob(base64)
    const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0))
    return new TextDecoder().decode(bytes)
  }
  return Buffer.from(base64, 'base64').toString('utf-8')
}
