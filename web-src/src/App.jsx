import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import VocabularyBuilder from './pages/VocabularyBuilder'
import VocabularyPractice from './pages/VocabularyPractice'
import KanaQuiz from './pages/KanaQuiz'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/vocabulary-builder" element={<VocabularyBuilder />} />
      <Route path="/vocabulary-builder/practice" element={<VocabularyPractice />} />
      <Route path="/kana-quiz" element={<KanaQuiz />} />
    </Routes>
  )
}
