import { useEffect, useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Dot,
} from 'recharts'
import { apiClient } from '../services/api'
import { useApi } from '../hooks/useApi'
import '../styles/prediction.css'

const TRAINED_TICKER = 'BBD'

export default function Prediction() {
  const [prediction, setPrediction] = useState(null)
  const [chartData, setChartData] = useState([])
  const [yAxisMin, setYAxisMin] = useState(2.5)
  const [showScaleEditor, setShowScaleEditor] = useState(false)
  const [customMin, setCustomMin] = useState('2.5')
  const [aggregationMethod, setAggregationMethod] = useState('average') // 'average', 'minError', ou 'single'
  const [lastPredictionTime, setLastPredictionTime] = useState(null)

  const predictApi = useApi(apiClient.predict)
  const historyApi = useApi(() => apiClient.getValidationHistory(null, null, 30))

  // Carregar histórico no mount
  useEffect(() => {
    historyApi.execute()
  }, [])

  // Preparar dados do gráfico - manter todos os pontos individuais
  useEffect(() => {
    if (historyApi.data && historyApi.data.length > 0) {
      const now = Date.now()
      const data = historyApi.data.map((record, index) => {
        // Marcar como isPrediction se foi criado nos últimos 30 segundos
        const createdAt = new Date(record.created_at).getTime()
        const isRecent = lastPredictionTime && (now - lastPredictionTime) < 30000
        const isPredictionPoint = isRecent && (now - createdAt) < 30000

        return {
          date: new Date(record.prediction_date).toLocaleDateString('pt-BR'),
          actual: record.actual_close,
          predicted: record.predicted_close,
          timestamp: new Date(record.prediction_date).getTime(),
          error: record.error_percentage || 0,
          key: `${record.prediction_date}-${index}`,
          isPrediction: isPredictionPoint,
        }
      })

      // Ordenar por timestamp, depois por predicted (para visualização)
      data.sort((a, b) => {
        if (a.timestamp !== b.timestamp) return a.timestamp - b.timestamp
        return a.predicted - b.predicted
      })

      // Adicionar xAxisId baseado na primeira posição de cada data única
      let lastDate = null
      let dateStartIndex = 0
      data.forEach((d, i) => {
        if (d.date !== lastDate) {
          dateStartIndex = i
          lastDate = d.date
        }
        d.xAxisId = dateStartIndex // Todos os pontos da mesma data recebem o mesmo xAxisId
        d.index = i
      })

      setChartData(data)
    }
  }, [historyApi.data, lastPredictionTime])

  const handlePredict = async () => {
    const result = await predictApi.execute()
    if (result) {
      setPrediction(result)
      setLastPredictionTime(Date.now())

      // Carregar dados atualizados da API após a previsão
      setTimeout(() => {
        historyApi.execute()
      }, 500)
    }
  }

  const formatPrice = (price) => {
    if (!price) return 'N/A'
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'USD',
    }).format(price)
  }

  const formatDate = (date) => {
    return new Date(date).toLocaleDateString('pt-BR')
  }

  // Auto ajustar escala do eixo Y
  const handleAutoScale = () => {
    if (chartData.length === 0) return

    const prices = chartData
      .map((d) => d.actual || d.predicted)
      .filter((p) => p !== undefined && p !== null)

    if (prices.length === 0) return

    const minPrice = Math.min(...prices)
    const maxPrice = Math.max(...prices)
    const range = maxPrice - minPrice
    const padding = range * 0.1 // 10% de padding

    const newMin = Math.max(0, minPrice - padding)
    setYAxisMin(Math.round(newMin * 100) / 100)
    setCustomMin(Math.round(newMin * 100) / 100)
  }

  // Aplicar escala customizada
  const handleApplyScale = () => {
    const value = parseFloat(customMin)
    if (!isNaN(value)) {
      setYAxisMin(value)
      setShowScaleEditor(false)
    }
  }

  // Resetar para padrão
  const handleResetScale = () => {
    setYAxisMin(2.5)
    setCustomMin('2.5')
  }

  // Calcular tendência com valores consolidados por data
  const calculateTrendline = () => {
    if (chartData.length < 2) return null

    // Se modo 'single', filtrar apenas o ponto com menor erro por data
    let dataToUse = chartData
    if (aggregationMethod === 'single') {
      const grouped = {}
      chartData.forEach((d) => {
        if (!grouped[d.date]) {
          grouped[d.date] = d
        } else {
          // Manter o ponto com menor erro
          if (d.error < grouped[d.date].error) {
            grouped[d.date] = d
          }
        }
      })
      dataToUse = Object.values(grouped)
    }

    // Agrupar por data para consolidação
    const grouped = {}
    dataToUse.forEach((d) => {
      if (!grouped[d.date]) {
        grouped[d.date] = {
          date: d.date,
          timestamp: d.timestamp,
          predictions: [],
          actual: d.actual,
        }
      }
      grouped[d.date].predictions.push(d.predicted)
    })

    // Consolidar usando o método selecionado
    const consolidatedByDate = Object.values(grouped).map((group) => {
      let predicted = group.predictions[0]

      if (group.predictions.length > 1 && aggregationMethod !== 'single') {
        if (aggregationMethod === 'average') {
          predicted = group.predictions.reduce((sum, p) => sum + p, 0) / group.predictions.length
        } else if (aggregationMethod === 'minError') {
          // Usar a previsão com menor erro
          const dataForDate = dataToUse.filter((d) => d.date === group.date)
          const minErrorData = dataForDate.reduce((min, d) => d.error < min.error ? d : min)
          predicted = minErrorData.predicted
        }
      }

      return {
        date: group.date,
        timestamp: group.timestamp,
        predicted,
      }
    })

    // Calcular regressão linear com dados consolidados
    const n = consolidatedByDate.length
    const sumX = consolidatedByDate.reduce((acc, _, i) => acc + i, 0)
    const sumY = consolidatedByDate.reduce((acc, d) => acc + d.predicted, 0)
    const sumXY = consolidatedByDate.reduce((acc, d, i) => acc + i * d.predicted, 0)
    const sumX2 = consolidatedByDate.reduce((acc, _, i) => acc + i * i, 0)

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
    const intercept = (sumY - slope * sumX) / n

    // Mapear tendência - manter todos os pontos originais mas apenas na linha de tendência
    return chartData.map((d) => {
      const dateIndex = consolidatedByDate.findIndex((cd) => cd.date === d.date)
      const isHidden = aggregationMethod === 'single' && !dataToUse.find((du) => du.index === d.index)

      return {
        ...d,
        trend: intercept + slope * dateIndex,
        hidden: isHidden,
        // Quando em modo 'single', mostrar null para pontos escondidos (a linha pula esses pontos)
        displayPredicted: isHidden ? null : d.predicted,
      }
    })
  }

  const trendlineData = calculateTrendline()


  return (
    <div className="prediction-page">
      <div className="prediction-header">
        <h1>🔮 Gerar Previsão</h1>
        <p>Ação: <strong>{TRAINED_TICKER}</strong> (Banco Bradesco ADR - NYSE)</p>
      </div>

      {/* Seção de Controle */}
      <section className="prediction-control">
        <button
          onClick={handlePredict}
          disabled={predictApi.loading}
          className="btn-predict"
        >
          {predictApi.loading ? '⏳ Gerando...' : '🚀 Gerar Previsão'}
        </button>

        {predictApi.error && (
          <div className="error-box">❌ Erro: {predictApi.error}</div>
        )}
      </section>

      {/* Resultado da Previsão */}
      {prediction && (
        <section className="prediction-result">
          <div className="result-card">
            <div className="result-item">
              <label>Preço Previsto (Próximo Pregão):</label>
              <div className="result-value">{formatPrice(prediction.predicted_close)}</div>
            </div>
            <div className="result-item">
              <label>Data da Previsão:</label>
              <div className="result-value">{formatDate(new Date())}</div>
            </div>
            <div className="result-item">
              <label>Look Back (Dias):</label>
              <div className="result-value">{prediction.look_back}</div>
            </div>
          </div>
        </section>
      )}

      {/* Gráfico */}
      <section className="chart-section">
        <div className="chart-header">
          <h2>📊 Histórico vs Previsão</h2>
          <div className="chart-controls">
            <button onClick={handleAutoScale} className="btn-control" title="Auto ajustar escala">
              🔍 Auto Scale
            </button>
            <button onClick={() => setShowScaleEditor(!showScaleEditor)} className="btn-control">
              ⚙️ Editar Escala
            </button>
            <button onClick={handleResetScale} className="btn-control" title="Resetar para padrão (2.5)">
              🔄 Resetar
            </button>
            <span className="scale-display">Min Y: {yAxisMin}</span>
          </div>
        </div>

        {showScaleEditor && (
          <div className="scale-editor">
            <div className="editor-row">
              <label>Valor Mínimo do Eixo Y:</label>
              <input
                type="number"
                step="0.1"
                value={customMin}
                onChange={(e) => setCustomMin(e.target.value)}
                placeholder="Ex: 2.5"
                className="editor-input"
              />
              <button onClick={handleApplyScale} className="btn-apply">
                ✅ Aplicar
              </button>
              <button onClick={() => setShowScaleEditor(false)} className="btn-cancel">
                ❌ Cancelar
              </button>
            </div>
            <small>Insira um valor para definir onde o eixo Y começará (0 = valor mínimo dos dados)</small>
          </div>
        )}

        <div className="aggregation-selector">
          <label>Consolidar múltiplas previsões por data:</label>
          <div className="selector-buttons">
            <button
              onClick={() => setAggregationMethod('average')}
              className={`selector-btn ${aggregationMethod === 'average' ? 'active' : ''}`}
            >
              📊 Média
            </button>
            <button
              onClick={() => setAggregationMethod('minError')}
              className={`selector-btn ${aggregationMethod === 'minError' ? 'active' : ''}`}
            >
              ✅ Menor Erro
            </button>
            <button
              onClick={() => setAggregationMethod('single')}
              className={`selector-btn ${aggregationMethod === 'single' ? 'active' : ''}`}
            >
              🏆 Único Campeão
            </button>
          </div>
        </div>

        {historyApi.loading ? (
          <div className="loading">⏳ Carregando histórico...</div>
        ) : chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={500}>
            <LineChart data={trendlineData || chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="xAxisId"
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
                type="number"
                domain="dataMin"
                tickFormatter={(xAxisId) => {
                  // Mostrar a data do primeiro ponto com este xAxisId
                  const data = trendlineData || chartData
                  const firstPointWithId = data.find((d) => d.xAxisId === xAxisId)
                  return firstPointWithId ? firstPointWithId.date : ''
                }}
                tick={{ fontSize: 12 }}
              />
              <YAxis
                stroke="#6b7280"
                style={{ fontSize: '12px' }}
                domain={[yAxisMin, 'auto']}
                label={{ value: 'Preço (USD)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  padding: '12px',
                  fontSize: '12px',
                }}
                formatter={(value) => value ? `$${value.toFixed(4)}` : 'N/A'}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload
                    return (
                      <div style={{
                        background: '#fff',
                        border: '1px solid #e5e7eb',
                        borderRadius: '8px',
                        padding: '12px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                      }}>
                        <p style={{ margin: '0 0 8px 0', fontWeight: 'bold', color: '#2563eb' }}>
                          📅 {data.date}
                        </p>
                        {data.actual && (
                          <p style={{ margin: '4px 0', color: '#10b981' }}>
                            🟢 Real: ${data.actual.toFixed(4)}
                          </p>
                        )}
                        {data.predicted && (
                          <p style={{ margin: '4px 0', color: '#2563eb' }}>
                            🔵 Previsão: ${data.predicted.toFixed(4)}
                          </p>
                        )}
                        {data.actual && data.predicted && (
                          <>
                            <p style={{ margin: '8px 0 0 0', paddingTop: '8px', borderTop: '1px solid #e5e7eb', color: '#666' }}>
                              📊 Taxa de Erro: {((Math.abs(data.actual - data.predicted) / data.actual) * 100).toFixed(2)}%
                            </p>
                            <p style={{ margin: '4px 0', color: '#666' }}>
                              Diferença: ${Math.abs(data.actual - data.predicted).toFixed(4)}
                            </p>
                          </>
                        )}
                      </div>
                    )
                  }
                  return null
                }}
              />
              <Legend />

              {/* Histórico Real */}
              <Line
                type="monotone"
                dataKey="actual"
                stroke="#10b981"
                strokeWidth={2}
                name="Preço Real"
                connectNulls={true}
              />

              {/* Previsões */}
              <Line
                type="monotone"
                dataKey={aggregationMethod === 'single' ? 'displayPredicted' : 'predicted'}
                stroke="#2563eb"
                strokeWidth={2}
                name="Previsão LSTM"
                connectNulls={true}
                dot={(props) => {
                  const { cx, cy, payload } = props
                  const data = trendlineData || chartData

                  // Esconder pontos quando em modo 'single'
                  if (payload.hidden) {
                    return null
                  }

                  if (payload.isPrediction) {
                    return (
                      <circle
                        cx={cx}
                        cy={cy}
                        r={8}
                        fill="#f59e0b"
                        stroke="#fff"
                        strokeWidth={2}
                      />
                    )
                  }

                  // Encontrar todos os pontos neste xAxisId
                  const pointsInGroup = data.filter((d) => d.xAxisId === payload.xAxisId && !d.isPrediction)

                  // Encontrar valores Y únicos neste grupo
                  const uniqueYValues = [...new Set(pointsInGroup.map((d) => d.predicted))].sort((a, b) => a - b)

                  // Contar quantos pontos têm este valor Y
                  const pointsWithThisY = pointsInGroup.filter((d) => d.predicted === payload.predicted)
                  const isMultipleWithSameY = pointsWithThisY.length > 1

                  // Se há múltiplos valores Y, distribuir verticalmente
                  let cyOffset = cy
                  if (uniqueYValues.length > 1) {
                    const yIndex = uniqueYValues.indexOf(payload.predicted)
                    const spreadAmount = 20
                    cyOffset = cy + (yIndex - (uniqueYValues.length - 1) / 2) * spreadAmount
                  }

                  // Aumentar tamanho e opacidade se há múltiplos com mesmo Y
                  const radius = isMultipleWithSameY ? 6 : 4
                  const opacity = isMultipleWithSameY ? 0.7 : 1
                  const stroke = isMultipleWithSameY ? 'white' : 'none'
                  const strokeWidth = isMultipleWithSameY ? 2 : 0

                  return (
                    <circle
                      cx={cx}
                      cy={cyOffset}
                      r={radius}
                      fill="#2563eb"
                      opacity={opacity}
                      stroke={stroke}
                      strokeWidth={strokeWidth}
                    />
                  )
                }}
              />

              {/* Linha de Tendência */}
              {trendlineData && (
                <Line
                  type="monotone"
                  dataKey="trend"
                  stroke="#9333ea"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  name="Tendência"
                  dot={false}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="no-data">
            📊 Gere uma previsão para ver o gráfico
          </div>
        )}
      </section>

      {/* Legenda */}
      <section className="chart-legend">
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#10b981' }}></div>
          <span>Preço Real Histórico</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#2563eb' }}></div>
          <span>Previsões LSTM</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#f59e0b' }}></div>
          <span>Última Previsão (Destaque)</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#9333ea' }}></div>
          <span>Linha de Tendência</span>
        </div>
      </section>

      {/* Info */}
      <section className="info-section">
        <div className="info-box">
          <h3>ℹ️ Sobre o Gráfico</h3>
          <ul>
            <li>🟢 <strong>Verde:</strong> Preços reais históricos do BBD</li>
            <li>🔵 <strong>Azul:</strong> Previsões feitas pela rede LSTM</li>
            <li>🟠 <strong>Laranja:</strong> Última previsão gerada (mais recente)</li>
            <li>🟣 <strong>Roxo:</strong> Linha de tendência dos dados</li>
            <li>📈 <strong>Modelo:</strong> LSTM Bidirecional com 30 dias de histórico</li>
          </ul>
        </div>
      </section>
    </div>
  )
}
