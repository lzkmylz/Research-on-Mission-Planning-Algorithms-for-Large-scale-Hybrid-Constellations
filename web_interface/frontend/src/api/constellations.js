import client from './client'

export const constellationApi = {
  // Get all constellations
  getAll() {
    return client.get('/constellations/')
  },

  // Get constellation by ID
  getById(id) {
    return client.get(`/constellations/${id}`)
  },

  // Create new constellation
  create(data) {
    return client.post('/constellations/', data)
  },

  // Update constellation
  update(id, data) {
    return client.put(`/constellations/${id}`, data)
  },

  // Delete constellation
  delete(id) {
    return client.delete(`/constellations/${id}`)
  },

  // Get satellites in constellation
  getSatellites(constellationId) {
    return client.get(`/constellations/${constellationId}/satellites`)
  },

  // Add satellite to constellation
  addSatellite(constellationId, satelliteData) {
    return client.post(`/constellations/${constellationId}/satellites`, satelliteData)
  },

  // Update satellite
  updateSatellite(constellationId, satelliteId, data) {
    return client.put(`/constellations/${constellationId}/satellites/${satelliteId}`, data)
  },

  // Remove satellite from constellation
  removeSatellite(constellationId, satelliteId) {
    return client.delete(`/constellations/${constellationId}/satellites/${satelliteId}`)
  },

  // Generate Walker constellation
  generateWalker(data) {
    return client.post('/constellations/generate/walker', data)
  },

  // Generate Flower constellation
  generateFlower(data) {
    return client.post('/constellations/generate/flower', data)
  }
}

export default constellationApi
