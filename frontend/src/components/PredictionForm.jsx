import '../styles/form.css'

const TRAINED_TICKER = 'BBD'
const TRAINED_COMPANY = 'Banco Bradesco ADR (NYSE)'

export default function PredictionForm({ onSubmit, loading }) {
  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit({ ticker: TRAINED_TICKER })
  }

  return (
    <form className="form" onSubmit={handleSubmit}>
      <div className="form-group">
        <label>Ação Monitorada:</label>
        <div className="ticker-display">
          <strong>{TRAINED_TICKER}</strong>
          <span className="company-name">{TRAINED_COMPANY}</span>
        </div>
        <small className="info-text">
          ℹ️ Este modelo foi treinado especificamente para {TRAINED_TICKER}
        </small>
      </div>

      <div className="form-group">
        <label>O que será previsto:</label>
        <div className="prediction-info">
          📊 Preço de fechamento do <strong>próximo pregão</strong> baseado
          nos últimos 30 dias de histórico.
        </div>
      </div>

      <button type="submit" className="btn-submit" disabled={loading}>
        {loading ? '⏳ Carregando...' : '🔮 Gerar Previsão de ' + TRAINED_TICKER}
      </button>

      <div className="model-info">
        <p>
          <strong>ℹ️ Sobre o Modelo:</strong><br/>
          Rede Neural LSTM Bidirecional treinada com dados históricos de {TRAINED_TICKER}.
          A precisão é otimizada para este ticker específico.
        </p>
      </div>
    </form>
  )
}
