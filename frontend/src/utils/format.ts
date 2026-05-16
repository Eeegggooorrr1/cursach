const EMPTY_VALUE = '-'

export function formatDate(value: string | null | undefined) {
  if (!value) {
    return EMPTY_VALUE
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export function formatPercent(value: number | null | undefined, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return EMPTY_VALUE
  }

  return `${Number(value).toFixed(digits)}%`
}

export function formatRatioPercent(value: number | null | undefined, digits = 0) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return EMPTY_VALUE
  }

  return formatPercent(Number(value) * 100, digits)
}

export function formatDecimal(value: number | null | undefined, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return EMPTY_VALUE
  }

  return Number(value).toFixed(digits)
}

export function clampRatio(value: number | null | undefined) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return 0
  }
  return Math.max(0, Math.min(1, Number(value)))
}

export function ratioToPercent(value: number | null | undefined) {
  return clampRatio(value) * 100
}

export function statusTone(status: string) {
  const normalized = status.toLowerCase()
  if (normalized.includes('finished') || normalized.includes('done') || normalized.includes('complete') || normalized.includes('success')) {
    return 'pill--success'
  }
  if (normalized.includes('progress') || normalized.includes('process') || normalized.includes('running') || normalized.includes('active')) {
    return 'pill--warning'
  }
  if (normalized.includes('fail') || normalized.includes('error') || normalized.includes('cancel')) {
    return 'pill--danger'
  }
  return ''
}

export function formatStatusLabel(status: string) {
  const normalized = status.toLowerCase()

  if (normalized === 'finished') {
    return 'Завершен'
  }
  if (normalized === 'in_progress') {
    return 'В процессе'
  }
  if (normalized === 'active') {
    return 'Активен'
  }

  return status
}

export function formatDifficultyLabel(value: number) {
  switch (value) {
    case 0:
      return 'Базовая'
    case 1:
      return 'Средняя'
    case 2:
      return 'Продвинутая'
    default:
      return `Уровень ${value}`
  }
}
