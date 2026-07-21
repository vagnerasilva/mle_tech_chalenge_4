import { useState } from 'react'
import PredictionForm from './components/PredictionForm'
import ResultCard from './components/ResultCard'
import './App.css'

function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePrediction = async (data) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/api/v1/predict/next_close', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const apiData = await response.json()

      // Transformar resposta da API para o formato esperado pelo frontend
      const formattedResult = {
        ticker: apiData.symbol,
        last_price: apiData.predicted_close, // Preço previsto do próximo dia
        predictions: [apiData.predicted_close],
        rmse: null,
        mae: null,
        prediction_date: new Date().toISOString(),
        last_trading_date: apiData.last_trading_date,
        look_back: apiData.look_back,
      }

      setResult(formattedResult)
    } catch (err) {
      setError(err.message || 'Erro ao conectar com a API')
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>📈 Previsão de Preços - LSTM</h1>
        <p>Predição de preços de ações com redes neurais LSTM</p>
        <div className="ticker-badge">
          🎯 Modelo Treinado Para: <strong>BBD (Banco Bradesco ADR - NYSE)</strong>
        </div>
      </header>

      <main className="main">
        <PredictionForm onSubmit={handlePrediction} loading={loading} />

        {error && (
          <div className="alert alert-error">
            ❌ Erro: {error}
          </div>
        )}

        {loading && (
          <div className="alert alert-info">
            ⏳ Carregando predição...
          </div>
        )}

        {result && <ResultCard data={result} />}
      </main>

      <footer className="footer">
        <p>LSTM API v1.0 | Modelo treinado com dados históricos</p>
      </footer>
    </div>
  )
}

export default App
