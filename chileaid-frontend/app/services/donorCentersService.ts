/**
 * MODEL — Acceso a datos del dominio centros/emergencias para el donante.
 *
 * Conectado al backend real vía `apiFetch` (endpoints públicos, sin token):
 *   getActiveEmergencies → `GET /emergencies?estado=activa`
 *   getAllCenters        → `GET /centers`
 *   getCriticalCenters   → `GET /centers?orden=cobertura_asc`
 *   getCenterDetail      → `GET /centers/{id}`
 *
 * El service es la ÚNICA capa que adapta el contrato: las necesidades del detalle
 * llegan en la forma unificada del backend (insumo ANIDADO + `urgencia` enum) y
 * aquí se aplanan a la `NeedDTO` plana (`urgente` booleano) que consumen las
 * vistas del donante. `cobertura` (0-100) = porcentaje de la meta cubierto;
 * NUNCA se llama "saturación".
 */
import { apiFetch } from '~/utils/apiFetch'

/** Tipo de evento catastrófico que origina una emergencia. */
export type EmergencyType = 'terremoto' | 'incendio' | 'aluvion' | 'otro'

/** Estado del ciclo de vida de una emergencia. */
export type EmergencyStatus = 'activa' | 'cerrada'

/** Estado operativo de un centro de acopio según su cobertura. */
export type CenterStatus = 'en_capacidad' | 'critico' | 'cerrado'

/**
 * Función del centro: si recibe donaciones físicas (`centro_acopio`), entrega
 * ayuda a personas (`punto_distribucion`) o ambas (`ambos`). Coincide con la
 * unión `TipoCentro` del registro de organización.
 */
export type CenterType = 'centro_acopio' | 'punto_distribucion' | 'ambos'

/**
 * Emergencia: evento catastrófico activo que agrupa varios centros de acopio.
 * `cobertura` es el promedio agregado de la cobertura de sus centros.
 */
export interface EmergencyDTO {
  id: string
  nombre: string
  tipo: EmergencyType
  zona: string
  fechaInicio: string
  estado: EmergencyStatus
  totalCentros: number
  cobertura: number
}

/**
 * Centro de acopio. `cobertura` (0-100) indica el porcentaje de la meta ya
 * cubierto; `estado` es la saturación derivada. `zona` es la comuna que se
 * muestra en la tarjeta; `region` (de la organización dueña) alimenta el filtro
 * del listado. `emergenciaId`/`tipoEmergencia`/`emergenciaNombre` son `null` si el
 * centro no está vinculado a una emergencia. `emergenciaNombre` es el nombre
 * específico del evento (p. ej. "Incendio Victoria"): el donante lo necesita para
 * distinguir dos emergencias del mismo tipo, no solo el tipo genérico.
 */
export interface CenterDTO {
  id: string
  nombre: string
  organizacion: string
  zona: string
  region: string
  cobertura: number
  estado: CenterStatus
  emergenciaId: string | null
  tipoEmergencia: EmergencyType | null
  emergenciaNombre: string | null
  tipoCentro: CenterType
  necesidadesUrgentes: string[]
  direccion: string
  latitud: number
  longitud: number
}

/**
 * Filtros del listado completo de centros (`/donor/centers`). Ambos actúan en
 * AND. `region === 'Todas las regiones'` y `tipoEmergencia === 'todas'` son los
 * valores neutros que no filtran.
 */
export interface CenterFilters {
  region: string
  tipoEmergencia: 'todas' | EmergencyType
}

/** Estado de una necesidad concreta de un centro. */
export type NeedStatus = 'activa' | 'completada'

/**
 * Necesidad concreta de un centro de acopio (un ítem donable), en forma plana
 * para las vistas del donante. `cobertura` (0-100) = porcentaje ya comprometido;
 * `urgente` marca los ítems críticos que se destacan en el detalle.
 */
