export default function SelectionPanel({
  selectedWords, language, generating, onRemove, onLanguageChange, onGenerate, onClear,
}) {
  return (
    <div className="selection-panel">
      <div className="selection-header">
        <span>Selected ({selectedWords.length})</span>
        {selectedWords.length > 0 && (
          <button className="clear-btn" onClick={onClear}>Clear</button>
        )}
      </div>
      <div className="selected-list">
        {selectedWords.map(w => (
          <div key={`${w.kanji}|${w.kana}`} className="selected-row">
            <div className="selected-word-label">
              <span className="sel-primary">{w.kanji || w.kana}</span>
              {w.kanji && <span className="sel-reading">{w.kana}</span>}
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
