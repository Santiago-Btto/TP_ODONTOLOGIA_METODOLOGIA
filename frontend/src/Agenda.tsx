import { useEffect, useState } from 'react'
import { ApiClient, ApiError, type Identidad, type TurnoAgenda } from './api/client'
import { fechaHoyLocal, periodo, type Vista } from './periodos'

function horario(fecha: string): string {
  return new Intl.DateTimeFormat('es-AR', { hour: '2-digit', minute: '2-digit' }).format(new Date(fecha))
}

function localDateString(fecha: string): string {
  const date = new Date(fecha)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function turnosTabla(turnos: TurnoAgenda[]) {
  if (!turnos.length) return null
  return <div className="table-scroll"><table>
    <thead><tr><th scope="col">Horario</th><th scope="col">Profesional</th><th scope="col">Box</th><th scope="col">Estado</th></tr></thead>
    <tbody>{turnos.map(item => <tr key={item.id}>
      <td>{horario(item.inicio)}–{horario(item.fin)}</td><td>{item.profesional_id}</td><td>{item.box_id}</td><td><span className={`badge badge-${item.estado}`}>{item.estado}</span></td>
    </tr>)}</tbody>
  </table></div>
}

export function Agenda({ api, actor, onUnauthorized, refresh }: { api: ApiClient; actor: Identidad; onUnauthorized: () => void; refresh: number }) {
  const [vista, setVista] = useState<Vista>('dia')
  const [fecha, setFecha] = useState(fechaHoyLocal)
  const [profesional, setProfesional] = useState('')
  const [box, setBox] = useState('')
  const [retry, setRetry] = useState(0)
  const [turnos, setTurnos] = useState<TurnoAgenda[] | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let active = true
    if (actor.rol === 'odontologo' && !actor.profesional_id) {
      setTurnos(null)
      setError('El odontólogo no tiene un profesional asignado. Consultá con administración.')
      return
    }
    const { inicio, fin } = periodo(fecha, vista)
    setLoading(true)
    setError('')
    setTurnos(null)
    void api.agenda({ inicio, fin, profesional_id: actor.rol === 'odontologo' ? actor.profesional_id ?? undefined : profesional.trim() || undefined, box_id: box.trim() || undefined })
      .then(result => { if (active) setTurnos(result) })
      .catch(cause => {
        if (!active) return
        if (cause instanceof ApiError && cause.status === 401) onUnauthorized()
        else setError(cause instanceof Error ? cause.message : 'No se pudo cargar la agenda.')
      }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [api, actor, fecha, vista, profesional, box, retry, refresh])

  const dias = periodo(fecha, vista).dias
  return <section className="card" aria-labelledby="agenda-title">
    <div className="card-heading"><div><p className="eyebrow">PLANIFICACIÓN</p><h2 id="agenda-title">Próximos turnos</h2></div><button type="button" className="button-secondary" onClick={() => setRetry(value => value + 1)}>Actualizar agenda</button></div>
    <div className="toolbar">
      <div className="segmented" aria-label="Vista"><button type="button" aria-pressed={vista === 'dia'} onClick={() => setVista('dia')}>Día</button><button type="button" aria-pressed={vista === 'semana'} onClick={() => setVista('semana')}>Semana</button></div>
      <label>Fecha<input type="date" value={fecha} onChange={event => { if (event.target.value) setFecha(event.target.value) }} /></label>
      {actor.rol !== 'odontologo' && <label>Filtrar profesional<input value={profesional} onChange={event => setProfesional(event.target.value)} placeholder="prof-demo" maxLength={64} /></label>}
      <label>Filtrar box<input value={box} onChange={event => setBox(event.target.value)} placeholder="box-demo" maxLength={64} /></label>
    </div>
    {loading && <p role="status" className="muted">Cargando agenda…</p>}
    {error && <div className="error-box"><p role="alert">{error}</p><button type="button" className="button-secondary" onClick={() => setRetry(value => value + 1)}>Reintentar</button></div>}
    {!loading && !error && turnos && <>
      {!turnos.length && <p className="empty-state">No hay turnos en este período.</p>}
      {vista === 'dia' ? turnosTabla(turnos) : <div className="week-grid">{dias.map(dia => <section key={dia} data-testid="dia-semana" className="week-day">
        <h3>{new Intl.DateTimeFormat('es-AR', { weekday: 'long', day: 'numeric', month: 'short' }).format(new Date(`${dia}T12:00:00`))}</h3>
        {turnosTabla(turnos.filter(item => localDateString(item.inicio) === dia)) || <p className="muted">Sin turnos</p>}
      </section>)}</div>}
    </>}
  </section>
}
