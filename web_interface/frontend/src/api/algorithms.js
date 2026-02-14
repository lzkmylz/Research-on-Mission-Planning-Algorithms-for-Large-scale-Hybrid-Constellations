import client from './client'

export const algorithmApi = {
  // Get all algorithms
  getAll() {
    return client.get('/algorithms/')
  },

  // Get algorithm by ID
  getById(id) {
    return client.get(`/algorithms/${id}`)
  },

  // Get algorithm parameters
  getParameters(algorithmId) {
    return client.get(`/algorithms/${algorithmId}/parameters`)
  },

  // Validate algorithm parameters
  validateParameters(algorithmId, parameters) {
    return client.post(`/algorithms/${algorithmId}/validate`, { parameters })
  },

  // Get algorithm performance stats
  getStats(algorithmId) {
    return client.get(`/algorithms/${algorithmId}/stats`)
  },

  // Compare algorithms
  compare(algorithmIds, scenarioId) {
    return client.post('/algorithms/compare', {
      algorithm_ids: algorithmIds,
      scenario_id: scenarioId
    })
  }
}

export default algorithmApi
