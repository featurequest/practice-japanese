import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SearchPanel from './SearchPanel'

const words = [
  { id: 'aaaaaaaa', kanji: '会う', kana: 'あう', romaji: 'au', meanings_en: 'to meet', meanings_sv: 'träffa', jlpt: 'N5' },
  { id: 'bbbbbbbb', kanji: '',    kana: 'あさ', romaji: 'asa', meanings_en: 'morning', meanings_sv: 'morgon', jlpt: 'N5' },
]

const defaultProps = {
  words,
  activeJlpt: new Set(),
  searchText: '',
  selectedKeys: new Set(),
  language: 'en',
  onJlptToggle: vi.fn(),
  onSearch: vi.fn(),
  onToggleWord: vi.fn(),
}

describe('SearchPanel', () => {
  it('renders all 5 JLPT level buttons', () => {
    render(<SearchPanel {...defaultProps} />)
    for (const level of ['N5', 'N4', 'N3', 'N2', 'N1']) {
      expect(screen.getByRole('button', { name: level })).toBeInTheDocument()
    }
  })

  it('active level button has active class', () => {
    render(<SearchPanel {...defaultProps} activeJlpt={new Set(['N5'])} />)
    expect(screen.getByRole('button', { name: 'N5' })).toHaveClass('active')
    expect(screen.getByRole('button', { name: 'N4' })).not.toHaveClass('active')
  })

  it('clicking level button calls onJlptToggle with level string', async () => {
    const onJlptToggle = vi.fn()
    render(<SearchPanel {...defaultProps} onJlptToggle={onJlptToggle} />)
    await userEvent.click(screen.getByRole('button', { name: 'N3' }))
    expect(onJlptToggle).toHaveBeenCalledWith('N3')
  })

  it('shows result count', () => {
    render(<SearchPanel {...defaultProps} />)
    expect(screen.getByText(/2 words/i)).toBeInTheDocument()
  })

  it('renders a word row for each word', () => {
    render(<SearchPanel {...defaultProps} />)
    expect(screen.getByText('会う')).toBeInTheDocument()
    expect(screen.getByText('morning')).toBeInTheDocument()
  })

  it('typing in search calls onSearch', async () => {
    const onSearch = vi.fn()
    render(<SearchPanel {...defaultProps} onSearch={onSearch} />)
    await userEvent.type(screen.getByPlaceholderText(/search/i), 'a')
    expect(onSearch).toHaveBeenCalledWith('a')
  })
})
