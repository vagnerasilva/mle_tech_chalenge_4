import { useEffect } from 'react'
import { apiClient } from '../services/api'
import { useApi } from '../hooks/useApi'
import '../styles/logs.css'

export default function Logs() {
  const logsApi = useApi(() => apiClient.getLogs(100))

  useEffect(() => {
    logsApi.execute()
  }, [])

  const formatDate = (dateString) => {
    const [year, month, day] = dateString.split('-').slice(0, 3)
    const timePart = dateString.split('T')[1]?.split('.')[0] || ''
    return `${day}/${month}/${year} ${timePart}`
  }

  const getStatusColor = (statusCode) => {
    if (statusCode >= 200 && statusCode < 300) return '#10b981' // success
    if (statusCode >= 400 && statusCode < 500) return '#f59e0b' // warning
    if (statusCode >= 500) return '#ef4444' // error
    return '#3b82f6' // info
  }

  const getMethodColor = (method) => {
    const colors = {
      GET: '#3b82f6',
      POST: '#10b981',
      PUT: '#f59e0b',
      DELETE: '#ef4444',
      PATCH: '#8b5cf6',
    }
    return colors[method] || '#6b7280'
  }

  return (
    <div className="logs-page">
      <div className="logs-header">
        <h1>📋 Logs de Requisições HTTP</h1>
        <p>Acompanhe todas as chamadas para a API</p>
      </div>

      {logsApi.loading ? (
        <div className="loading">⏳ Carregando logs...</div>
      ) : logsApi.error ? (
        <div className="error">❌ Erro: {logsApi.error}</div>
      ) : logsApi.data && logsApi.data.length > 0 ? (
        <section className="logs-section">
          <div className="logs-count">
            Total: {logsApi.data.length} requisições
          </div>
          <div className="logs-table-wrapper">
            <table className="logs-table">
              <thead>
                <tr>
                  <th>Método</th>
                  <th>Caminho</th>
                  <th>Status</th>
                  <th>Tempo (ms)</th>
                  <th>IP</th>
                  <th>Data/Hora</th>
                </tr>
              </thead>
              <tbody>
                {logsApi.data.map((log, idx) => (
                  <tr key={idx}>
                    <td>
                      <span
                        className="method-badge"
                        style={{ backgroundColor: getMethodColor(log.method) }}
                      >
                        {log.method}
                      </span>
                    </td>
                    <td className="path">{log.path}</td>
                    <td>
                      <span
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(log.status_code) }}
                      >
                        {log.status_code}
                      </span>
                    </td>
                    <td>{(log.process_time * 1000).toFixed(2)}</td>
                    <td className="ip">{log.ip_address}</td>
                    <td className="timestamp">{formatDate(log.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : (
        <div className="no-data">📭 Nenhum log disponível</div>
      )}
    </div>
  )
}
