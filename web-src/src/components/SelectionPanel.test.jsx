import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SelectionPanel from './SelectionPanel'

const words = [
  { kanji: '会う', kana: 'あう', romaji: 'au', meanings_en: 'to meet', meanings_sv: 'träffa', jlpt: 'N5' },
  { kanji: '',    kana: 'あさ', romaji: 'asa', meanings_en: 'morning', meanings_sv: 'morgon', jlpt: 'N5' },
]

const defaultProps = {
  selectedWords: words,
  language: 'en',
  generating: false,
  onRemove: vi.fn(),
  onLanguageChange: vi.fn(),
  onGenerate: vi.fn(),
  onClear: vi.fn(),
}

describe('SelectionPanel', () => {
  it('shows selected count in header', () => {
    render(<SelectionPanel {...defaultProps} />)
    expect(screen.getByText(/selected.*2/i)).toBeInTheDocument()
  })

  it('renders each selected word', () => {
    render(<SelectionPanel {...defaultProps} />)
    expect(screen.getByText('会う')).toBeInTheDocument()
    expect(screen.getByText('あさ')).toBeInTheDocument()
  })

  it('clicking remove button calls onRemove with word', async () => {
    const onRemove = vi.fn()
    render(<SelectionPanel {...defaultProps} onRemove={onRemove} />)
    const removeBtns = screen.getAllByRole('button', { name: /remove/i })
    await userEvent.click(removeBtns[0])
    expect(onRemove).toHaveBeenCalledWith(words[0])
  })

  it('active language button has active class', () => {
    render(<SelectionPanel {...defaultProps} language="sv" />)
    expect(screen.getByRole('button', { name: 'SV' })).toHaveClass('active')
    expect(screen.getByRole('button', { name: 'EN' })).not.toHaveClass('active')
  })

  it('clicking language button calls onLanguageChange', async () => {
    const onLanguageChange = vi.fn()
    render(<SelectionPanel {...defaultProps} onLanguageChange={onLanguageChange} />)
    await userEvent.click(screen.getByRole('button', { name: 'SV' }))
    expect(onLanguageChange).toHaveBeenCalledWith('sv')
  })

  it('generate button is disabled when no words selected', () => {
    render(<SelectionPanel {...defaultProps} selectedWords={[]} />)
    expect(screen.getByRole('button', { name: /generate pdf/i })).toBeDisabled()
  })

  it('generate button is enabled when words are selected', () => {
    render(<SelectionPanel {...defaultProps} />)
    expect(screen.getByRole('button', { name: /generate pdf/i })).toBeEnabled()
  })

  it('clicking generate calls onGenerate', async () => {
    const onGenerate = vi.fn()
    render(<SelectionPanel {...defaultProps} onGenerate={onGenerate} />)
    await userEvent.click(screen.getByRole('button', { name: /generate pdf/i }))
    expect(onGenerate).toHaveBeenCalled()
  })

  it('generate button is disabled and shows Generating when generating is true', () => {
    render(<SelectionPanel {...defaultProps} generating={true} />)
    const btn = screen.getByRole('button', { name: /generating/i })
    expect(btn).toBeDisabled()
  })

  it('shows clear button when words are selected and calls onClear', async () => {
    const onClear = vi.fn()
    render(<SelectionPanel {...defaultProps} onClear={onClear} />)
    const clearBtn = screen.getByRole('button', { name: /clear/i })
    expect(clearBtn).toBeInTheDocument()
    await userEvent.click(clearBtn)
    expect(onClear).toHaveBeenCalled()
  })

  it('does not show clear button when no words selected', () => {
    render(<SelectionPanel {...defaultProps} selectedWords={[]} />)
    expect(screen.queryByRole('button', { name: /clear/i })).not.toBeInTheDocument()
  })
})
