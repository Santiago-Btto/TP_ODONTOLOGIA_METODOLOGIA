import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ApiClient, ApiError, type Identidad, type TurnoAgenda } from './api/client'
import { App } from './App'

const recepcion: Identidad = { id: 'u1', nombre_usuario: 'Recepción Demo', rol: 'recepcion', profesional_id: null }
const odontologo: Identidad = { id: 'u2', nombre_usuario: 'Odontólogo Demo', rol: 'odontologo', profesional_id: 'prof-demo' }
const turno: TurnoAgenda = { id: 't1', profesional_id: 'prof-demo', box_id: 'box-demo', inicio: '2026-11-03T12:00:00Z', fin: '2026-11-03T12:30:00Z', estado: 'reservado' }

function cliente(actor: Identidad = recepcion, turnos: TurnoAgenda[] = []): ApiClient {
  const api = new ApiClient()
  vi.spyOn(api, 'login').mockResolvedValue({ access_token: 'token-demo', token_type: 'bearer', expires_in: 1800 })
  vi.spyOn(api, 'me').mockResolvedValue(actor)
  vi.spyOn(api, 'agenda').mockResolvedValue(turnos)
  vi.spyOn(api, 'searchPatients').mockResolvedValue([])
  return api
}

async function ingresar(api: ApiClient): Promise<ReturnType<typeof userEvent.setup>> {
  const user = userEvent.setup()
  render(<App api={api} />)
  await user.type(screen.getByLabelText('Usuario'), 'recepcion-demo')
  await user.type(screen.getByLabelText('Contraseña'), 'clave')
  await user.click(screen.getByRole('button', { name: 'Ingresar' }))
  await screen.findByText(/Recepción Demo|Odontólogo Demo/)
  return user
}

test('muestra el acceso sin datos de agenda antes de iniciar sesión', () => {
  render(<App />)
  expect(screen.getByRole('heading', { name: /agenda odontológica/i })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: /ingresar/i })).toBeInTheDocument()
  expect(screen.queryByText(/próximos turnos/i)).not.toBeInTheDocument()
})

test('login correcto obtiene identidad, agenda y cierre limpia datos', async () => {
  const api = cliente(recepcion, [turno])
  const user = await ingresar(api)
  await screen.findByText('prof-demo')
  expect(api.getToken()).toBe('token-demo')
  expect(screen.getByText(/recepcion/i)).toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: 'Cerrar sesión' }))
  expect(screen.getByRole('button', { name: 'Ingresar' })).toBeInTheDocument()
  expect(screen.queryByText('prof-demo')).not.toBeInTheDocument()
  expect(api.getToken()).toBeNull()
})

