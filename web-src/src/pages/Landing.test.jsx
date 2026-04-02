import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Landing from './Landing'

function renderLanding() {
  return render(
    <MemoryRouter>
      <Landing />
    </MemoryRouter>
  )
}

describe('Landing', () => {
  it('renders the site title', () => {
    renderLanding()
    expect(screen.getByText('Practice')).toBeInTheDocument()
  })

  it('renders links to the vocabulary builder', () => {
    renderLanding()
    const links = screen.getAllByRole('link', { name: /vocabulary builder/i })
    expect(links.length).toBeGreaterThanOrEqual(1)
  })

  it('renders download sections', () => {
    renderLanding()
    expect(screen.getByRole('heading', { name: /Kana Flash Cards/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /JLPT Vocabulary PDFs/i })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: /Anki Decks/i })).toBeInTheDocument()
  })
})
