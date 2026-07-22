import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Navigation from './components/Navigation'
import Dashboard from './pages/Dashboard'
import Prediction from './pages/Prediction'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/predict" element={<Prediction />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
