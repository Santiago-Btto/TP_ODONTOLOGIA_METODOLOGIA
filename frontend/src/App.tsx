import { useState, type FormEvent } from 'react'
import { ApiClient, type Identidad } from './api/client'
import { Agenda } from './Agenda'
import { Gestion } from './Gestion'
import { zonaHorariaLocal } from './periodos'

export function App({ api }: { api?: ApiClient }) {
  const [client] = useState(() => api ?? new ApiClient())
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [identity, setIdentity] = useState<Identidad | null>(null)
  const [authError, setAuthError] = useState('')
  const [loggingIn, setLoggingIn] = useState(false)
  const [refresh, setRefresh] = useState(0)

  function salir(message = '') {
    client.setToken(null)
    setIdentity(null)
    setAuthError(message)
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoggingIn(true)
    setAuthError('')
    try {
      const token = await client.login(username, password)
      client.setToken(token.access_token)
      const actor = await client.me()
      setPassword('')
      setIdentity(actor)
    } catch (error) {
      client.setToken(null)
      setAuthError(error instanceof Error ? error.message : 'No se pudo iniciar sesión.')
    } finally { setLoggingIn(false) }
  }

  if (!identity) return <main className="login-layout"><section className="login-card">
    <div className="brand-mark" aria-hidden="true">✳</div>
    <p className="eyebrow">CONSULTORIO · AGENDA</p>
    <h1>Agenda odontológica</h1>
    <p className="muted">Ingresá con tu usuario autorizado para consultar y gestionar turnos.</p>
    {authError && <p role="alert" className="error-box">{authError}</p>}
    <form onSubmit={submit} className="stack">
      <label>Usuario<input autoComplete="username" value={username} onChange={event => setUsername(event.target.value)} required /></label>
      <label>Contraseña<input type="password" autoComplete="current-password" value={password} onChange={event => setPassword(event.target.value)} required /></label>
      <button type="submit" disabled={loggingIn}>{loggingIn ? 'Ingresando…' : 'Ingresar'}</button>
    </form>
    <p className="footnote">Los datos demo son ficticios. La sesión se cierra al recargar la página.</p>
  </section></main>

  const puedeGestionar = identity.rol === 'recepcion' || identity.rol === 'responsable'
  return <div className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark small" aria-hidden="true">✳</span>Agenda odontológica</div><div className="identity"><span>{identity.nombre_usuario} <small>· {identity.rol}</small></span><button type="button" className="button-quiet" onClick={() => salir()}>Cerrar sesión</button></div></header>
    <main className="content"><div className="page-heading"><div><p className="eyebrow">PANEL DE TURNOS</p><h1>Agenda</h1><p className="muted">Horarios desde la API · Zona horaria del dispositivo: <strong>{zonaHorariaLocal()}</strong>.</p></div></div>
      <Agenda api={client} actor={identity} onUnauthorized={() => salir('La sesión venció. Ingresá nuevamente.')} refresh={refresh} />
      {puedeGestionar && <Gestion api={client} onUnauthorized={() => salir('La sesión venció. Ingresá nuevamente.')} onCreated={() => setRefresh(previous => previous + 1)} />}
    </main>
  </div>
}
