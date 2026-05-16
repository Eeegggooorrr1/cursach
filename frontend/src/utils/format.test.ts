import { describe, expect, it } from 'vitest'
import {
  clampRatio,
  formatDecimal,
  formatPercent,
  formatRatioPercent,
  ratioToPercent,
  statusTone,
} from './format'

describe('format utilities', () => {
  it('formats percentage-like values and falls back for empty values', () => {
    expect(formatPercent(42.49)).toBe('42%')
    expect(formatPercent(42.49, 1)).toBe('42.5%')
    expect(formatPercent(null)).toBe('-')
    expect(formatPercent(Number.NaN)).toBe('-')
  })

  it('formats ratio values as percentages', () => {
    expect(formatRatioPercent(0.755)).toBe('76%')
    expect(formatRatioPercent(0.755, 1)).toBe('75.5%')
    expect(formatRatioPercent(undefined)).toBe('-')
  })

  it('formats decimals and clamps ratios to the supported range', () => {
    expect(formatDecimal(1.234)).toBe('1.23')
    expect(formatDecimal(1.234, 1)).toBe('1.2')
    expect(clampRatio(-1)).toBe(0)
    expect(clampRatio(2)).toBe(1)
    expect(ratioToPercent(0.42)).toBe(42)
  })

  it('maps common status names to visual tones', () => {
    expect(statusTone('finished')).toBe('pill--success')
    expect(statusTone('in_progress')).toBe('pill--warning')
    expect(statusTone('error')).toBe('pill--danger')
    expect(statusTone('unknown')).toBe('')
  })
})
