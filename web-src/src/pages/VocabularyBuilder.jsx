import { useState, useEffect, useMemo } from 'react'
import { Link } from 'react-router-dom'
import Fuse from 'fuse.js'
import SearchPanel from '../components/SearchPanel'
import SelectionPanel from '../components/SelectionPanel'
import { generatePdf } from '../utils/generatePdf'

const STORAGE_KEY = 'japanese-practice-selected-words'

export default function VocabularyBuilder() {
  const [vocab, setVocab] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedWords, setSelectedWords] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  })
  const [activeJlpt, setActiveJlpt] = useState(new Set())
  const [searchText, setSearchText] = useState('')
  const [language, setLanguage] = useState('en')
  const [generating, setGenerating] = useState(false)

  useEffect(() => {
    fetch(import.meta.env.BASE_URL + 'vocab.json')
      .then(r => r.json())
      .then(data => { setVocab(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(selectedWords))
    } catch {}
  }, [selectedWords])

  const fuse = useMemo(() => new Fuse(vocab, {
    keys: [
      { name: 'kana',        weight: 3 },
      { name: 'kanji',       weight: 3 },
      { name: 'romaji',      weight: 3 },
      { name: 'meanings_en', weight: 1 },
      { name: 'meanings_sv', weight: 1 },
    ],
    threshold: 0.35,
    ignoreLocation: true,
    includeScore: true,
    minMatchCharLength: 1,
  }), [vocab])

  const filteredVocab = useMemo(() => {
    const jlptFilter = w => activeJlpt.size === 0 || activeJlpt.has(w.jlpt)
    if (!searchText) {
      return vocab.filter(jlptFilter).sort((a, b) => a.kana.length - b.kana.length)
    }
    return fuse.search(searchText).map(r => r.item).filter(jlptFilter)
  }, [vocab, fuse, activeJlpt, searchText])

  const selectedKeys = useMemo(
    () => new Set(selectedWords.map(w => `${w.kanji}|${w.kana}`)),
    [selectedWords]
  )

  function toggleJlpt(level) {
    setActiveJlpt(prev => {
      const next = new Set(prev)
      if (next.has(level)) next.delete(level)
      else next.add(level)
      return next
    })
  }

  function toggleWord(word) {
    const key = `${word.kanji}|${word.kana}`
    if (selectedKeys.has(key)) {
      setSelectedWords(prev => prev.filter(w => `${w.kanji}|${w.kana}` !== key))
    } else {
      setSelectedWords(prev => [...prev, word])
    }
  }

  function removeWord(word) {
    const key = `${word.kanji}|${word.kana}`
    setSelectedWords(prev => prev.filter(w => `${w.kanji}|${w.kana}` !== key))
  }

  function clearWords() {
    setSelectedWords([])
  }

  function handleImport(ids) {
    if (!Array.isArray(ids)) return
    const vocabMap = new Map(vocab.map(w => [`${w.kanji}|${w.kana}`, w]))
    const toAdd = ids
      .filter(id => id && typeof id === 'object')
      .map(id => vocabMap.get(`${id.kanji}|${id.kana}`))
      .filter(Boolean)
    if (toAdd.length === 0) return
    setSelectedWords(prev => {
      const existing = new Set(prev.map(w => `${w.kanji}|${w.kana}`))
      return [...prev, ...toAdd.filter(w => !existing.has(`${w.kanji}|${w.kana}`))]
    })
  }

  function handleAddLevel(level) {
    const toAdd = vocab.filter(w => w.jlpt === level)
    setSelectedWords(prev => {
      const existing = new Set(prev.map(w => `${w.kanji}|${w.kana}`))
      return [...prev, ...toAdd.filter(w => !existing.has(`${w.kanji}|${w.kana}`))]
    })
  }

  async function handleGenerate() {
    setGenerating(true)
    try {
      await generatePdf(selectedWords, language)
    } catch {
      alert('Failed to generate PDF. Please try again.')
    } finally {
      setGenerating(false)
    }
  }

  const header = (
    <div className="builder-header">
      <Link to="/" className="builder-brand">
        <span className="jp">日本語</span>Practice
      </Link>
    </div>
  )

  if (loading) {
    return (
      <div className="builder-root">
        {header}
        <div className="builder-loading">Loading vocabulary…</div>
      </div>
    )
  }

  return (
    <div className="builder-root">
      {header}
      <div className="builder-page">
      <SearchPanel
        words={filteredVocab}
        activeJlpt={activeJlpt}
        searchText={searchText}
        selectedKeys={selectedKeys}
        language={language}
        onJlptToggle={toggleJlpt}
        onSearch={setSearchText}
        onToggleWord={toggleWord}
      />
      <SelectionPanel
        selectedWords={selectedWords}
        language={language}
        generating={generating}
        onRemove={removeWord}
        onLanguageChange={setLanguage}
        onGenerate={handleGenerate}
        onClear={clearWords}
        onImport={handleImport}
        onAddLevel={handleAddLevel}
      />
      </div>
    </div>
  )
}
