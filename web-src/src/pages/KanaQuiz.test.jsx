import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import KanaQuiz from './KanaQuiz'

function renderQuiz() {
  return render(<MemoryRouter><KanaQuiz /></MemoryRouter>)
}

describe('KanaQuiz', () => {
  it('shows the setup screen on mount', () => {
    renderQuiz()
    expect(screen.getByRole('button', { name: /start quiz/i })).toBeInTheDocument()
  })

  it('shows script toggle buttons', () => {
    renderQuiz()
    expect(screen.getByRole('button', { name: /hiragana/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /katakana/i })).toBeInTheDocument()
  })

  it('shows quick-select buttons', () => {
    renderQuiz()
    expect(screen.getByRole('button', { name: /^all$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^dakuten$/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /^combinations$/i })).toBeInTheDocument()
  })

  it('shows mode toggle buttons on setup screen', () => {
    renderQuiz()
    expect(screen.getByRole('button', { name: /multiple choice/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /keyboard/i })).toBeInTheDocument()
  })

  it('start button is disabled when no characters selected', async () => {
    renderQuiz()
    await userEvent.click(screen.getByRole('button', { name: /^none$/i }))
    expect(screen.getByRole('button', { name: /start quiz/i })).toBeDisabled()
  })

  it('shows 4 quiz choice buttons after starting in multiple-choice mode', async () => {
    renderQuiz()
    await userEvent.click(screen.getByRole('button', { name: /start quiz/i }))
    expect(document.querySelectorAll('.quiz-choice')).toHaveLength(4)
  })

  it('shows text input after starting in keyboard mode', async () => {
    renderQuiz()
    await userEvent.click(screen.getByRole('button', { name: /^keyboard$/i }))
    // Select only 1 character so quiz starts with a known card
    await userEvent.click(screen.getByRole('button', { name: /^none$/i }))
    await userEvent.click(document.querySelectorAll('.kana-cell')[0])
    await userEvent.click(screen.getByRole('button', { name: /start quiz/i }))
    expect(screen.getByPlaceholderText(/romaji/i)).toBeInTheDocument()
    expect(document.querySelectorAll('.quiz-choice')).toHaveLength(0)
  })

  it('keyboard mode: correct answer shows correct state', async () => {
    renderQuiz()
    await userEvent.click(screen.getByRole('button', { name: /^keyboard$/i }))
    await userEvent.click(screen.getByRole('button', { name: /^none$/i }))
    // Select only あ (first cell, romaji = 'a')
    await userEvent.click(document.querySelectorAll('.kana-cell')[0])
    await userEvent.click(screen.getByRole('button', { name: /start quiz/i }))
    const input = screen.getByPlaceholderText(/romaji/i)
    await userEvent.type(input, 'a')
    await userEvent.click(screen.getByRole('button', { name: /check/i }))
    expect(input).toHaveClass('quiz-input--correct')
  })

  it('keyboard mode: wrong answer shows wrong state and correct hint', async () => {
    renderQuiz()
    await userEvent.click(screen.getByRole('button', { name: /^keyboard$/i }))
    await userEvent.click(screen.getByRole('button', { name: /^none$/i }))
    await userEvent.click(document.querySelectorAll('.kana-cell')[0])
    await userEvent.click(screen.getByRole('button', { name: /start quiz/i }))
    const input = screen.getByPlaceholderText(/romaji/i)
    await userEvent.type(input, 'zzz')
    await userEvent.click(screen.getByRole('button', { name: /check/i }))
    expect(input).toHaveClass('quiz-input--wrong')
    expect(screen.getByText(/✓/)).toBeInTheDocument()
  })

  it('applies correct CSS class to right answer and wrong CSS class to chosen wrong answer', async () => {
    renderQuiz()
    await userEvent.click(screen.getByRole('button', { name: /^none$/i }))
    const cells = document.querySelectorAll('.kana-cell')
    await userEvent.click(cells[0])
    await userEvent.click(screen.getByRole('button', { name: /start quiz/i }))

    const choices = Array.from(document.querySelectorAll('.quiz-choice'))
    await userEvent.click(choices[0])

    const allChoices = Array.from(document.querySelectorAll('.quiz-choice'))
    const correctChoices = allChoices.filter(b => b.classList.contains('quiz-choice--correct'))
    expect(correctChoices).toHaveLength(1)
  })

  it('shows results screen when all questions answered', async () => {
    renderQuiz()
    await userEvent.click(screen.getByRole('button', { name: /^none$/i }))
    const cells = document.querySelectorAll('.kana-cell')
    await userEvent.click(cells[0])
    await userEvent.click(screen.getByRole('button', { name: /start quiz/i }))
    const choices = document.querySelectorAll('.quiz-choice')
    await userEvent.click(choices[0])
    expect(await screen.findByText(/results/i)).toBeInTheDocument()
  })
})
