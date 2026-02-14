import { createPinia } from 'pinia'

export default createPinia()

// Export all stores
export { useConstellationStore } from './constellation'
export { usePlanningStore } from './planning'
export { useScenarioStore } from './scenario'
