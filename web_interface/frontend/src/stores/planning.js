import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const usePlanningStore = defineStore('planning', () => {
  // State
  const currentJob = ref(null)
  const jobs = ref([])
  const algorithms = ref([])
  const selectedAlgorithm = ref(null)
  const isRunning = ref(false)
  const progress = ref(0)
  const results = ref(null)
  const error = ref(null)

  // Getters
  const hasActiveJob = computed(() => currentJob.value !== null)
  const completedJobs = computed(() => jobs.value.filter(j => j.status === 'completed'))
  const pendingJobs = computed(() => jobs.value.filter(j => j.status === 'pending'))

  // Actions
  function setAlgorithms(data) {
    algorithms.value = data
  }

  function selectAlgorithm(algorithm) {
    selectedAlgorithm.value = algorithm
  }

  function setCurrentJob(job) {
    currentJob.value = job
  }

  function addJob(job) {
    jobs.value.push(job)
  }

  function updateJob(id, updates) {
    const index = jobs.value.findIndex(j => j.id === id)
    if (index !== -1) {
      jobs.value[index] = { ...jobs.value[index], ...updates }
    }
    if (currentJob.value?.id === id) {
      currentJob.value = { ...currentJob.value, ...updates }
    }
  }

  function setRunning(value) {
    isRunning.value = value
  }

  function setProgress(value) {
    progress.value = Math.min(100, Math.max(0, value))
  }

  function setResults(data) {
    results.value = data
  }

  function setError(err) {
    error.value = err
  }

  function clearError() {
    error.value = null
  }

  function reset() {
    currentJob.value = null
    isRunning.value = false
    progress.value = 0
    results.value = null
    error.value = null
  }

  return {
    // State
    currentJob,
    jobs,
    algorithms,
    selectedAlgorithm,
    isRunning,
    progress,
    results,
    error,
    // Getters
    hasActiveJob,
    completedJobs,
    pendingJobs,
    // Actions
    setAlgorithms,
    selectAlgorithm,
    setCurrentJob,
    addJob,
    updateJob,
    setRunning,
    setProgress,
    setResults,
    setError,
    clearError,
    reset
  }
})
