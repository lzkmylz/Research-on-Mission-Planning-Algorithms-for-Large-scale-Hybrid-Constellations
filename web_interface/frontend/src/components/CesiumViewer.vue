<template>
  <div ref="cesiumContainer" class="cesium-viewer"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as Cesium from 'cesium'
import 'cesium/Build/Cesium/Widgets/widgets.css'

const props = defineProps({
  satellites: {
    type: Array,
    default: () => []
  },
  targets: {
    type: Array,
    default: () => []
  },
  groundStations: {
    type: Array,
    default: () => []
  },
  observations: {
    type: Array,
    default: () => []
  },
  showSatellites: {
    type: Boolean,
    default: true
  },
  showTargets: {
    type: Boolean,
    default: true
  },
  showGroundStations: {
    type: Boolean,
    default: true
  },
  showObservations: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['entity-click', 'viewer-ready'])

const cesiumContainer = ref(null)
let viewer = null

// Initialize Cesium viewer
onMounted(async () => {
  // Set Cesium ion token (replace with your own)
  Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlYWE1ZDAwZC1iZTEyLTRkNDUtODVlYi0zYTI2ODI2N2FjMDUiLCJpZCI6NTYwODUsImlhdCI6MTY5NjA0MjE3OH0.MmK0RXva9E8Z7aW3F9X7v3z9z9z9z9z9z9z9z9z9z9z'

  const terrainProvider = await Cesium.createWorldTerrainAsync()

  viewer = new Cesium.Viewer(cesiumContainer.value, {
    terrainProvider: terrainProvider,
    imageryProvider: new Cesium.IonImageryProvider({ assetId: 2 }),
    baseLayerPicker: true,
    geocoder: true,
    homeButton: true,
    sceneModePicker: true,
    navigationHelpButton: true,
    animation: false,
    timeline: false,
    fullscreenButton: false,
    vrButton: false
  })

  // Add click handler
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  handler.setInputAction((click) => {
    const pickedObject = viewer.scene.pick(click.position)
    if (Cesium.defined(pickedObject) && pickedObject.id) {
      emit('entity-click', pickedObject.id)
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)

  emit('viewer-ready', viewer)

  // Initial render
  updateEntities()
})

// Cleanup
onUnmounted(() => {
  if (viewer) {
    viewer.destroy()
    viewer = null
  }
})

// Watch for changes
watch(() => props.satellites, updateEntities, { deep: true })
watch(() => props.targets, updateEntities, { deep: true })
watch(() => props.groundStations, updateEntities, { deep: true })
watch(() => props.observations, updateEntities, { deep: true })
watch(() => props.showSatellites, updateEntities)
watch(() => props.showTargets, updateEntities)
watch(() => props.showGroundStations, updateEntities)
watch(() => props.showObservations, updateEntities)

function updateEntities() {
  if (!viewer) return

  viewer.entities.removeAll()

  // Add satellites
  if (props.showSatellites) {
    props.satellites.forEach(sat => {
      viewer.entities.add({
        id: `sat-${sat.id}`,
        position: Cesium.Cartesian3.fromDegrees(
          sat.longitude || 0,
          sat.latitude || 0,
          sat.altitude || 500000
        ),
        point: {
          pixelSize: 10,
          color: Cesium.Color.CYAN,
          outlineColor: Cesium.Color.WHITE,
          outlineWidth: 2
        },
        label: {
          text: sat.name || `Sat ${sat.id}`,
          font: '12px sans-serif',
          fillColor: Cesium.Color.WHITE,
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 2,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
          pixelOffset: new Cesium.Cartesian2(0, -10)
        },
        properties: { type: 'satellite', data: sat }
      })
    })
  }

  // Add targets
  if (props.showTargets) {
    props.targets.forEach(target => {
      const priorityColors = {
        1: Cesium.Color.GREEN,
        2: Cesium.Color.LIME,
        3: Cesium.Color.YELLOW,
        4: Cesium.Color.ORANGE,
        5: Cesium.Color.RED
      }
      const color = priorityColors[target.priority] || Cesium.Color.YELLOW

      viewer.entities.add({
        id: `target-${target.id}`,
        position: Cesium.Cartesian3.fromDegrees(target.longitude, target.latitude, 0),
        point: {
          pixelSize: 8,
          color: color,
          outlineColor: Cesium.Color.WHITE,
          outlineWidth: 2
        },
        label: {
          text: target.name || `Target ${target.id}`,
          font: '11px sans-serif',
          fillColor: Cesium.Color.WHITE,
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 2,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: Cesium.VerticalOrigin.TOP,
          pixelOffset: new Cesium.Cartesian2(0, 10)
        },
        properties: { type: 'target', data: target }
      })
    })
  }

  // Add ground stations
  if (props.showGroundStations) {
    props.groundStations.forEach(station => {
      viewer.entities.add({
        id: `station-${station.id}`,
        position: Cesium.Cartesian3.fromDegrees(station.longitude, station.latitude, 0),
        point: {
          pixelSize: 12,
          color: Cesium.Color.BLUE,
          outlineColor: Cesium.Color.WHITE,
          outlineWidth: 2
        },
        label: {
          text: station.name || `Station ${station.id}`,
          font: '11px sans-serif',
          fillColor: Cesium.Color.WHITE,
          outlineColor: Cesium.Color.BLACK,
          outlineWidth: 2,
          style: Cesium.LabelStyle.FILL_AND_OUTLINE,
          verticalOrigin: Cesium.VerticalOrigin.TOP,
          pixelOffset: new Cesium.Cartesian2(0, 10)
        },
        properties: { type: 'groundStation', data: station }
      })
    })
  }

  // Add observation paths
  if (props.showObservations) {
    props.observations.forEach(obs => {
      const sat = props.satellites.find(s => s.id === obs.satellite_id)
      const target = props.targets.find(t => t.id === obs.target_id)
      if (sat && target) {
        viewer.entities.add({
          id: `obs-${obs.id}`,
          polyline: {
            positions: [
              Cesium.Cartesian3.fromDegrees(sat.longitude, sat.latitude, sat.altitude || 500000),
              Cesium.Cartesian3.fromDegrees(target.longitude, target.latitude, 0)
            ],
            width: 2,
            material: new Cesium.PolylineDashMaterialProperty({
              color: Cesium.Color.YELLOW,
              dashLength: 10
            })
          },
          properties: { type: 'observation', data: obs }
        })
      }
    })
  }
}

// Expose methods
defineExpose({
  flyTo: (entityId) => {
    const entity = viewer?.entities.getById(entityId)
    if (entity) {
      viewer.flyTo(entity)
    }
  },
  getViewer: () => viewer
})
</script>

<style scoped>
.cesium-viewer {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style>
