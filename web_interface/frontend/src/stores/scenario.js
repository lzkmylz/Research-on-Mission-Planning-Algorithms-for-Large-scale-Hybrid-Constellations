import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useScenarioStore = defineStore('scenario', () => {
  // State
  const scenarios = ref([])
  const currentScenario = ref(null)
  const targets = ref([])
  const groundStations = ref([])
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const targetCount = computed(() => targets.value.length)
  const groundStationCount = computed(() => groundStations.value.length)

  const targetTypes = computed(() => {
    const types = new Set()
    targets.value.forEach(t => {
      if (t.target_type) types.add(t.target_type)
    })
    return Array.from(types)
  })

  const priorityDistribution = computed(() => {
    const dist = {}
    targets.value.forEach(t => {
      const p = t.priority || 1
      dist[p] = (dist[p] || 0) + 1
    })
    return dist
  })

  // Actions
  function setScenarios(data) {
    scenarios.value = data
  }

  function setCurrentScenario(scenario) {
    currentScenario.value = scenario
  }

  function setTargets(data) {
    targets.value = data
  }

  function setGroundStations(data) {
    groundStations.value = data
  }

  function addTarget(target) {
    targets.value.push(target)
  }

  function updateTarget(id, updates) {
    const index = targets.value.findIndex(t => t.id === id)
    if (index !== -1) {
      targets.value[index] = { ...targets.value[index], ...updates }
    }
  }

  function removeTarget(id) {
    const index = targets.value.findIndex(t => t.id === id)
    if (index !== -1) {
      targets.value.splice(index, 1)
    }
  }

  function addGroundStation(station) {
    groundStations.value.push(station)
  }

  function updateGroundStation(id, updates) {
    const index = groundStations.value.findIndex(s => s.id === id)
    if (index !== -1) {
      groundStations.value[index] = { ...groundStations.value[index], ...updates }
    }
  }

  function removeGroundStation(id) {
    const index = groundStations.value.findIndex(s => s.id === id)
    if (index !== -1) {
      groundStations.value.splice(index, 1)
    }
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

  function clearScenario() {
    currentScenario.value = null
    targets.value = []
    groundStations.value = []
  }

  return {
    // State
    scenarios,
    currentScenario,
    targets,
    groundStations,
    loading,
    error,
    // Getters
    targetCount,
    groundStationCount,
    targetTypes,
    priorityDistribution,
    // Actions
    setScenarios,
    setCurrentScenario,
    setTargets,
    setGroundStations,
    addTarget,
    updateTarget,
    removeTarget,
    addGroundStation,
    updateGroundStation,
    removeGroundStation,
    setLoading,
    setError,
    clearError,
    clearScenario
  }
})
