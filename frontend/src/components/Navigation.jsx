import { Link, useLocation } from 'react-router-dom'
import '../styles/navigation.css'

export default function Navigation() {
  const location = useLocation()

  const isActive = (path) => location.pathname === path ? 'active' : ''

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/">
            <span className="brand-icon">📈</span>
            <span className="brand-text">LSTM Predictions</span>
          </Link>
        </div>

        <ul className="nav-links">
          <li>
            <Link to="/" className={`nav-link ${isActive('/')}`}>
              📊 Dashboard
            </Link>
          </li>
          <li>
            <Link to="/predict" className={`nav-link ${isActive('/predict')}`}>
              🔮 Previsões
            </Link>
          </li>
          <li>
            <Link to="/history" className={`nav-link ${isActive('/history')}`}>
              📜 Histórico
            </Link>
          </li>
          <li>
            <Link to="/logs" className={`nav-link ${isActive('/logs')}`}>
              📋 Logs
            </Link>
          </li>
        </ul>

        <div className="nav-status">
          <span className="status-badge">🟢 Online</span>
        </div>
      </div>
    </nav>
  )
}
