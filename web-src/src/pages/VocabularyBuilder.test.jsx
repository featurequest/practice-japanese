import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import VocabularyBuilder from './VocabularyBuilder'

const mockVocab = [
  { id: 'aaaaaaaa', kanji: '会う', kana: 'あう', romaji: 'au',  meanings_en: 'to meet', meanings_sv: 'träffa', meanings: [{ en: 'to meet', sv: 'träffa', note: '' }], jlpt: 'N5' },
  { id: 'bbbbbbbb', kanji: '青',  kana: 'あお', romaji: 'ao',  meanings_en: 'blue',    meanings_sv: '',       meanings: [{ en: 'blue',    sv: '',       note: '' }], jlpt: 'N5' },
  { id: 'cccccccc', kanji: '赤',  kana: 'あか', romaji: 'aka', meanings_en: 'red',     meanings_sv: 'röd',    meanings: [{ en: 'red',     sv: 'röd',    note: '' }], jlpt: 'N4' },
]

beforeEach(() => {
  localStorage.clear()
  global.fetch = vi.fn().mockResolvedValue({
    json: () => Promise.resolve(mockVocab),
  })
})

function renderBuilder() {
  return render(
    <MemoryRouter>
      <VocabularyBuilder />
    </MemoryRouter>
  )
}

describe('VocabularyBuilder', () => {
  it('loads and displays vocabulary', async () => {
    renderBuilder()
    await waitFor(() => expect(screen.getByText('会う')).toBeInTheDocument())
    expect(screen.getByText('青')).toBeInTheDocument()
    expect(screen.getByText('赤')).toBeInTheDocument()
  })

  it('shows total word count', async () => {
    renderBuilder()
    await waitFor(() => expect(screen.getByText('3 words')).toBeInTheDocument())
  })

  it('JLPT filter hides non-matching words', async () => {
    renderBuilder()
    await waitFor(() => screen.getByText('会う'))
    await userEvent.click(screen.getByRole('button', { name: 'N5' }))
    expect(screen.getByText('会う')).toBeInTheDocument()
    expect(screen.queryByText('赤')).not.toBeInTheDocument()
  })

  it('text search filters results by English meaning', async () => {
    renderBuilder()
    await waitFor(() => screen.getByText('会う'))
    await userEvent.type(screen.getByPlaceholderText(/search/i), 'blue')
    expect(screen.getByText('青')).toBeInTheDocument()
    expect(screen.queryByText('会う')).not.toBeInTheDocument()
  })

  it('text search filters by Swedish meaning when language is sv', async () => {
    renderBuilder()
    await waitFor(() => screen.getByText('会う'))
    await userEvent.click(screen.getByRole('button', { name: 'SV' }))
    await userEvent.type(screen.getByPlaceholderText(/search/i), 'röd')
    expect(screen.getByText('赤')).toBeInTheDocument()
    expect(screen.queryByText('会う')).not.toBeInTheDocument()
  })

  it('selecting a word adds it to the selection panel', async () => {
    renderBuilder()
    await waitFor(() => screen.getByText('会う'))
    const addBtns = screen.getAllByRole('button', { name: /add to selection/i })
    await userEvent.click(addBtns[0])
    expect(screen.getByText(/selected.*1/i)).toBeInTheDocument()
  })

  it('removing a word removes it from the selection panel', async () => {
    renderBuilder()
    await waitFor(() => screen.getByText('会う'))
    await userEvent.click(screen.getAllByRole('button', { name: /add to selection/i })[0])
    await userEvent.click(screen.getByRole('button', { name: /remove 会う/i }))
    expect(screen.getByText(/selected.*0/i)).toBeInTheDocument()
  })

  it('clear button removes all selected words', async () => {
    renderBuilder()
    await waitFor(() => screen.getByText('会う'))
    await userEvent.click(screen.getAllByRole('button', { name: /add to selection/i })[0])
    await userEvent.click(screen.getByRole('button', { name: /clear/i }))
    expect(screen.getByText(/selected.*0/i)).toBeInTheDocument()
  })

  it('persists selected words to localStorage', async () => {
    renderBuilder()
    await waitFor(() => screen.getByText('会う'))
    await userEvent.click(screen.getAllByRole('button', { name: /add to selection/i })[0])
    const stored = JSON.parse(localStorage.getItem('japanese-practice-selected-words'))
    expect(stored).toHaveLength(1)
    expect(stored[0].kanji).toBe('会う')
  })

  it('restores selected words from localStorage on mount', async () => {
    localStorage.setItem('japanese-practice-selected-words', JSON.stringify([mockVocab[0]]))
    renderBuilder()
    await waitFor(() => expect(screen.getByText(/selected.*1/i)).toBeInTheDocument())
  })
})
