import '../styles/result.css'

export default function ResultCard({ data }) {
  if (!data) return null

  const {
    ticker,
    last_price,
    predictions,
    prediction_date,
    last_trading_date,
    look_back,
  } = data

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('pt-BR')
  }

  const companyName = ticker === 'BBD' ? 'Banco Bradesco ADR (NYSE)' : ticker

  return (
    <div className="result-card">
      <div className="result-header">
        <h2>📊 Resultados da Previsão</h2>
        <p className="result-date">
          Previsão em: {formatDate(prediction_date)} | Último pregão: {formatDate(last_trading_date)}
        </p>
      </div>

      <div className="result-info">
        <div className="info-item">
          <label>Ticker:</label>
          <strong>{ticker}</strong>
          <span className="company-info">{companyName}</span>
        </div>
        <div className="info-item">
          <label>Preço Previsto (Próximo Pregão):</label>
          <strong>{formatPrice(last_price)}</strong>
        </div>
      </div>

      <div className="metrics">
        <div className="metric">
          <label>Dias Históricos (Look Back):</label>
          <span>{look_back}</span>
        </div>
        <div className="metric">
          <label>Modelo:</label>
          <span>LSTM Bidirecional</span>
        </div>
      </div>

      <div className="predictions">
        <h3>🎯 Previsão Gerada:</h3>
        <div className="prediction-box">
          <p className="prediction-text">
            Com base nos últimos <strong>{look_back} pregões</strong> do {ticker},
            o modelo prevê um preço de fechamento de <strong>{formatPrice(last_price)}</strong>
            para o próximo pregão.
          </p>
          <div className="prediction-detail">
            <span>📅 Última cotação: {formatDate(last_trading_date)}</span><br/>
            <span>🔬 Modelo: LSTM Bidirecional com normalização log1p</span>
          </div>
        </div>
      </div>
    </div>
  )
}
