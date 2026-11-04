import { periodo, fechaLocalAISO } from './periodos'

test('día usa medianoche local y fin exclusivo del día siguiente', () => {
  const result = periodo('2026-11-03', 'dia')
  expect(result.inicio).toBe(new Date(2026, 10, 3).toISOString())
  expect(result.fin).toBe(new Date(2026, 10, 4).toISOString())
  expect(result.dias).toEqual(['2026-11-03'])
})

test('semana cruza de mes lunes a lunes con siete días', () => {
  const result = periodo('2026-11-01', 'semana')
  expect(result.inicio).toBe(new Date(2026, 9, 26).toISOString())
  expect(result.fin).toBe(new Date(2026, 10, 2).toISOString())
  expect(result.dias).toHaveLength(7)
  expect(result.dias[0]).toBe('2026-10-26')
  expect(result.dias[6]).toBe('2026-11-01')
})

test('fecha de formulario se transforma en instante ISO con zona', () => {
  expect(fechaLocalAISO('2026-11-03T09:30')).toBe(new Date(2026, 10, 3, 9, 30).toISOString())
  expect(fechaLocalAISO('')).toBeNull()
})

test('rechaza fechas imposibles', () => {
  expect(() => periodo('2026-02-30', 'dia')).toThrow(/fecha/i)
  expect(fechaLocalAISO('2026-02-30T09:30')).toBeNull()
})
