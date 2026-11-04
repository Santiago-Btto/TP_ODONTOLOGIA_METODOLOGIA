export type Rol = 'recepcion' | 'responsable' | 'odontologo'

export interface Identidad {
  id: string
  nombre_usuario: string
  rol: Rol
  profesional_id: string | null
}

export interface TokenRespuesta {
  access_token: string
  token_type: string
  expires_in: number
}

export interface TurnoAgenda {
  id: string
  profesional_id: string
  box_id: string
  inicio: string
  fin: string
  estado: string
}

export interface TurnoCreado extends TurnoAgenda {
  paciente_id: string
  prestacion_id: string
}

export interface Paciente {
  id: string
  nombre_mostrado: string
  contacto: string | null
}

export interface NuevoTurno {
  paciente_id: string
  profesional_id: string
  box_id: string
  prestacion_id: string
  inicio: string
  fin?: string
}

export interface FiltrosAgenda {
  inicio: string
  fin: string
  profesional_id?: string
  box_id?: string
}

export class ApiError extends Error {
  constructor(public readonly status: number, message: string, public readonly codigo?: string) {
    super(message)
    this.name = 'ApiError'
  }
}

function messageFromError(body: unknown, status: number): { message: string; codigo?: string } {
  if (typeof body === 'object' && body !== null) {
    const object = body as Record<string, unknown>
    if (typeof object.detalle === 'string') {
      return { message: object.detalle, codigo: typeof object.codigo === 'string' ? object.codigo : undefined }
    }
    if (typeof object.detail === 'string') return { message: object.detail }
    if (Array.isArray(object.detail)) {
      const messages = object.detail
        .filter((item): item is { msg: string } => typeof item === 'object' && item !== null && 'msg' in item && typeof item.msg === 'string')
        .map(item => item.msg)
      if (messages.length) return { message: messages.join('; ') }
    }
  }
  return { message: `La solicitud falló (HTTP ${status}).` }
}

export class ApiClient {
  private token: string | null = null

  constructor(private readonly fetcher: typeof fetch = fetch, private readonly onUnauthorized: () => void = () => {}) {}

  setToken(token: string | null): void { this.token = token }
  getToken(): string | null { return this.token }

  async login(username: string, password: string): Promise<TokenRespuesta> {
    const body = new URLSearchParams({ username, password }).toString()
    return this.request<TokenRespuesta>('/api/v1/auth/token', {
      method: 'POST', body, headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    }, false)
  }

  me(): Promise<Identidad> { return this.request<Identidad>('/api/v1/auth/yo') }

  agenda(filters: FiltrosAgenda): Promise<TurnoAgenda[]> {
    const query = new URLSearchParams({ inicio: filters.inicio, fin: filters.fin })
    if (filters.profesional_id) query.set('profesional_id', filters.profesional_id)
    if (filters.box_id) query.set('box_id', filters.box_id)
    return this.request<TurnoAgenda[]>(`/api/v1/agenda?${query.toString()}`)
  }

  searchPatients(q: string): Promise<Paciente[]> {
    return this.request<Paciente[]>(`/api/v1/pacientes?q=${encodeURIComponent(q)}`)
  }

  createPatient(nombre_mostrado: string, contacto: string | null): Promise<Paciente> {
    return this.request<Paciente>('/api/v1/pacientes', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre_mostrado, contacto }),
    })
  }

  createAppointment(turno: NuevoTurno): Promise<TurnoCreado> {
    return this.request<TurnoCreado>('/api/v1/turnos', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(turno),
    })
  }

  private async request<T>(url: string, options: RequestInit = {}, protectedRoute = true): Promise<T> {
    const headers = new Headers(options.headers)
    if (protectedRoute && this.token) headers.set('Authorization', `Bearer ${this.token}`)
    let response: Response
    try {
      response = await this.fetcher(url, { ...options, headers })
    } catch {
      throw new ApiError(0, 'No se pudo establecer conexión con el servidor. Reintentá.')
    }
    if (!response.ok) {
      let body: unknown
      try { body = await response.json() } catch { body = null }
      const { message, codigo } = messageFromError(body, response.status)
      if (protectedRoute && response.status === 401) {
        this.token = null
        this.onUnauthorized()
      }
      throw new ApiError(response.status, message, codigo)
    }
    return response.json() as Promise<T>
  }
}
