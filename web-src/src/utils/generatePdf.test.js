import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock jsPDF and jspdf-autotable before importing generatePdf
const mockSave = vi.fn()
const mockAddFileToVFS = vi.fn()
const mockAddFont = vi.fn()
const mockSetFont = vi.fn()
const mockSetPage = vi.fn()
const mockSetProperties = vi.fn()
const mockDoc = {
  addFileToVFS: mockAddFileToVFS,
  addFont: mockAddFont,
  setFont: mockSetFont,
  setFontSize: vi.fn(),
  setTextColor: vi.fn(),
  setDrawColor: vi.fn(),
  setLineWidth: vi.fn(),
  line: vi.fn(),
  text: vi.fn(),
  getTextWidth: vi.fn(() => 30),
  save: mockSave,
  setPage: mockSetPage,
  setProperties: mockSetProperties,
  internal: { pageSize: { width: 595.28, height: 841.89 }, getNumberOfPages: vi.fn(() => 2) },
}
const mockAutoTable = vi.fn()

vi.mock('jspdf', () => ({
  jsPDF: vi.fn(() => mockDoc),
}))
vi.mock('jspdf-autotable', () => ({
  default: mockAutoTable,
}))

// Mock fetch to return a dummy TTF buffer with ok: true
beforeEach(() => {
  vi.clearAllMocks()
  global.fetch = vi.fn().mockResolvedValue({
    ok: true,
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(8)),
  })
})

const { generatePdf } = await import('./generatePdf.js')

const words = [
  { id: 'aaaaaaaa', kanji: '会う', kana: 'あう', romaji: 'au', meanings_en: 'to meet', meanings_sv: 'träffa', meanings: [{ en: 'to meet', sv: 'träffa', note: '' }], jlpt: 'N5' },
  { id: 'bbbbbbbb', kanji: '',    kana: 'あさ', romaji: 'asa', meanings_en: 'morning', meanings_sv: 'morgon', meanings: [{ en: 'morning', sv: 'morgon', note: '' }], jlpt: 'N5' },
]

describe('generatePdf', () => {
  it('throws when font fetch returns a non-ok response', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 404 })
    await expect(generatePdf(words, 'en')).rejects.toThrow('Failed to load font: 404')
  })

  it('fetches the KleeOne TTF font', async () => {
    await generatePdf(words, 'en')
    expect(global.fetch).toHaveBeenCalledWith(expect.stringContaining('klee-one.ttf'))
  })

  it('registers the font with jsPDF', async () => {
    await generatePdf(words, 'en')
    expect(mockAddFileToVFS).toHaveBeenCalledWith('KleeOne.ttf', expect.any(String))
    expect(mockAddFont).toHaveBeenCalledWith('KleeOne.ttf', 'KleeOne', 'normal')
  })

  it('draws the 日本語Practice header on the first page', async () => {
    await generatePdf(words, 'en')
    expect(mockDoc.text).toHaveBeenCalledWith('日本語', expect.any(Number), expect.any(Number))
    expect(mockDoc.text).toHaveBeenCalledWith('Practice', expect.any(Number), expect.any(Number))
  })

  it('calls autoTable with correct rows for EN language', async () => {
    await generatePdf(words, 'en')
    expect(mockAutoTable).toHaveBeenCalledWith(
      mockDoc,
      expect.objectContaining({
        body: [
          ['会う\nあう', 'au', 'to meet'],
          ['あさ', 'asa', 'morning'],
        ],
      })
    )
  })

  it('uses SV meanings when language is sv', async () => {
    await generatePdf(words, 'sv')
    expect(mockAutoTable).toHaveBeenCalledWith(
      mockDoc,
      expect.objectContaining({
        body: expect.arrayContaining([
          ['会う\nあう', 'au', 'träffa'],
        ]),
      })
    )
  })

  it('falls back to EN meaning when SV is empty', async () => {
    const wordNoSv = { kanji: '青', kana: 'あお', romaji: 'ao', meanings_en: 'blue', meanings_sv: '', meanings: [{ en: 'blue', sv: '', note: '' }], jlpt: 'N5' }
    await generatePdf([wordNoSv], 'sv')
    expect(mockAutoTable).toHaveBeenCalledWith(
      mockDoc,
      expect.objectContaining({
        body: [['青\nあお', 'ao', 'blue']],
      })
    )
  })

  it('appends note below meaning when present', async () => {
    const wordWithNote = { kanji: '赤', kana: 'あか', romaji: 'aka', meanings_en: 'red', meanings_sv: 'röd', meanings: [{ en: 'red', sv: 'röd', note: 'esp. 紅い for scarlet' }], jlpt: 'N5' }
    await generatePdf([wordWithNote], 'en')
    expect(mockAutoTable).toHaveBeenCalledWith(
      mockDoc,
      expect.objectContaining({
        body: [['赤\nあか', 'aka', 'red\nesp. 紅い for scarlet']],
      })
    )
  })

  it('passes a didDrawPage hook for the footer', async () => {
    await generatePdf(words, 'en')
    const options = mockAutoTable.mock.calls.at(-1)[1]
    expect(typeof options.didDrawPage).toBe('function')
  })

  it('prefixes multiple meanings with circled numbers', async () => {
    const wordMulti = { kanji: '見る', kana: 'みる', romaji: 'miru', meanings_en: 'to see', meanings_sv: '', meanings: [{ en: 'to see', sv: '', note: '' }, { en: 'to look', sv: '', note: '' }], jlpt: 'N5' }
    await generatePdf([wordMulti], 'en')
    expect(mockAutoTable).toHaveBeenCalledWith(
      mockDoc,
      expect.objectContaining({
        body: [['見る\nみる', 'miru', '① to see\n② to look']],
      })
    )
  })

  it('does not prefix single meanings with circled numbers', async () => {
    await generatePdf(words, 'en')
    const options = mockAutoTable.mock.calls.at(-1)[1]
    // single meaning — no prefix
    expect(options.body[0][2]).toBe('to meet')
  })

  it('adds page numbers by iterating all pages', async () => {
    await generatePdf(words, 'en')
    expect(mockSetPage).toHaveBeenCalledTimes(2)
    expect(mockDoc.text).toHaveBeenCalledWith('1 / 2', expect.any(Number), expect.any(Number), expect.objectContaining({ align: 'right' }))
  })

  it('saves the file as vocabulary-custom.pdf', async () => {
    await generatePdf(words, 'en')
    expect(mockSave).toHaveBeenCalledWith('vocabulary-custom.pdf')
  })

  it('embeds word IDs in PDF subject metadata', async () => {
    await generatePdf(words, 'en')
    expect(mockSetProperties).toHaveBeenCalledWith(
      expect.objectContaining({ subject: JSON.stringify({ v: 1, ids: ['aaaaaaaa', 'bbbbbbbb'] }) })
    )
  })
})
