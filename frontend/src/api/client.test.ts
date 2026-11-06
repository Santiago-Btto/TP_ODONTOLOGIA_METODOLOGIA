import { ApiClient, ApiError } from './client'

const identity = { id: 'u1', nombre_usuario: 'recepcion-demo', rol: 'recepcion', profesional_id: null }

test('login envía form-url-encoded y lee la identidad con Bearer', async () => {
  const fetcher = vi.fn<typeof fetch>()
    .mockResolvedValueOnce(new Response(JSON.stringify({ access_token: 'token-demo', token_type: 'bearer', expires_in: 1800 }), { status: 200 }))
    .mockResolvedValueOnce(new Response(JSON.stringify(identity), { status: 200 }))
  const client = new ApiClient(fetcher)
  const token = await client.login('recepcion-demo', 'clave ficticia')
  client.setToken(token.access_token)
  expect(await client.me()).toEqual(identity)
  expect(fetcher.mock.calls[0][0]).toBe('/api/v1/auth/token')
  expect(fetcher.mock.calls[0][1]?.body).toBe('username=recepcion-demo&password=clave+ficticia')
  expect(new Headers(fetcher.mock.calls[0][1]?.headers).get('Content-Type')).toBe('application/x-www-form-urlencoded')
  expect(new Headers(fetcher.mock.calls[1][1]?.headers).get('Authorization')).toBe('Bearer token-demo')
})

test('consulta agenda con filtros combinados y token', async () => {
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(new Response('[]', { status: 200 }))
  const client = new ApiClient(fetcher)
  client.setToken('test-token')
  await client.agenda({ inicio: '2026-11-03T00:00:00-03:00', fin: '2026-11-04T00:00:00-03:00', profesional_id: 'prof-demo', box_id: 'box-demo' })
  const url = new URL(String(fetcher.mock.calls[0][0]), 'http://localhost')
  expect(url.pathname).toBe('/api/v1/agenda')
  expect(url.searchParams.get('profesional_id')).toBe('prof-demo')
  expect(url.searchParams.get('box_id')).toBe('box-demo')
  expect(new Headers(fetcher.mock.calls[0][1]?.headers).get('Authorization')).toBe('Bearer test-token')
})

test.each([
  [409, { codigo: 'solapamiento', detalle: 'Box ocupado' }, 'Box ocupado'],
  [422, { detail: [{ loc: ['body', 'inicio'], msg: 'Fecha inválida', type: 'value_error' }] }, 'Fecha inválida'],
  [401, { codigo: 'token_invalido', detalle: 'Sesión vencida' }, 'Sesión vencida'],
])('convierte error HTTP %i en mensaje del servidor', async (status, body, message) => {
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify(body), { status }))
  const client = new ApiClient(fetcher)
  await expect(client.me()).rejects.toMatchObject({ status, message })
})

test('distingue fallo de red', async () => {
  const fetcher = vi.fn<typeof fetch>().mockRejectedValue(new TypeError('Failed to fetch'))
  await expect(new ApiClient(fetcher).me()).rejects.toMatchObject({ status: 0, message: expect.stringMatching(/conexión/i) })
})

test('borra el token al recibir 401 protegido', async () => {
  const fetcher = vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify({ detalle: 'Venció', codigo: 'no_autorizado' }), { status: 401 }))
  const expired = vi.fn()
  const client = new ApiClient(fetcher, expired)
  client.setToken('demo')
  await expect(client.me()).rejects.toBeInstanceOf(ApiError)
  expect(client.getToken()).toBeNull()
  expect(expired).toHaveBeenCalledOnce()
})

test('delega en fetch global sin perder contexto al instanciarse sin fetcher', async () => {
  const mockGlobalFetch = vi.fn<typeof fetch>().mockResolvedValue(new Response('[]', { status: 200 }))
  const originalFetch = globalThis.fetch
  globalThis.fetch = mockGlobalFetch
  try {
    const client = new ApiClient()
    await client.agenda({ inicio: '2026-11-03T00:00:00-03:00', fin: '2026-11-04T00:00:00-03:00' })
    expect(mockGlobalFetch).toHaveBeenCalledOnce()
  } finally {
    globalThis.fetch = originalFetch
  }
})
