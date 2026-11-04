import { useState, type FormEvent } from 'react'
import { ApiClient, ApiError, type Paciente, type TurnoCreado } from './api/client'
import { fechaLocalAISO } from './periodos'

export function Gestion({ api, onUnauthorized, onCreated }: { api: ApiClient; onUnauthorized: () => void; onCreated: () => void }) {
  const [buscar, setBuscar] = useState('')
  const [pacientes, setPacientes] = useState<Paciente[]>([])
  const [pacientesError, setPacientesError] = useState('')
  const [nombre, setNombre] = useState('')
  const [contacto, setContacto] = useState('')
  const [seleccionado, setSeleccionado] = useState<Paciente | null>(null)
  const [profesional, setProfesional] = useState('')
  const [box, setBox] = useState('')
  const [prestacion, setPrestacion] = useState('')
  const [inicio, setInicio] = useState('')
  const [fin, setFin] = useState('')
  const [turnoError, setTurnoError] = useState('')
  const [turnoCreado, setTurnoCreado] = useState<TurnoCreado | null>(null)

  function mostrarError(error: unknown): string {
    if (error instanceof ApiError && error.status === 401) onUnauthorized()
    return error instanceof Error ? error.message : 'Ocurrió un error inesperado.'
  }

  async function consultarPacientes(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setPacientesError('')
    try { setPacientes(await api.searchPatients(buscar.trim())) }
    catch (error) { setPacientesError(mostrarError(error)) }
  }

  async function registrarPaciente(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setPacientesError('')
    try {
      const paciente = await api.createPatient(nombre.trim(), contacto.trim() || null)
      setSeleccionado(paciente)
      setPacientes(previous => [paciente, ...previous.filter(item => item.id !== paciente.id)])
    } catch (error) { setPacientesError(mostrarError(error)) }
  }

  async function crearTurno(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setTurnoError('')
    setTurnoCreado(null)
    if (!seleccionado) { setTurnoError('Seleccioná un paciente primero.'); return }
    const inicioISO = fechaLocalAISO(inicio)
    const finISO = fin ? fechaLocalAISO(fin) : null
    if (!inicioISO || (fin && !finISO)) { setTurnoError('Indicá fechas válidas.'); return }
    try {
      const result = await api.createAppointment({
        paciente_id: seleccionado.id, profesional_id: profesional.trim(), box_id: box.trim(),
        prestacion_id: prestacion.trim(), inicio: inicioISO, ...(finISO ? { fin: finISO } : {}),
      })
      setTurnoCreado(result)
      onCreated()
    } catch (error) { setTurnoError(mostrarError(error)) }
  }

  return <div className="management-grid">
    <section className="card" aria-labelledby="patients-title"><p className="eyebrow">PASO 1</p><h2 id="patients-title">Pacientes</h2><p className="muted">Buscá o registrá un paciente con datos mínimos.</p>
      <form onSubmit={consultarPacientes} className="inline-form"><label>Buscar paciente<input value={buscar} onChange={event => setBuscar(event.target.value)} placeholder="Nombre o contacto" /></label><button type="submit" className="button-secondary">Buscar</button></form>
      {pacientes.length > 0 && <ul className="patient-results">{pacientes.map(patient => <li key={patient.id}><span>{patient.nombre_mostrado}<small>{patient.contacto}</small></span><button type="button" className="button-secondary" onClick={() => setSeleccionado(patient)}>Elegir {patient.nombre_mostrado}</button></li>)}</ul>}
      <form onSubmit={registrarPaciente} className="stack divided"><label>Nombre del paciente<input value={nombre} onChange={event => setNombre(event.target.value)} required maxLength={200} placeholder="Paciente Demo" /></label><label>Contacto opcional<input value={contacto} onChange={event => setContacto(event.target.value)} maxLength={200} placeholder="demo@example.invalid" /></label><button type="submit">Registrar paciente</button></form>
      {pacientesError && <p role="alert" className="error-box">{pacientesError}</p>}
      {seleccionado && <p className="selection">Paciente seleccionado: {seleccionado.nombre_mostrado} <small>({seleccionado.id})</small></p>}
    </section>
    <section className="card" aria-labelledby="create-title"><p className="eyebrow">PASO 2</p><h2 id="create-title">Nuevo turno</h2><p className="muted">La disponibilidad se verifica al crear el turno.</p>
      <form onSubmit={crearTurno} className="stack"><label>Profesional para turno<input value={profesional} onChange={event => setProfesional(event.target.value)} required maxLength={64} placeholder="prof-demo" /></label><label>Box para turno<input value={box} onChange={event => setBox(event.target.value)} required maxLength={64} placeholder="box-demo" /></label><label>Prestación<input value={prestacion} onChange={event => setPrestacion(event.target.value)} required maxLength={64} placeholder="prest-demo" /></label><div className="two-columns"><label>Inicio del turno<input type="datetime-local" value={inicio} onChange={event => setInicio(event.target.value)} required /></label><label>Fin opcional<input type="datetime-local" value={fin} onChange={event => setFin(event.target.value)} /></label></div><button type="submit" disabled={!seleccionado}>Crear turno</button></form>
      {!seleccionado && <p className="hint">Seleccioná un paciente para habilitar el alta.</p>}
      {turnoError && <p role="alert" className="error-box">{turnoError}</p>}
      {turnoCreado && <p role="status" className="success-box">Turno creado: {turnoCreado.id}. La agenda se está actualizando.</p>}
    </section>
  </div>
}
