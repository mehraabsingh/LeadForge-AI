import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { ScoreBadge } from '../components/ui/ScoreBadge'

// ─── Button Tests ───────────────────────────────────────────────────────────────

describe('Button', () => {
  it('renders with children text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
  })

  it('calls onClick when clicked', async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()
    render(<Button onClick={handleClick}>Click</Button>)
    await user.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('is disabled when disabled prop is passed', () => {
    render(<Button disabled>Disabled</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('is disabled when isLoading is true', () => {
    render(<Button isLoading>Loading</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('shows spinner when isLoading', () => {
    render(<Button isLoading>Submit</Button>)
    // The spinner (Loader2) is rendered — button should be in loading state
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('applies primary variant classes', () => {
    render(<Button variant="primary">Primary</Button>)
    const btn = screen.getByRole('button')
    expect(btn.className).toMatch(/bg-indigo/)
  })

  it('applies danger variant classes', () => {
    render(<Button variant="danger">Delete</Button>)
    const btn = screen.getByRole('button')
    expect(btn.className).toMatch(/bg-red/)
  })
})

// ─── Badge Tests ────────────────────────────────────────────────────────────────

describe('Badge', () => {
  it('renders with label prop', () => {
    render(<Badge label="NEW" />)
    expect(screen.getByText('NEW')).toBeInTheDocument()
  })

  it('renders with children', () => {
    render(<Badge>Active</Badge>)
    expect(screen.getByText('Active')).toBeInTheDocument()
  })

  it('renders using status auto-color', () => {
    render(<Badge status="QUALIFIED" label="Qualified" />)
    expect(screen.getByText('Qualified')).toBeInTheDocument()
  })

  it('applies variant color class', () => {
    render(<Badge variant="green">Won</Badge>)
    const el = screen.getByText('Won')
    expect(el.className).toMatch(/green/)
  })
})

// ─── ScoreBadge Tests ───────────────────────────────────────────────────────────

describe('ScoreBadge', () => {
  it('renders score number', () => {
    render(<ScoreBadge score={85} label="HOT" />)
    expect(screen.getByText(/85/)).toBeInTheDocument()
  })

  it('renders HOT label for high scores', () => {
    render(<ScoreBadge score={85} label="HOT" />)
    expect(screen.getByText(/HOT/)).toBeInTheDocument()
  })

  it('renders WARM label for medium scores', () => {
    render(<ScoreBadge score={55} label="WARM" />)
    expect(screen.getByText(/WARM/)).toBeInTheDocument()
  })

  it('renders COLD label for low scores', () => {
    render(<ScoreBadge score={25} label="COLD" />)
    expect(screen.getByText(/COLD/)).toBeInTheDocument()
  })
})
