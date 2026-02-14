import client from './client'

export const targetApi = {
  // Get all targets
  getAll(params = {}) {
    return client.get('/targets/', { params })
  },

  // Get target by ID
  getById(id) {
    return client.get(`/targets/${id}`)
  },

  // Create new target
  create(data) {
    return client.post('/targets/', data)
  },

  // Create multiple targets
  createBatch(targets) {
    return client.post('/targets/batch', targets)
  },

  // Update target
  update(id, data) {
    return client.put(`/targets/${id}`, data)
  },

  // Delete target
  delete(id) {
    return client.delete(`/targets/${id}`)
  },

  // Delete multiple targets
  deleteBatch(ids) {
    return client.post('/targets/batch-delete', { ids })
  },

  // Import targets from file
  importFile(file, format = 'geojson') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('format', format)
    return client.post('/targets/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  // Export targets
  exportFile(format = 'geojson') {
    return client.get('/targets/export', {
      params: { format },
      responseType: 'blob'
    })
  },

  // Get target visibility from satellites
  getVisibility(targetId, params) {
    return client.get(`/targets/${targetId}/visibility`, { params })
  },

  // Generate grid targets for area
  generateGrid(params) {
    return client.post('/targets/generate/grid', params)
  },

  // Generate random targets
  generateRandom(params) {
    return client.post('/targets/generate/random', params)
  }
}

export default targetApi
