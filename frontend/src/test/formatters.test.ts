import { describe, it, expect } from 'vitest'
import {
  formatCurrency,
  formatDate,
  formatRelativeDate,
  getScoreColor,
  getScoreLabel,
  formatPercent,
  formatNumber,
  truncate,
  getInitials,
  getStatusColor,
  getPriorityColor,
} from '../utils/formatters'

describe('formatCurrency', () => {
  it('formats a positive number as USD', () => {
    expect(formatCurrency(1000)).toBe('$1,000')
  })
  it('formats zero', () => {
    expect(formatCurrency(0)).toBe('$0')
  })
  it('formats large numbers with commas', () => {
    expect(formatCurrency(250000)).toBe('$250,000')
  })
  it('returns em dash for undefined', () => {
    expect(formatCurrency(undefined)).toBe('—')
  })
  it('returns em dash for null', () => {
    expect(formatCurrency(null)).toBe('—')
  })
})

describe('formatDate', () => {
  it('formats a valid ISO date string', () => {
    const result = formatDate('2024-01-15T10:00:00Z')
    expect(result).toMatch(/Jan 15, 2024/)
  })
  it('returns em dash for null', () => {
    expect(formatDate(null)).toBe('—')
  })
  it('returns em dash for undefined', () => {
    expect(formatDate(undefined)).toBe('—')
  })
  it('returns em dash for invalid date string', () => {
    expect(formatDate('not-a-date')).toBe('—')
  })
})

describe('getScoreColor', () => {
  it('returns hot color for score >= 70', () => {
    expect(getScoreColor(82)).toContain('red')
    expect(getScoreColor(70)).toContain('red')
  })
  it('returns warm color for score 40-69', () => {
    expect(getScoreColor(55)).toContain('yellow')
    expect(getScoreColor(40)).toContain('yellow')
  })
  it('returns cold color for score < 40', () => {
    expect(getScoreColor(25)).toContain('blue')
    expect(getScoreColor(0)).toContain('blue')
  })
  it('returns gray for undefined score', () => {
    expect(getScoreColor(undefined)).toContain('gray')
  })
})

describe('getScoreLabel', () => {
  it('labels high scores as HOT', () => {
    expect(getScoreLabel(90)).toBe('HOT')
    expect(getScoreLabel(70)).toBe('HOT')
  })
  it('labels medium scores as WARM', () => {
    expect(getScoreLabel(50)).toBe('WARM')
    expect(getScoreLabel(40)).toBe('WARM')
  })
  it('labels low scores as COLD', () => {
    expect(getScoreLabel(20)).toBe('COLD')
    expect(getScoreLabel(0)).toBe('COLD')
  })
  it('returns N/A for undefined', () => {
    expect(getScoreLabel(undefined)).toBe('N/A')
  })
})

describe('formatPercent', () => {
  it('formats a percentage with one decimal', () => {
    expect(formatPercent(66.7)).toBe('66.7%')
    expect(formatPercent(100)).toBe('100.0%')
  })
  it('returns em dash for null', () => {
    expect(formatPercent(null)).toBe('—')
  })
})

describe('formatNumber', () => {
  it('formats with commas', () => {
    expect(formatNumber(1234567)).toBe('1,234,567')
  })
  it('handles zero', () => {
    expect(formatNumber(0)).toBe('0')
  })
  it('returns em dash for null', () => {
    expect(formatNumber(null)).toBe('—')
  })
})

describe('truncate', () => {
  it('does not truncate short strings', () => {
    expect(truncate('hello', 10)).toBe('hello')
  })
  it('truncates long strings', () => {
    const long = 'a'.repeat(60)
    const result = truncate(long, 50)
    expect(result.length).toBeLessThan(60)
    expect(result.endsWith('…')).toBe(true)
  })
  it('returns empty string for undefined', () => {
    expect(truncate(undefined)).toBe('')
  })
})

describe('getInitials', () => {
  it('returns initials for full name', () => {
    expect(getInitials('John Doe')).toBe('JD')
  })
  it('returns single initial for single name', () => {
    expect(getInitials('Alice')).toBe('A')
  })
  it('returns ? for undefined', () => {
    expect(getInitials(undefined)).toBe('?')
  })
  it('handles multi-word names', () => {
    expect(getInitials('Mary Jane Watson')).toBe('MW')
  })
})

describe('getStatusColor', () => {
  it('returns a non-empty string for known statuses', () => {
    expect(getStatusColor('NEW')).toBeTruthy()
    expect(getStatusColor('QUALIFIED')).toBeTruthy()
    expect(getStatusColor('LOST')).toBeTruthy()
  })
  it('falls back to gray for unknown status', () => {
    expect(getStatusColor('UNKNOWN_STATUS')).toContain('gray')
  })
})

describe('getPriorityColor', () => {
  it('returns a non-empty string for known priorities', () => {
    expect(getPriorityColor('LOW')).toBeTruthy()
    expect(getPriorityColor('HIGH')).toBeTruthy()
    expect(getPriorityColor('URGENT')).toBeTruthy()
  })
  it('falls back to gray for unknown priority', () => {
    expect(getPriorityColor('EXTREME')).toContain('gray')
  })
})