export interface NeedDTO {
  id: string
  nombre: string
  categoria: string
  unidad: string
  cantidadRequerida: number
  cantidadComprometida: number
  cobertura: number
  urgente: boolean
  estado: NeedStatus
}

/**
 * Detalle completo de un centro (`/donor/center/:id`). Extiende el `CenterDTO`
 * del listado con datos operativos, la emergencia a la que pertenece (o `null`)
 * y el desglose de necesidades.
 */
export interface CenterDetailDTO extends CenterDTO {
  horario: string
  coordinador: string
  telefono: string
  emergencia: EmergencyDTO | null
  necesidades: NeedDTO[]
}

/**
 * Listado fijo de las 16 regiones de Chile (más la opción neutra). No proviene
 * de la API: es un catálogo estático que alimenta el selector de región.
 */
export { REGIONES_CHILE } from '~/services/donorDashboardService'

/**
 * Forma cruda de una necesidad del backend (`NeedDTO` de FastAPI): insumo
 * ANIDADO y `urgencia` como enum string. Se aplana a la `NeedDTO` del donante.
 */
interface ApiNeed {
  id: string
  insumo: { nombre: string; categoria: string; unidad: string }
  cantidadRequerida: number
  cantidadComprometida: number
  cantidadRecibida: number
  urgencia: 'alta' | 'media' | 'baja'
  estado: string
  cobertura: number
}

/** Forma cruda del detalle de centro del backend (`CenterDetailDTO` de FastAPI). */
interface ApiCenterDetail extends Omit<CenterDTO, 'region'> {
  region: string | null
  horario: string | null
  coordinador: string | null
  telefono: string | null
  emergencia: EmergencyDTO | null
  necesidades: ApiNeed[]
}

/** Aplana una necesidad anidada del backend a la `NeedDTO` plana del donante. */
function toNeedDTO(api: ApiNeed): NeedDTO {
  return {
    id: api.id,
    nombre: api.insumo.nombre,
    categoria: api.insumo.categoria,
    unidad: api.insumo.unidad,
    cantidadRequerida: api.cantidadRequerida,
    cantidadComprometida: api.cantidadComprometida,
    cobertura: api.cobertura,
    urgente: api.urgencia === 'alta',
    estado: api.estado === 'completada' ? 'completada' : 'activa'
  }
}

export const donorCentersService = {
  /**
   * Emergencias activas con sus agregados (`GET /emergencies?estado=activa`).
   * `cobertura`/`totalCentros` se calculan server-side.
   */
  async getActiveEmergencies(): Promise<EmergencyDTO[]> {
    return apiFetch<EmergencyDTO[]>('/emergencies', {
      query: { estado: 'activa' }
    })
  },

  /**
   * Centros más urgentes primero (`GET /centers?orden=cobertura_asc`): el backend
   * ordena ascendente por cobertura (los críticos encabezan).
   */
  async getCriticalCenters(): Promise<CenterDTO[]> {
    return apiFetch<CenterDTO[]>('/centers', {
      query: { orden: 'cobertura_asc' }
    })
  },

  /**
   * Colección completa de centros (`GET /centers`). El filtrado por región y
   * tipo de emergencia ocurre en el cliente (ViewModel), por eso se traen todos.
   */
  async getAllCenters(): Promise<CenterDTO[]> {
    return apiFetch<CenterDTO[]>('/centers')
  },

  /**
   * Detalle de un centro (`GET /centers/{id}`). Aplana las necesidades anidadas a
   * la forma plana del donante y normaliza los campos opcionales de contacto.
   */
  async getCenterDetail(id: string): Promise<CenterDetailDTO> {
    const api = await apiFetch<ApiCenterDetail>(`/centers/${id}`)
    return {
      ...api,
      region: api.region ?? '',
      horario: api.horario ?? '',
      coordinador: api.coordinador ?? '',
      telefono: api.telefono ?? '',
      necesidades: api.necesidades.map(toNeedDTO)
    }
  }
}
