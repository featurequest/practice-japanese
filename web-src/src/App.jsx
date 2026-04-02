import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import VocabularyBuilder from './pages/VocabularyBuilder'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/vocabulary-builder" element={<VocabularyBuilder />} />
    </Routes>
  )
}
