import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../services/api'
import { useApi } from '../hooks/useApi'
import '../styles/dashboard.css'

export default function Dashboard() {
  const [validationResult, setValidationResult] = useState(null)
  const metricsApi = useApi(apiClient.getMetrics)
  const statsApi = useApi(apiClient.getValidationStats)
  const historyApi = useApi(() => apiClient.getValidationHistory(null, null, 10))
  const validateApi = useApi(apiClient.validateAllPending)

  useEffect(() => {
    metricsApi.execute()
    statsApi.execute()
    historyApi.execute()
  }, [])

  const handleValidatePending = async () => {
    const result = await validateApi.execute()
    if (result) {
      setValidationResult(result)
      // Recarregar dados após validação
      setTimeout(() => {
        statsApi.execute()
        historyApi.execute()
      }, 500)
    }
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }

  const formatDate = (dateString) => {
    // Parse a data no formato YYYY-MM-DD sem conversão de timezone
    const [year, month, day] = dateString.split('-')
    return `${day}/${month}/${year}`
  }

  const isWeekend = (dateString) => {
    // Parse sem timezone: YYYY-MM-DD
    const [year, month, day] = dateString.split('-').map(Number)
    const date = new Date(year, month - 1, day)
    const dayOfWeek = date.getDay()
    return dayOfWeek === 0 || dayOfWeek === 6 // 0 = domingo, 6 = sábado (FDS = sábado e domingo)
  }

  const getStatusLabel = (record) => {
    if (record.actual_close) {
      return '✅ Validado'
    }
    return isWeekend(record.prediction_date) ? '🅵🅳🆂 FDS' : '⏳ Pendente'
  }

  return (
    <div className="dashboard">
      {/* Hero Section - Destaque para Previsão */}
      <section className="hero">
        <div className="hero-content">
          <h1>📈 Previsão de Preços BBD</h1>
          <p>LSTM Bidirecional - Previsões em Tempo Real</p>
          <Link to="/predict" className="btn-hero">
            🔮 Gerar Nova Previsão
          </Link>
        </div>
      </section>

      {/* Métricas do Modelo */}
      <section className="metrics-grid">
        <h2>📊 Performance do Modelo</h2>

        {metricsApi.loading ? (
          <div className="loading">⏳ Carregando métricas...</div>
        ) : metricsApi.error ? (
          <div className="error">❌ Erro ao carregar: {metricsApi.error}</div>
        ) : metricsApi.data ? (
          <div className="metrics">
            <MetricCard
              label="MAE"
              value={metricsApi.data.mae?.toFixed(4)}
              description="Erro Absoluto Médio"
            />
            <MetricCard
              label="RMSE"
              value={metricsApi.data.rmse?.toFixed(4)}
              description="Raiz do Erro Quadrático Médio"
            />
            <MetricCard
              label="MAPE"
              value={metricsApi.data.mape?.toFixed(2) + '%'}
              description="Erro Percentual Médio Absoluto"
            />
            <MetricCard
              label="Acurácia Direcional"
              value={metricsApi.data.directional_accuracy?.toFixed(2) + '%'}
              description="Capacidade de prever direção"
            />
          </div>
        ) : null}
      </section>

      {/* Seção de Validação de Pendentes */}
      <section className="validation-section">
        <h2>🔄 Validar Predições Pendentes</h2>
        <div className="validation-container">
          <p>Clique abaixo para validar as predições pendentes buscando preços reais no yfinance:</p>

          <button
            onClick={handleValidatePending}
            disabled={validateApi.loading}
            className="btn-validate"
          >
            {validateApi.loading ? '⏳ Validando...' : '✅ Validar Pendentes'}
          </button>

          {validateApi.error && (
            <div className="error-box">
              ❌ Erro: {validateApi.error}
            </div>
          )}

          {validationResult && (
            <div className="validation-result">
              <div className="result-summary">
                <div className="result-item">
                  <span className="result-label">Total Pendente:</span>
                  <span className="result-value">{validationResult.total_pending}</span>
                </div>
                <div className="result-item">
                  <span className="result-label">✅ Validadas:</span>
                  <span className="result-value success">{validationResult.updated}</span>
                </div>
                <div className="result-item">
                  <span className="result-label">⏳ Ainda Pendentes:</span>
                  <span className="result-value pending">{validationResult.pending}</span>
                </div>
                <div className="result-item">
                  <span className="result-label">❌ Falhadas:</span>
                  <span className="result-value error">{validationResult.failed}</span>
                </div>
              </div>

              {validationResult.updated > 0 && (
                <div className="success-box">
                  ✅ {validationResult.updated} previsão(ões) foram validadas com sucesso!
                </div>
              )}

              {validationResult.pending > 0 && (
                <div className="warning-box">
                  ⏳ {validationResult.pending} previsão(ões) ainda pendente(s).
                  Isso pode significar que os dados ainda não estão disponíveis no yfinance.
                </div>
              )}

              {validationResult.updated === 0 && (
                <div className="info-box">
                  ℹ️ Nenhuma previsão nova foi validada nesta tentativa.
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Estatísticas Gerais */}
      <section className="stats-section">
        <h2>📈 Estatísticas Gerais</h2>

        {statsApi.loading ? (
          <div className="loading">⏳ Carregando estatísticas...</div>
        ) : statsApi.error ? (
          <div className="error">❌ Erro: {statsApi.error}</div>
        ) : statsApi.data ? (
          <div className="stats-grid">
            <StatBox
              title="Total de Predições"
              value={statsApi.data.total_predictions}
              icon="📊"
            />
            <StatBox
              title="Validadas"
              value={statsApi.data.validated}
              icon="✅"
            />
            <StatBox
              title="Pendentes"
              value={statsApi.data.pending}
              icon="⏳"
            />
            <StatBox
              title="Taxa de Acerto"
              value={statsApi.data.success_rate !== undefined ? statsApi.data.success_rate.toFixed(1) + '%' : 'N/A'}
              icon="🎯"
            />
          </div>
        ) : null}
      </section>

      {/* Histórico Recente */}
      <section className="history-section">
        <h2>📜 Predições Recentes</h2>

        {historyApi.loading ? (
          <div className="loading">⏳ Carregando histórico...</div>
        ) : historyApi.error ? (
          <div className="error">❌ Erro: {historyApi.error}</div>
        ) : historyApi.data && historyApi.data.length > 0 ? (
          <div className="history-table">
            <table>
              <thead>
                <tr>
                  <th>Data</th>
                  <th>Previsão</th>
                  <th>Real</th>
                  <th>Erro (%)</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {historyApi.data.slice(0, 10).map((record) => (
                  <tr key={record.prediction_date}>
                    <td>{formatDate(record.prediction_date)}</td>
                    <td>{formatPrice(record.predicted_close)}</td>
                    <td>
                      {record.actual_close
                        ? formatPrice(record.actual_close)
                        : '⏳ Pendente'}
                    </td>
                    <td>
                      {record.error_percentage
                        ? record.error_percentage.toFixed(2) + '%'
                        : '-'}
                    </td>
                    <td className={record.actual_close ? 'validated' : (isWeekend(record.prediction_date) ? 'weekend' : 'pending')}>
                      {getStatusLabel(record)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>Nenhuma predição registrada ainda.</p>
        )}
      </section>

      {/* Call to Action */}
      <section className="cta">
        <h2>Pronto para fazer uma previsão?</h2>
        <Link to="/predict" className="btn-cta">
          🚀 Ir para Previsões
        </Link>
      </section>
    </div>
  )
}

function MetricCard({ label, value, description }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value || 'N/A'}</div>
      <div className="metric-desc">{description}</div>
    </div>
  )
}

function StatBox({ title, value, icon }) {
  return (
    <div className="stat-box">
      <div className="stat-icon">{icon}</div>
      <div className="stat-title">{title}</div>
      <div className="stat-value">{value}</div>
    </div>
  )
}
