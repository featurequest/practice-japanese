import { describe, it, expect } from 'vitest'
import { transformEntry } from './build-vocab-data.js'

describe('transformEntry', () => {
  it('maps all fields correctly', () => {
    const entry = {
      kanji: '会う',
      kana: 'あう',
      romaji: 'au',
      meanings: [{ localized: { en: 'to meet; to encounter', sv: 'träffa; möta' }, note: 'some note' }],
      jlpt: 'N5',
    }
    expect(transformEntry(entry)).toEqual({
      kanji: '会う',
      kana: 'あう',
      romaji: 'au',
      meanings_en: 'to meet; to encounter',
      meanings_sv: 'träffa; möta',
      meanings: [{ en: 'to meet; to encounter', sv: 'träffa; möta', note: 'some note' }],
      jlpt: 'N5',
    })
  })

  it('uses empty string when kanji is absent', () => {
    const entry = {
      kanji: '',
      kana: 'あう',
      romaji: 'au',
      meanings: [{ localized: { en: 'to meet', sv: 'träffa' }, note: '' }],
      jlpt: 'N5',
    }
    expect(transformEntry(entry).kanji).toBe('')
  })

  it('uses empty string when sv meaning is absent', () => {
    const entry = {
      kanji: '青',
      kana: 'あお',
      romaji: 'ao',
      meanings: [{ localized: { en: 'blue', sv: '' }, note: '' }],
      jlpt: 'N5',
    }
    expect(transformEntry(entry).meanings_sv).toBe('')
  })

  it('uses empty string when meanings array is empty', () => {
    const entry = {
      kanji: '',
      kana: 'あ',
      romaji: 'a',
      meanings: [],
      jlpt: 'N5',
    }
    expect(transformEntry(entry).meanings_en).toBe('')
    expect(transformEntry(entry).meanings_sv).toBe('')
    expect(transformEntry(entry).meanings).toEqual([])
  })
})
