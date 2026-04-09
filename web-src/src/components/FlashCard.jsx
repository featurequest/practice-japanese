export default function FlashCard({ front, back, flipped = false, onFlip }) {
  return (
    <button
      className={`flashcard${flipped ? ' flashcard--flipped' : ''}`}
      onClick={onFlip}
      aria-label="flip"
      aria-pressed={flipped}
    >
      <div className="flashcard__inner">
        <div className="flashcard__face flashcard__face--front">{front}</div>
        <div className="flashcard__face flashcard__face--back">
          {flipped ? back : null}
        </div>
      </div>
    </button>
  )
}
