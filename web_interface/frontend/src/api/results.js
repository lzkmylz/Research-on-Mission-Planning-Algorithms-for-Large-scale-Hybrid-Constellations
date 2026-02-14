import client from './client'

export const resultsApi = {
  // Get results by job ID
  getByJobId(jobId) {
    return client.get(`/results/${jobId}`)
  },

  // Get observation schedule
  getSchedule(jobId, params = {}) {
    return client.get(`/results/${jobId}/schedule`, { params })
  },

  // Get satellite utilization
  getSatelliteUtilization(jobId) {
    return client.get(`/results/${jobId}/satellite-utilization`)
  },

  // Get ground station utilization
  getGroundStationUtilization(jobId) {
    return client.get(`/results/${jobId}/ground-station-utilization`)
  },

  // Get target coverage
  getTargetCoverage(jobId) {
    return client.get(`/results/${jobId}/target-coverage`)
  },

  // Get statistics
  getStatistics(jobId) {
    return client.get(`/results/${jobId}/statistics`)
  },

  // Compare results
  compare(jobIds) {
    return client.post('/results/compare', { job_ids: jobIds })
  },

  // Export results
  exportResults(jobId, format = 'json') {
    return client.get(`/results/${jobId}/export`, {
      params: { format },
      responseType: 'blob'
    })
  },

  // Get timeline data for visualization
  getTimeline(jobId) {
    return client.get(`/results/${jobId}/timeline`)
  },

  // Get Gantt chart data
  getGanttData(jobId) {
    return client.get(`/results/${jobId}/gantt`)
  },

  // Get map data for visualization
  getMapData(jobId) {
    return client.get(`/results/${jobId}/map-data`)
  }
}

export default resultsApi
