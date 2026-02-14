import client from './client'

export const scenarioApi = {
  // Get all scenarios
  getAll() {
    return client.get('/scenarios/')
  },

  // Get scenario by ID
  getById(id) {
    return client.get(`/scenarios/${id}`)
  },

  // Create new scenario
  create(data) {
    return client.post('/scenarios/', data)
  },

  // Update scenario
  update(id, data) {
    return client.put(`/scenarios/${id}`, data)
  },

  // Delete scenario
  delete(id) {
    return client.delete(`/scenarios/${id}`)
  },

  // Clone scenario
  clone(id, newName) {
    return client.post(`/scenarios/${id}/clone`, { name: newName })
  },

  // Get scenario targets
  getTargets(scenarioId) {
    return client.get(`/scenarios/${scenarioId}/targets`)
  },

  // Add target to scenario
  addTarget(scenarioId, targetId) {
    return client.post(`/scenarios/${scenarioId}/targets`, { target_id: targetId })
  },

  // Remove target from scenario
  removeTarget(scenarioId, targetId) {
    return client.delete(`/scenarios/${scenarioId}/targets/${targetId}`)
  },

  // Get scenario ground stations
  getGroundStations(scenarioId) {
    return client.get(`/scenarios/${scenarioId}/ground-stations`)
  },

  // Add ground station to scenario
  addGroundStation(scenarioId, stationId) {
    return client.post(`/scenarios/${scenarioId}/ground-stations`, { station_id: stationId })
  },

  // Remove ground station from scenario
  removeGroundStation(scenarioId, stationId) {
    return client.delete(`/scenarios/${scenarioId}/ground-stations/${stationId}`)
  },

  // Get scenario constellation
  getConstellation(scenarioId) {
    return client.get(`/scenarios/${scenarioId}/constellation`)
  },

  // Set scenario constellation
  setConstellation(scenarioId, constellationId) {
    return client.put(`/scenarios/${scenarioId}/constellation`, { constellation_id: constellationId })
  }
}

export default scenarioApi
