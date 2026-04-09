import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FlashCard from './FlashCard'

describe('FlashCard', () => {
  it('shows front face when flipped=false', () => {
    render(<FlashCard front={<span>Front</span>} back={<span>Back</span>} flipped={false} />)
    expect(screen.getByRole('button', { name: /flip/i })).toHaveAttribute('aria-pressed', 'false')
  })

  it('back content visible immediately when flipped=true', () => {
    render(<FlashCard front={<span>Front</span>} back={<span>Back</span>} flipped={true} />)
    expect(screen.getByText('Back')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /flip/i })).toHaveAttribute('aria-pressed', 'true')
  })

  it('back content hidden immediately when flipped=false', () => {
    const { rerender } = render(
      <FlashCard front={<span>Front</span>} back={<span>Back</span>} flipped={true} />
    )
    expect(screen.getByText('Back')).toBeInTheDocument()
    rerender(<FlashCard front={<span>Front</span>} back={<span>Back</span>} flipped={false} />)
    expect(screen.queryByText('Back')).not.toBeInTheDocument()
  })

  it('calls onFlip when clicked', async () => {
    const onFlip = vi.fn()
    render(<FlashCard front={<span>F</span>} back={<span>B</span>} flipped={false} onFlip={onFlip} />)
    await userEvent.click(screen.getByRole('button', { name: /flip/i }))
    expect(onFlip).toHaveBeenCalledOnce()
  })
})
