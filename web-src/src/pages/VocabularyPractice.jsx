import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import FlashCard from '../components/FlashCard'

const STORAGE_KEY = 'japanese-practice-selected-words'

function loadWords(state) {
  if (state?.words?.length) return state.words
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [] } catch { return [] }
}

export default function VocabularyPractice() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [words] = useState(() => loadWords(state))
  const [idx, setIdx] = useState(0)
  const [direction, setDirection] = useState('jp-en') // 'jp-en' | 'en-jp'
  const [flipped, setFlipped] = useState(false)

  if (words.length === 0) {
    navigate('/vocabulary-builder')
    return null
  }

  const word = words[idx]
  const isLast = idx + 1 >= words.length

  function advance() {
    if (isLast) { navigate('/vocabulary-builder'); return }
    setIdx(i => i + 1)
    setFlipped(false)
  }

  function handleAdvance() {
    if (!flipped) { setFlipped(true) } else { advance() }
  }

  const front = direction === 'jp-en' ? (
    <>
      <div className="fc-front-main">{word.kanji || word.kana}</div>
      {word.kanji && <div className="fc-front-sub">{word.kana}</div>}
    </>
  ) : (
    <>
      <div className="fc-back-meaning">{word.meanings_en}</div>
      <div className="fc-back-sub">{word.romaji}</div>
    </>
  )

  const back = direction === 'jp-en' ? (
    <>
      <div className="fc-back-meaning">{word.meanings_en}</div>
      <div className="fc-back-sub">{word.romaji}</div>
      {word.jlpt && <span className="fc-back-jlpt">{word.jlpt}</span>}
    </>
  ) : (
    <>
      <div className="fc-front-main">{word.kanji || word.kana}</div>
      {word.kanji && <div className="fc-front-sub">{word.kana}</div>}
    </>
  )

  const btnLabel = flipped ? (isLast ? 'Done' : 'Next →') : 'Next →'

  return (
    <div className="quiz-root">
      <div className="quiz-header">
        <Link to="/vocabulary-builder" className="quiz-brand"><span className="jp">日本語</span>Practice</Link>
        <div className="practice-direction">
          <button className={`practice-dir-btn${direction === 'jp-en' ? ' practice-dir-btn--active' : ''}`}
            onClick={() => { setDirection('jp-en'); setFlipped(false) }} aria-label="JP to EN">JP → EN</button>
          <button className={`practice-dir-btn${direction === 'en-jp' ? ' practice-dir-btn--active' : ''}`}
            onClick={() => { setDirection('en-jp'); setFlipped(false) }} aria-label="EN to JP">EN → JP</button>
        </div>
      </div>

      <div className="quiz-body">
        <div className="quiz-progress">
          <span>{idx + 1} / {words.length}</span>
        </div>
        <div className="quiz-progress-bar">
          <div className="quiz-progress-bar__fill" style={{ width: `${(idx / words.length) * 100}%` }} />
        </div>

        <FlashCard front={front} back={back} flipped={flipped} onFlip={handleAdvance} />
        <p className="fc-hint">{flipped ? 'Tap or press Next to continue' : 'Tap the card or press Next to reveal'}</p>

        <button className="quiz-btn" onClick={handleAdvance} aria-label={btnLabel}>
          {btnLabel}
        </button>
      </div>
    </div>
  )
}
