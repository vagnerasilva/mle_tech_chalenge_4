import { useEffect, useState } from 'react'
import { apiClient } from '../services/api'
import { useApi } from '../hooks/useApi'
import '../styles/history.css'

export default function History() {
  const [filterDate, setFilterDate] = useState('')
  const historyApi = useApi(() => apiClient.getValidationHistory(null, null, 100))

  useEffect(() => {
    historyApi.execute()
  }, [])

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }

  const formatDate = (dateString) => {
    const [year, month, day] = dateString.split('-')
    return `${day}/${month}/${year}`
  }

  const filteredData = filterDate
    ? historyApi.data?.filter((r) => r.prediction_date === filterDate)
    : historyApi.data

  return (
    <div className="history-page">
      <div className="history-header">
        <h1>📜 Histórico Completo de Previsões</h1>
        <p>Veja todas as previsões realizadas</p>
      </div>

      <section className="history-filter">
        <label>Filtrar por data:</label>
        <input
          type="date"
          value={filterDate}
          onChange={(e) => setFilterDate(e.target.value)}
          placeholder="YYYY-MM-DD"
        />
        {filterDate && (
          <button onClick={() => setFilterDate('')} className="btn-clear">
            ✕ Limpar filtro
          </button>
        )}
      </section>

      {historyApi.loading ? (
        <div className="loading">⏳ Carregando histórico...</div>
      ) : historyApi.error ? (
        <div className="error">❌ Erro: {historyApi.error}</div>
      ) : filteredData && filteredData.length > 0 ? (
        <section className="history-table-section">
          <div className="history-count">
            Mostrando {filteredData.length} de {historyApi.data.length} registros
          </div>
          <div className="history-table-wrapper">
            <table className="history-table">
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Previsão</th>
                  <th>Valor Real</th>
                  <th>Erro (%)</th>
                  <th>MAE</th>
                  <th>RMSE</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredData.map((record, idx) => (
                  <tr key={idx}>
                    <td>{formatDate(record.prediction_date)}</td>
                    <td className="price">{formatPrice(record.predicted_close)}</td>
                    <td className="price">
                      {record.actual_close ? formatPrice(record.actual_close) : '⏳'}
                    </td>
                    <td>
                      {record.error_percentage
                        ? record.error_percentage.toFixed(2) + '%'
                        : '-'}
                    </td>
                    <td>{record.mae ? record.mae.toFixed(4) : '-'}</td>
                    <td>{record.rmse ? record.rmse.toFixed(4) : '-'}</td>
                    <td className={record.actual_close ? 'validated' : 'pending'}>
                      {record.actual_close ? '✅ Validado' : '⏳ Pendente'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      ) : (
        <div className="no-data">📭 Nenhuma previsão encontrada</div>
      )}
    </div>
  )
}