test('credenciales inválidas muestran error sin agenda', async () => {
  const api = cliente()
  vi.mocked(api.login).mockRejectedValue(new ApiError(401, 'Credenciales inválidas'))
  const user = userEvent.setup()
  render(<App api={api} />)
  await user.type(screen.getByLabelText('Usuario'), 'demo')
  await user.type(screen.getByLabelText('Contraseña'), 'mala')
  await user.click(screen.getByRole('button', { name: 'Ingresar' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Credenciales inválidas')
  expect(screen.queryByText('Próximos turnos')).not.toBeInTheDocument()
})

test('401 de agenda retira datos protegidos y solicita nuevo login', async () => {
  const api = cliente(recepcion, [turno])
  const user = await ingresar(api)
  await screen.findByText('prof-demo')
  vi.mocked(api.agenda).mockRejectedValue(new ApiError(401, 'Token expirado'))
  await user.click(screen.getByRole('button', { name: 'Actualizar agenda' }))
  expect(await screen.findByRole('button', { name: 'Ingresar' })).toBeInTheDocument()
  expect(screen.queryByText('prof-demo')).not.toBeInTheDocument()
})

test('vista semanal muestra siete días y estado vacío', async () => {
  const api = cliente()
  const user = await ingresar(api)
  await user.click(screen.getByRole('button', { name: 'Semana' }))
  expect(await screen.findByText(/No hay turnos en este período/i)).toBeInTheDocument()
  expect(screen.getAllByTestId('dia-semana')).toHaveLength(7)
  expect(vi.mocked(api.agenda).mock.calls.at(-1)?.[0].inicio).toContain('T')
})

test('borrar momentáneamente la fecha no rompe la agenda', async () => {
  const api = cliente()
  await ingresar(api)
  const calls = vi.mocked(api.agenda).mock.calls.length
  fireEvent.change(screen.getByLabelText('Fecha'), { target: { value: '' } })
  expect(screen.getByRole('heading', { name: 'Próximos turnos' })).toBeInTheDocument()
  expect(vi.mocked(api.agenda).mock.calls).toHaveLength(calls)
})

test('filtros combinados y retry envían datos a la API', async () => {
  const api = cliente()
  vi.mocked(api.agenda).mockRejectedValueOnce(new ApiError(0, 'Sin conexión'))
  const user = await ingresar(api)
  expect(await screen.findByRole('alert')).toHaveTextContent('Sin conexión')
  await user.click(screen.getByRole('button', { name: 'Reintentar' }))
  await user.type(screen.getByLabelText('Filtrar profesional'), 'prof-demo')
  await user.type(screen.getByLabelText('Filtrar box'), 'box-demo')
  await waitFor(() => expect(vi.mocked(api.agenda).mock.calls.at(-1)?.[0]).toMatchObject({ profesional_id: 'prof-demo', box_id: 'box-demo' }))
})

test('odontólogo consulta sólo su profesional y no ve alta ni padrón', async () => {
  const api = cliente(odontologo)
  const user = await ingresar(api)
  await waitFor(() => expect(api.agenda).toHaveBeenCalled())
  expect(vi.mocked(api.agenda).mock.calls[0][0].profesional_id).toBe('prof-demo')
  expect(screen.queryByLabelText('Filtrar profesional')).not.toBeInTheDocument()
  expect(screen.queryByRole('button', { name: 'Registrar paciente' })).not.toBeInTheDocument()
  expect(screen.queryByRole('button', { name: 'Crear turno' })).not.toBeInTheDocument()
  await user.type(screen.getByLabelText('Filtrar box'), 'box-demo')
  await waitFor(() => expect(vi.mocked(api.agenda).mock.calls.at(-1)?.[0]).toMatchObject({ profesional_id: 'prof-demo', box_id: 'box-demo' }))
})

test('paciente nuevo se selecciona y un duplicado no reemplaza selección', async () => {
  const api = cliente()
  const patient = { id: 'pac-demo', nombre_mostrado: 'Paciente Demo', contacto: 'demo@example.invalid' }
  vi.spyOn(api, 'createPatient').mockResolvedValueOnce(patient).mockRejectedValueOnce(new ApiError(409, 'Contacto duplicado'))
  const user = await ingresar(api)
  await user.type(screen.getByLabelText('Nombre del paciente'), 'Paciente Demo')
  await user.type(screen.getByLabelText('Contacto opcional'), 'demo@example.invalid')
  await user.click(screen.getByRole('button', { name: 'Registrar paciente' }))
  expect(await screen.findByText(/Paciente seleccionado: Paciente Demo/)).toBeInTheDocument()
  await user.click(screen.getByRole('button', { name: 'Registrar paciente' }))
  expect(await screen.findByRole('alert')).toHaveTextContent('Contacto duplicado')
  expect(screen.getByText(/Paciente seleccionado: Paciente Demo/)).toBeInTheDocument()
})

test('búsqueda de paciente permite seleccionar ID devuelto', async () => {
  const api = cliente()
  vi.mocked(api.searchPatients).mockResolvedValue([{ id: 'pac2', nombre_mostrado: 'Paciente Demo Dos', contacto: null }])
  const user = await ingresar(api)
  await user.type(screen.getByLabelText('Buscar paciente'), 'Demo Dos')
  await user.click(screen.getByRole('button', { name: 'Buscar' }))
  await user.click(await screen.findByRole('button', { name: /Elegir Paciente Demo Dos/i }))
  expect(screen.getByText(/Paciente seleccionado: Paciente Demo Dos/)).toBeInTheDocument()
})

test.each([409, 422])('alta rechazada %i conserva formulario y muestra causa', async (status) => {
  const api = cliente()
  const patient = { id: 'pac-demo', nombre_mostrado: 'Paciente Demo', contacto: null }
  vi.spyOn(api, 'createPatient').mockResolvedValue(patient)
  vi.spyOn(api, 'createAppointment').mockRejectedValue(new ApiError(status, `Causa ${status}`))
  const user = await ingresar(api)
  await user.type(screen.getByLabelText('Nombre del paciente'), 'Paciente Demo')
  await user.click(screen.getByRole('button', { name: 'Registrar paciente' }))
  await screen.findByText(/Paciente seleccionado/)
  await user.type(screen.getByLabelText('Profesional para turno'), 'prof-demo')
  await user.type(screen.getByLabelText('Box para turno'), 'box-demo')
  await user.type(screen.getByLabelText('Prestación'), 'prest-demo')
  await user.type(screen.getByLabelText('Inicio del turno'), '2026-11-04T09:00')
  await user.click(screen.getByRole('button', { name: 'Crear turno' }))
  expect(await screen.findByRole('alert')).toHaveTextContent(`Causa ${status}`)
  expect(screen.getByLabelText('Profesional para turno')).toHaveValue('prof-demo')
  expect(vi.mocked(api.agenda).mock.calls).toHaveLength(1)
})

test('alta válida confirma y reconsulta agenda', async () => {
  const api = cliente()
  vi.spyOn(api, 'createPatient').mockResolvedValue({ id: 'pac-demo', nombre_mostrado: 'Paciente Demo', contacto: null })
  const appointment = { ...turno, id: 'turno-nuevo', paciente_id: 'pac-demo', prestacion_id: 'prest-demo' }
  vi.spyOn(api, 'createAppointment').mockResolvedValue(appointment)
  const user = await ingresar(api)
  await user.type(screen.getByLabelText('Nombre del paciente'), 'Paciente Demo')
  await user.click(screen.getByRole('button', { name: 'Registrar paciente' }))
  await screen.findByText(/Paciente seleccionado/)
  await user.type(screen.getByLabelText('Profesional para turno'), 'prof-demo')
  await user.type(screen.getByLabelText('Box para turno'), 'box-demo')
  await user.type(screen.getByLabelText('Prestación'), 'prest-demo')
  await user.type(screen.getByLabelText('Inicio del turno'), '2026-11-04T09:00')
  await user.click(screen.getByRole('button', { name: 'Crear turno' }))
  expect(await screen.findByText(/Turno creado: turno-nuevo/)).toBeInTheDocument()
  await waitFor(() => expect(api.agenda).toHaveBeenCalledTimes(2))
  expect(vi.mocked(api.createAppointment).mock.calls[0][0]).toMatchObject({ paciente_id: 'pac-demo', profesional_id: 'prof-demo' })
})
