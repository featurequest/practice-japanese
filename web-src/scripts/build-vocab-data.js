import { readFileSync, writeFileSync, copyFileSync, mkdirSync, existsSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = dirname(fileURLToPath(import.meta.url))

export function transformEntry(entry) {
  const meanings = entry.meanings.map(m => ({
    en: m.localized?.en || '',
    sv: m.localized?.sv || '',
    note: m.note || '',
  }))
  return {
    id: entry.id,
    kanji: entry.kanji || '',
    kana: entry.kana,
    romaji: entry.romaji,
    meanings_en: meanings[0]?.en || '',
    meanings_sv: meanings[0]?.sv || '',
    meanings,
    jlpt: entry.jlpt,
  }
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const srcPath = resolve(__dirname, '../../data/vocabulary.json')
  const outPath = resolve(__dirname, '../public/vocab.json')
  const ttfSrc = resolve(__dirname, '../../fonts/KleeOne-SemiBold.ttf')
  const ttfDst = resolve(__dirname, '../public/fonts/klee-one.ttf')

  const fontsDir = resolve(__dirname, '../public/fonts')
  if (!existsSync(fontsDir)) mkdirSync(fontsDir, { recursive: true })

  const all = JSON.parse(readFileSync(srcPath, 'utf8'))
  const compact = all.map(transformEntry)
  writeFileSync(outPath, JSON.stringify(compact))
  copyFileSync(ttfSrc, ttfDst)
  console.log(`Wrote ${compact.length} entries → ${outPath}`)
  console.log(`Copied TTF → ${ttfDst}`)
}
