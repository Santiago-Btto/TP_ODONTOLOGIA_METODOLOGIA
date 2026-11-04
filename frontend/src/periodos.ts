export type Vista = 'dia' | 'semana'

function componentes(fecha: string): [number, number, number] {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(fecha)
  if (!match) throw new Error('Fecha inválida')
  const year = Number(match[1]); const month = Number(match[2]); const day = Number(match[3])
  const value = new Date(year, month - 1, day)
  if (value.getFullYear() !== year || value.getMonth() !== month - 1 || value.getDate() !== day) {
    throw new Error('Fecha inválida')
  }
  return [year, month, day]
}

function localDateString(date: Date): string {
  return [String(date.getFullYear()).padStart(4, '0'), String(date.getMonth() + 1).padStart(2, '0'), String(date.getDate()).padStart(2, '0')].join('-')
}

export function fechaHoyLocal(): string { return localDateString(new Date()) }

export function periodo(fecha: string, vista: Vista): { inicio: string; fin: string; dias: string[] } {
  const [year, month, day] = componentes(fecha)
  const selected = new Date(year, month - 1, day)
  const mondayOffset = (selected.getDay() + 6) % 7
  const start = vista === 'semana' ? new Date(year, month - 1, day - mondayOffset) : selected
  const count = vista === 'semana' ? 7 : 1
  const end = new Date(start.getFullYear(), start.getMonth(), start.getDate() + count)
  const dias = Array.from({ length: count }, (_, index) => localDateString(new Date(start.getFullYear(), start.getMonth(), start.getDate() + index)))
  return { inicio: start.toISOString(), fin: end.toISOString(), dias }
}

export function fechaLocalAISO(value: string): string | null {
  const match = /^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})$/.exec(value)
  if (!match) return null
  try {
    const [year, month, day] = componentes(match[1])
    const hour = Number(match[2]); const minute = Number(match[3])
    if (hour > 23 || minute > 59) return null
    const date = new Date(year, month - 1, day, hour, minute)
    if (date.getFullYear() !== year || date.getMonth() !== month - 1 || date.getDate() !== day || date.getHours() !== hour || date.getMinutes() !== minute) return null
    return date.toISOString()
  } catch { return null }
}

export function zonaHorariaLocal(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || 'zona local del dispositivo'
}
