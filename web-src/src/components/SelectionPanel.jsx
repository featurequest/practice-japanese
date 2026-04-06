import { useRef } from 'react'

const LEVELS = ['N5', 'N4', 'N3', 'N2', 'N1']

export default function SelectionPanel({
  selectedWords, language, generating, onRemove, onLanguageChange, onGenerate, onClear, onImport, onAddLevel,
}) {
  const fileInputRef = useRef(null)

  function handleExport() {
    const ids = selectedWords.map(w => w.id)
    const blob = new Blob([JSON.stringify(ids, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'vocabulary-selection.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  function handleFileChange(e) {
    const file = e.target.files[0]
    if (!file) return
    e.target.value = ''

    const isPdf = file.name.endsWith('.pdf') || file.type === 'application/pdf'
    const reader = new FileReader()

    if (isPdf) {
      reader.onload = evt => {
        try {
          const text = new TextDecoder('latin1').decode(evt.target.result)
          const match = text.match(/\/Subject\s*\(([^)]*)\)/)
          if (!match) throw new Error('No vocabulary data found in this PDF.')
          const { v, ids } = JSON.parse(match[1])
          if (v !== 1 || !Array.isArray(ids)) throw new Error('Unrecognized format.')
          onImport(ids)
        } catch (err) {
          alert(err.message || 'Could not read vocabulary data from this PDF.')
        }
      }
      reader.readAsArrayBuffer(file)
    } else {
      reader.onload = evt => {
        try {
          const ids = JSON.parse(evt.target.result)
          onImport(ids)
        } catch {
          alert('Invalid file. Please select a vocabulary-selection.json or vocabulary-custom.pdf file.')
        }
      }
      reader.readAsText(file)
    }
  }

  return (
    <div className="selection-panel">
      <div className="selection-header">
        <span>Selected ({selectedWords.length})</span>
        <div className="selection-header-actions">
          <button className="icon-btn" onClick={() => fileInputRef.current.click()} title="Import selection (JSON or PDF)" aria-label="Import selection">↑</button>
          <input ref={fileInputRef} type="file" accept=".json,.pdf" style={{ display: 'none' }} onChange={handleFileChange} />
          {selectedWords.length > 0 && (
            <button className="icon-btn" onClick={handleExport} title="Export selection" aria-label="Export selection">↓</button>
          )}
          {selectedWords.length > 0 && (
            <button className="clear-btn" onClick={onClear}>Clear</button>
          )}
        </div>
      </div>

      <div className="quick-select-row">
        {LEVELS.map(level => (
          <button key={level} className="quick-select-btn" onClick={() => onAddLevel(level)}>
            +{level}
          </button>
        ))}
      </div>

      <div className="selected-list">
        {selectedWords.length === 0 && (
          <div className="sel-empty">
            <span className="sel-empty-icon" aria-hidden="true">選</span>
            <p>Search and add words to build your PDF</p>
          </div>
        )}
        {selectedWords.map(w => (
          <div key={w.id} className="selected-row">
            <div className="selected-word-label">
              <div className="sel-main">
                <span className="sel-primary">{w.kanji || w.kana}</span>
                {w.kanji && <span className="sel-reading">{w.kana}</span>}
              </div>
              <div className="sel-sub">
                <span className="sel-romaji">{w.romaji}</span>
                {w.jlpt && <span className="sel-jlpt">{w.jlpt}</span>}
              </div>
            </div>
            <button
              className="remove-btn"
              onClick={() => onRemove(w)}
              aria-label={`Remove ${w.kanji || w.kana}`}
            >
              ✕
            </button>
          </div>
        ))}
      </div>

      <div className="lang-toggle">
        {['en', 'sv'].map(lang => (
          <button
            key={lang}
            className={`lang-btn${language === lang ? ' active' : ''}`}
            onClick={() => onLanguageChange(lang)}
          >
            {lang.toUpperCase()}
          </button>
        ))}
      </div>
      <button
        className="generate-btn"
        disabled={selectedWords.length === 0 || generating}
        onClick={onGenerate}
      >
        {generating ? 'Generating…' : '⬇ Generate PDF'}
      </button>
    </div>
  )
}
