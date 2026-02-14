import client from './client'

export const groundStationApi = {
  // Get all ground stations
  getAll() {
    return client.get('/ground-stations/')
  },

  // Get ground station by ID
  getById(id) {
    return client.get(`/ground-stations/${id}`)
  },

  // Create new ground station
  create(data) {
    return client.post('/ground-stations/', data)
  },

  // Update ground station
  update(id, data) {
    return client.put(`/ground-stations/${id}`, data)
  },

  // Delete ground station
  delete(id) {
    return client.delete(`/ground-stations/${id}`)
  },

  // Get antennas for ground station
  getAntennas(stationId) {
    return client.get(`/ground-stations/${stationId}/antennas`)
  },

  // Add antenna to ground station
  addAntenna(stationId, antennaData) {
    return client.post(`/ground-stations/${stationId}/antennas`, antennaData)
  },

  // Update antenna
  updateAntenna(stationId, antennaId, data) {
    return client.put(`/ground-stations/${stationId}/antennas/${antennaId}`, data)
  },

  // Remove antenna from ground station
  removeAntenna(stationId, antennaId) {
    return client.delete(`/ground-stations/${stationId}/antennas/${antennaId}`)
  },

  // Get visibility windows for ground station
  getVisibilityWindows(stationId, params) {
    return client.get(`/ground-stations/${stationId}/visibility`, { params })
  }
}

export default groundStationApi
