export default function WordRow({ word, selected, language, onToggle }) {
  const primary = word.kanji || word.kana
  const showReading = !!word.kanji
  const meaning = language === 'sv' && word.meanings_sv ? word.meanings_sv : word.meanings_en

  return (
    <div className="word-row">
      <div className="word-primary">
        <span className="word-kanji">{primary}</span>
        {showReading && <span className="word-kana">{word.kana}</span>}
      </div>
      <span className="word-romaji">{word.romaji}</span>
      <span className="word-meaning">{meaning}</span>
      {word.jlpt && <span className="word-jlpt-tag">{word.jlpt.toUpperCase()}</span>}
      <button
        className={`word-action-btn${selected ? ' selected' : ''}`}
        onClick={() => onToggle(word)}
        aria-label={selected ? 'Remove from selection' : 'Add to selection'}
      >
        {selected ? '✓' : '+'}
      </button>
    </div>
  )
}
