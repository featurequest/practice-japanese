import { useState, useRef } from 'react'
import { Link } from 'react-router-dom'
import { HIRAGANA, KATAKANA } from '../data/kana'

function getPool(s) {
  if (s === 'hiragana') return HIRAGANA
  if (s === 'katakana') return KATAKANA
  return [...HIRAGANA, ...KATAKANA]
}

const GROUPS = ['basic', 'dakuten', 'combination']

function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

function buildDistractors(correct, pool) {
  const candidates = shuffle(pool.filter(k => k.romaji !== correct.romaji))
  return candidates.slice(0, 3)
}

export default function KanaQuiz() {
  const [script, setScript] = useState('hiragana')
  const [selected, setSelected] = useState(() => new Set(HIRAGANA.map(k => k.char)))
  const [mode, setMode] = useState('multiple-choice') // 'multiple-choice' | 'keyboard'
  const [phase, setPhase] = useState('setup') // 'setup' | 'quiz' | 'results'
  const [questions, setQuestions] = useState([])
  const [qIdx, setQIdx] = useState(0)
  const [choices, setChoices] = useState([])
  const [answered, setAnswered] = useState(null) // null | 'correct' | 'wrong'
  const [selectedChoice, setSelectedChoice] = useState(null)
  const [score, setScore] = useState(0)
  const [inputValue, setInputValue] = useState('')
  const quizPoolRef = useRef([])

  const pool = getPool(script)

  function toggleScript(s) {
    setScript(s)
    setSelected(new Set(getPool(s).map(k => k.char)))
  }

  function toggleCell(char) {
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(char)) next.delete(char)
      else next.add(char)
      return next
    })
  }

  function quickSelect(group) {
    if (group === 'all') { setSelected(new Set(getPool(script).map(k => k.char))); return }
    if (group === 'none') { setSelected(new Set()); return }
    const chars = getPool(script).filter(k => k.group === group).map(k => k.char)
    setSelected(prev => {
      const next = new Set(prev)
      chars.forEach(c => { if (next.has(c)) next.delete(c); else next.add(c) })
      return next
    })
  }

  function startQuiz() {
    const qs = shuffle(pool.filter(k => selected.has(k.char)))
    const q = qs[0]
    quizPoolRef.current = pool
    setQuestions(qs)
    setQIdx(0)
    setScore(0)
    setAnswered(null)
    setSelectedChoice(null)
    setInputValue('')
    if (mode === 'multiple-choice') {
      setChoices(shuffle([q, ...buildDistractors(q, pool)]))
    }
    setPhase('quiz')
  }

  function handleChoice(romaji) {
    if (answered !== null) return
    const correct = romaji === questions[qIdx].romaji
    setSelectedChoice(romaji)
    setAnswered(correct ? 'correct' : 'wrong')
    if (correct) setScore(s => s + 1)
    setTimeout(() => {
      const next = qIdx + 1
      if (next >= questions.length) {
        setPhase('results')
      } else {
        const q = questions[next]
        setQIdx(next)
        setChoices(shuffle([q, ...buildDistractors(q, quizPoolRef.current)]))
        setAnswered(null)
        setSelectedChoice(null)
      }
    }, 700)
  }

  function handleKeyboardSubmit(e) {
    e.preventDefault()
    if (answered !== null || !inputValue.trim()) return
    const correct = inputValue.trim().toLowerCase() === questions[qIdx].romaji
    setAnswered(correct ? 'correct' : 'wrong')
    if (correct) setScore(s => s + 1)
    setTimeout(() => {
      const next = qIdx + 1
      if (next >= questions.length) {
        setPhase('results')
      } else {
        setQIdx(next)
        setAnswered(null)
        setInputValue('')
      }
    }, 700)
  }

  const header = (
    <div className="quiz-header">
      <Link to="/" className="quiz-brand"><span className="jp">日本語</span>Practice</Link>
      {phase !== 'setup' && (
        <button className="quiz-btn quiz-back-btn"
          onClick={() => setPhase('setup')}>← Setup</button>
      )}
    </div>
  )

  if (phase === 'results') {
    return (
      <div className="quiz-root">
        {header}
        <div className="quiz-body">
          <div className="quiz-results">
            <h2>Results</h2>
            <p>{score} / {questions.length} correct</p>
            <button className="quiz-btn" onClick={startQuiz}>Try Again</button>
            <button className="quiz-btn" onClick={() => setPhase('setup')}>Change Characters</button>
          </div>
        </div>
      </div>
    )
  }

  if (phase === 'quiz') {
    const q = questions[qIdx]
    const pct = (qIdx / questions.length * 100).toFixed(0)
    return (
      <div className="quiz-root">
        {header}
        <div className="quiz-body">
          <div className="quiz-progress">
            <span>{qIdx + 1} / {questions.length}</span>
            <span>{score} correct</span>
          </div>
          <div className="quiz-progress-bar">
            <div className="quiz-progress-bar__fill" style={{ width: `${pct}%` }} />
          </div>
          <div className="quiz-char">{q.char}</div>

          {mode === 'multiple-choice' ? (
            <div className="quiz-choices">
              {choices.map(k => {
                let cls = 'quiz-choice'
                if (answered !== null) {
                  if (k.romaji === q.romaji) cls += ' quiz-choice--correct'
                  else if (k.romaji === selectedChoice) cls += ' quiz-choice--wrong'
                }
                return (
                  <button key={k.romaji + k.char} className={cls}
                    onClick={() => handleChoice(k.romaji)} disabled={answered !== null}>
                    {k.romaji}
                  </button>
                )
              })}
            </div>
          ) : (
            <form className="quiz-keyboard-form" onSubmit={handleKeyboardSubmit}>
              <input
                className={`quiz-input${answered === 'correct' ? ' quiz-input--correct' : answered === 'wrong' ? ' quiz-input--wrong' : ''}`}
                type="text"
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                disabled={answered !== null}
                autoFocus
                placeholder="romaji…"
                autoComplete="off"
                autoCapitalize="none"
                autoCorrect="off"
              />
              {answered === 'wrong' && (
                <div className="quiz-correct-hint">✓ {q.romaji}</div>
              )}
              <button className="quiz-btn" type="submit"
                disabled={!inputValue.trim() || answered !== null}>
                Check →
              </button>
            </form>
          )}
        </div>
      </div>
    )
  }

  // Setup screen
  const selectedPool = pool.filter(k => selected.has(k.char))
  const groupAllSelected = g => pool.filter(k => k.group === g).every(k => selected.has(k.char))
  const allActive = pool.every(k => selected.has(k.char))
  const noneActive = selected.size === 0
  return (
    <div className="quiz-root">
      {header}
      <div className="kana-selector">
        <div className="kana-script-toggle">
          {['hiragana', 'katakana', 'both'].map(s => (
            <button key={s} className={`kana-script-btn${script === s ? ' kana-script-btn--active' : ''}`}
              onClick={() => toggleScript(s)}>
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>

        <div className="kana-quick-label">Quick select</div>
        <div className="kana-quick-btns">
          <button className={`kana-quick-btn${allActive ? ' kana-quick-btn--active' : ''}`} onClick={() => quickSelect('all')}>All</button>
          <button className={`kana-quick-btn${noneActive ? ' kana-quick-btn--active' : ''}`} onClick={() => quickSelect('none')}>None</button>
          <button className={`kana-quick-btn${groupAllSelected('basic') ? ' kana-quick-btn--active' : ''}`} onClick={() => quickSelect('basic')}>Basic</button>
          <button className={`kana-quick-btn${groupAllSelected('dakuten') ? ' kana-quick-btn--active' : ''}`} onClick={() => quickSelect('dakuten')}>Dakuten</button>
          <button className={`kana-quick-btn${groupAllSelected('combination') ? ' kana-quick-btn--active' : ''}`} onClick={() => quickSelect('combination')}>Combinations</button>
        </div>

        {GROUPS.map(group => {
          const cells = pool.filter(k => k.group === group)
          if (cells.length === 0) return null
          const label = group === 'combination' ? 'Combinations (yōon)' : group.charAt(0).toUpperCase() + group.slice(1)
          return (
            <div key={group}>
              <div className="kana-group-label">{label} — {cells.length} characters</div>
              <div className="kana-grid">
                {cells.map(k => (
                  <button key={k.char} className={`kana-cell${selected.has(k.char) ? ' kana-cell--selected' : ''}`}
                    onClick={() => toggleCell(k.char)}>
                    {k.char}
                    <span className="kana-cell__romaji">{k.romaji}</span>
                  </button>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      <div className="kana-start-bar">
        <span className="kana-count">{selectedPool.length} characters selected</span>
        <div className="quiz-mode-toggle">
          <button className={`quiz-mode-btn${mode === 'multiple-choice' ? ' quiz-mode-btn--active' : ''}`}
            onClick={() => setMode('multiple-choice')}>Multiple choice</button>
          <button className={`quiz-mode-btn${mode === 'keyboard' ? ' quiz-mode-btn--active' : ''}`}
            onClick={() => setMode('keyboard')}>Keyboard</button>
        </div>
        <button className="quiz-btn" onClick={startQuiz} disabled={selectedPool.length === 0}>
          Start Quiz →
        </button>
      </div>
    </div>
  )
}
