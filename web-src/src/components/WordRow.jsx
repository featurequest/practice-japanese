export default function WordRow({ word, selected, language, onToggle }) {
  const primary = word.kanji || word.kana
  const showReading = !!word.kanji
  const meaning = language === 'sv' && word.meanings_sv ? word.meanings_sv : word.meanings_en

  return (
    <button
      className={`word-row${selected ? ' selected' : ''}`}
      onClick={() => onToggle(word)}
      aria-label={`${selected ? 'Remove' : 'Add'} ${primary} (${word.romaji})`}
      aria-pressed={selected}
    >
      <div className="word-primary">
        <span className="word-kanji" lang="ja">{primary}</span>
        {showReading && <span className="word-kana" lang="ja">{word.kana}</span>}
      </div>
      <span className="word-romaji">{word.romaji}</span>
      <span className="word-meaning" title={meaning}>{meaning}</span>
      {word.jlpt && <span className="word-jlpt-tag">{word.jlpt.toUpperCase()}</span>}
      <span className="word-sel-icon" aria-hidden="true">{selected ? '✓' : '+'}</span>
    </button>
  )
}
