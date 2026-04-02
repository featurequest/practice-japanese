import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WordRow from './WordRow'

const wordWithKanji = { kanji: '会う', kana: 'あう', romaji: 'au', meanings_en: 'to meet', meanings_sv: 'träffa', jlpt: 'N5' }
const wordNoKanji   = { kanji: '',    kana: 'あう', romaji: 'au', meanings_en: 'to meet', meanings_sv: 'träffa', jlpt: 'N5' }

describe('WordRow', () => {
  it('shows kanji as primary when kanji is present', () => {
    render(<WordRow word={wordWithKanji} selected={false} language="en" onToggle={() => {}} />)
    expect(screen.getByText('会う')).toBeInTheDocument()
  })

  it('shows kana as primary when no kanji', () => {
    render(<WordRow word={wordNoKanji} selected={false} language="en" onToggle={() => {}} />)
    expect(screen.getAllByText('あう')).toHaveLength(1)
  })

  it('shows kana below kanji when kanji is present', () => {
    render(<WordRow word={wordWithKanji} selected={false} language="en" onToggle={() => {}} />)
    expect(screen.getByText('会う')).toBeInTheDocument()
    expect(screen.getByText('あう')).toBeInTheDocument()
  })

  it('shows romaji', () => {
    render(<WordRow word={wordWithKanji} selected={false} language="en" onToggle={() => {}} />)
    expect(screen.getByText('au')).toBeInTheDocument()
  })

  it('shows EN meaning when language is en', () => {
    render(<WordRow word={wordWithKanji} selected={false} language="en" onToggle={() => {}} />)
    expect(screen.getByText('to meet')).toBeInTheDocument()
  })

  it('shows SV meaning when language is sv', () => {
    render(<WordRow word={wordWithKanji} selected={false} language="sv" onToggle={() => {}} />)
    expect(screen.getByText('träffa')).toBeInTheDocument()
  })

  it('calls onToggle when button is clicked', async () => {
    const onToggle = vi.fn()
    render(<WordRow word={wordWithKanji} selected={false} language="en" onToggle={onToggle} />)
    await userEvent.click(screen.getByRole('button'))
    expect(onToggle).toHaveBeenCalledWith(wordWithKanji)
  })

  it('button has selected class when selected', () => {
    render(<WordRow word={wordWithKanji} selected={true} language="en" onToggle={() => {}} />)
    expect(screen.getByRole('button')).toHaveClass('selected')
  })

  it('shows JLPT level tag when jlpt is set', () => {
    render(<WordRow word={wordWithKanji} selected={false} language="en" onToggle={() => {}} />)
    expect(screen.getByText('N5')).toBeInTheDocument()
  })

  it('does not render JLPT tag when jlpt is empty', () => {
    const noJlpt = { ...wordWithKanji, jlpt: '' }
    render(<WordRow word={noJlpt} selected={false} language="en" onToggle={() => {}} />)
    expect(screen.queryByText(/^N[1-5]$/)).not.toBeInTheDocument()
  })
})
