import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useConstellationStore = defineStore('constellation', () => {
  // State
  const satellites = ref([])
  const selectedSatellite = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const satelliteCount = computed(() => satellites.value.length)
  const orbitTypes = computed(() => {
    const types = new Set()
    satellites.value.forEach(sat => {
      if (sat.orbit_type) types.add(sat.orbit_type)
    })
    return Array.from(types)
  })

  // Actions
  function setSatellites(data) {
    satellites.value = data
  }

  function addSatellite(satellite) {
    satellites.value.push(satellite)
  }

  function updateSatellite(id, updates) {
    const index = satellites.value.findIndex(s => s.id === id)
    if (index !== -1) {
      satellites.value[index] = { ...satellites.value[index], ...updates }
    }
  }

  function removeSatellite(id) {
    const index = satellites.value.findIndex(s => s.id === id)
    if (index !== -1) {
      satellites.value.splice(index, 1)
    }
  }

  function selectSatellite(satellite) {
    selectedSatellite.value = satellite
  }

  function clearSelection() {
    selectedSatellite.value = null
  }

  function setLoading(value) {
    loading.value = value
  }

  function setError(err) {
    error.value = err
  }

  function clearError() {
    error.value = null
  }

  return {
    // State
    satellites,
    selectedSatellite,
    loading,
    error,
    // Getters
    satelliteCount,
    orbitTypes,
    // Actions
    setSatellites,
    addSatellite,
    updateSatellite,
    removeSatellite,
    selectSatellite,
    clearSelection,
    setLoading,
    setError,
    clearError
  }
})
