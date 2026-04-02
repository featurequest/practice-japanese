import WordRow from './WordRow'

const LEVELS = ['N5', 'N4', 'N3', 'N2', 'N1']
const DISPLAY_LIMIT = 200

export default function SearchPanel({
  words, activeJlpt, searchText, selectedKeys, language,
  onJlptToggle, onSearch, onToggleWord,
}) {
  const visible = words.slice(0, DISPLAY_LIMIT)
  const overflow = words.length - visible.length

  return (
    <div className="search-panel">
      <div className="filter-row">
        {LEVELS.map(level => (
          <button
            key={level}
            className={`level-btn${activeJlpt.has(level) ? ' active' : ''}`}
            onClick={() => onJlptToggle(level)}
            aria-pressed={activeJlpt.has(level)}
          >
            {level}
          </button>
        ))}
      </div>
      <div className="search-input-wrap">
        <input
          className="search-input"
          type="text"
          placeholder="Search words, readings, meanings…"
          aria-label="Search words, readings, meanings"
          value={searchText}
          onChange={e => onSearch(e.target.value)}
        />
      </div>
      <div className="results-header">
        {overflow > 0
          ? `${words.length} words — showing first ${DISPLAY_LIMIT}, refine to see more`
          : `${words.length} words`}
      </div>
      <div className="results-list">
        {visible.map(w => (
          <WordRow
            key={`${w.kanji}|${w.kana}|${w.romaji}`}
            word={w}
            selected={selectedKeys.has(w.id)}
            language={language}
            onToggle={onToggleWord}
          />
        ))}
      </div>
    </div>
  )
}
