import axios from 'axios'

const API_BASE = '/api/v1'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const apiClient = {
  // Previsão
  predict: async () => {
    const response = await api.post('/predict/next_close')
    return response.data
  },

  // Métricas
  getMetrics: async () => {
    const response = await api.get('/metrics/latest')
    return response.data
  },

  // Validação
  getValidationStats: async () => {
    const response = await api.get('/validation/stats')
    return response.data
  },

  getValidationHistory: async (startDate, endDate, limit = 100) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    params.append('limit', limit)

    const response = await api.get(`/validation/history?${params}`)
    return response.data
  },

  getValidationSummary: async (startDate, endDate) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)

    const response = await api.get(`/validation/summary?${params}`)
    return response.data
  },

  getMetricsAverage: async () => {
    const response = await api.get('/validation/get-metrics')
    return response.data
  },

  validatePending: async () => {
    const response = await api.post('/validation/validate')
    return response.data
  },

  validateAllPending: async () => {
    const response = await api.post('/validation/validate')
    return response.data
  },

  // Logs
  getLogs: async (limit = 100) => {
    const response = await api.get(`/logs?limit=${limit}`)
    return response.data
  },

  // Health
  getHealth: async () => {
    try {
      const response = await api.get('/health')
      return response.data
    } catch {
      return null
    }
  },
}

export default api
