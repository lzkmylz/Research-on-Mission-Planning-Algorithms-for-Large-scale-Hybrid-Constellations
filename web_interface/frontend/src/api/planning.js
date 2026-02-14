import client from './client'

export const planningApi = {
  // Create planning job
  createJob(scenarioId, algorithmId, parameters = {}) {
    return client.post('/planning/jobs', {
      scenario_id: scenarioId,
      algorithm_id: algorithmId,
      parameters
    })
  },

  // Get job by ID
  getJob(jobId) {
    return client.get(`/planning/jobs/${jobId}`)
  },

  // Get all jobs
  getAllJobs(params = {}) {
    return client.get('/planning/jobs', { params })
  },

  // Cancel job
  cancelJob(jobId) {
    return client.post(`/planning/jobs/${jobId}/cancel`)
  },

  // Get job progress
  getProgress(jobId) {
    return client.get(`/planning/jobs/${jobId}/progress`)
  },

  // Get job results
  getResults(jobId) {
    return client.get(`/planning/jobs/${jobId}/results`)
  },

  // Validate planning request
  validate(data) {
    return client.post('/planning/validate', data)
  },

  // Get planning preview (quick estimate)
  getPreview(scenarioId) {
    return client.get(`/planning/preview`, { params: { scenario_id: scenarioId } })
  },

  // Export planning job
  exportJob(jobId, format = 'json') {
    return client.get(`/planning/jobs/${jobId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  }
}

export default planningApi
