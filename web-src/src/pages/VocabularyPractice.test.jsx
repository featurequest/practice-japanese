import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import VocabularyPractice from './VocabularyPractice'

const words = [
  { id: '1', kanji: '食べる', kana: 'たべる', romaji: 'taberu', meanings_en: 'to eat', jlpt: 'N5' },
  { id: '2', kanji: '飲む',   kana: 'のむ',   romaji: 'nomu',   meanings_en: 'to drink', jlpt: 'N5' },
]

function renderPractice(state = { words }) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: '/vocabulary-builder/practice', state }]}>
      <Routes>
        <Route path="/vocabulary-builder/practice" element={<VocabularyPractice />} />
        <Route path="/vocabulary-builder" element={<div>Builder</div>} />
      </Routes>
    </MemoryRouter>
  )
}

describe('VocabularyPractice', () => {
  it('shows direction toggle buttons', () => {
    renderPractice()
    expect(screen.getByRole('button', { name: /jp.*en/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /en.*jp/i })).toBeInTheDocument()
  })

  it('shows the kanji front in JP→EN mode', () => {
    renderPractice()
    expect(screen.getByText('食べる')).toBeInTheDocument()
  })

  it('shows meaning front in EN→JP mode', async () => {
    renderPractice()
    await userEvent.click(screen.getByRole('button', { name: /en.*jp/i }))
    expect(screen.getByText('to eat')).toBeInTheDocument()
  })

  it('first press reveals back, second press advances card', async () => {
    renderPractice()
    const btn = screen.getByRole('button', { name: /next/i })
    expect(screen.getByRole('button', { name: /flip/i })).toHaveAttribute('aria-pressed', 'false')
    await userEvent.click(btn)
    expect(screen.getByRole('button', { name: /flip/i })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByText(/1\s*\/\s*2/)).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /next/i }))
    expect(screen.getByText(/2\s*\/\s*2/)).toBeInTheDocument()
  })

  it('tapping card flips then advances', async () => {
    renderPractice()
    const card = screen.getByRole('button', { name: /flip/i })
    await userEvent.click(card)
    expect(card).toHaveAttribute('aria-pressed', 'true')
    await userEvent.click(card)
    expect(screen.getByText(/2\s*\/\s*2/)).toBeInTheDocument()
  })

  it('shows progress 1 / 2', () => {
    renderPractice()
    expect(screen.getByText(/1\s*\/\s*2/)).toBeInTheDocument()
  })

  it('navigates back to builder after last card', async () => {
    renderPractice()
    // card 1: flip then advance
    await userEvent.click(screen.getByRole('button', { name: /next/i }))
    await userEvent.click(screen.getByRole('button', { name: /next/i }))
    // card 2: flip then done
    await userEvent.click(screen.getByRole('button', { name: /next/i }))
    await userEvent.click(screen.getByRole('button', { name: /done/i }))
    expect(await screen.findByText('Builder')).toBeInTheDocument()
  })
})
