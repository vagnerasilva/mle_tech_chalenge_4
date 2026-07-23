import { useState, useCallback } from 'react'

export function useApi(apiCall) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(async (...args) => {
    setLoading(true)
    setError(null)

    try {
      const result = await apiCall(...args)
      setData(result)
      return result
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Erro ao fazer requisição'
      setError(errorMessage)
      console.error('API Error:', err)
    } finally {
      setLoading(false)
    }
  }, [apiCall])

  return { data, loading, error, execute }
}
