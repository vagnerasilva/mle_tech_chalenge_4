import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import '../styles/navigation.css'

export default function Navigation() {
  const location = useLocation()
  const [b3Status, setB3Status] = useState('online')

  useEffect(() => {
    const checkB3Status = () => {
      try {
        const now = new Date()
        const brasiliaTime = now.toLocaleString('pt-BR', {
          timeZone: 'America/Sao_Paulo',
          hour: '2-digit',
          minute: '2-digit',
          weekday: 'short',
        })

        // Parse: "seg, 15:30" ou similar
        const parts = brasiliaTime.split(', ')
        const dayStr = parts[0]
        const timeStr = parts[1] || ''

        // Dias úteis: seg, ter, qua, qui, sex
        const isWeekday = ['seg', 'ter', 'qua', 'qui', 'sex'].includes(dayStr)

        // Horário de pregão: 09:30 às 18:00
        const [hoursStr, minutesStr] = timeStr.split(':')
        const hours = parseInt(hoursStr)
        const minutes = parseInt(minutesStr)

        const isOpeningHours = (hours > 9 || (hours === 9 && minutes >= 30)) && hours < 18

        setB3Status(isWeekday && isOpeningHours ? 'online' : 'offline')
      } catch (error) {
        console.error('Erro ao verificar status B3:', error)
        setB3Status('offline')
      }
    }

    checkB3Status()
    const interval = setInterval(checkB3Status, 60000)
    return () => clearInterval(interval)
  }, [])

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
          <span className={`status-badge ${b3Status}`}>
            {b3Status === 'online' ? '🟢 B3 Online' : '🔴 B3 Offline'}
          </span>
        </div>
      </div>
    </nav>
  )
}
