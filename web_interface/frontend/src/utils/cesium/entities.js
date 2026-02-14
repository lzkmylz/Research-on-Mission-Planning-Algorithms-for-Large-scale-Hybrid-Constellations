import * as Cesium from 'cesium'

/**
 * Create a satellite entity
 * @param {Object} satellite - Satellite data
 * @param {Object} options - Display options
 * @returns {Object} Entity data object
 */
export function createSatelliteEntity(satellite, options = {}) {
  const {
    color = Cesium.Color.CYAN,
    pixelSize = 10,
    showLabel = true,
    showOrbit = true
  } = options

  const position = Cesium.Cartesian3.fromDegrees(
    satellite.longitude || 0,
    satellite.latitude || 0,
    satellite.altitude || 500000
  )

  const entity = {
    id: `satellite-${satellite.id}`,
    name: satellite.name || `Satellite ${satellite.id}`,
    position: position,
    point: {
      pixelSize: pixelSize,
      color: color,
      outlineColor: Cesium.Color.WHITE,
      outlineWidth: 2,
      scaleByDistance: new Cesium.NearFarScalar(1.5e2, 2.0, 1.5e7, 0.5)
    },
    properties: {
      ...satellite,
      type: 'satellite'
    }
  }

  if (showLabel) {
    entity.label = {
      text: satellite.name || `Sat ${satellite.id}`,
      font: '14px sans-serif',
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 2,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM,
      pixelOffset: new Cesium.Cartesian2(0, -10),
      showBackground: true,
      backgroundColor: new Cesium.Color(0, 0, 0, 0.7)
    }
  }

  return entity
}

/**
 * Create a target entity
 * @param {Object} target - Target data
 * @param {Object} options - Display options
 * @returns {Object} Entity data object
 */
export function createTargetEntity(target, options = {}) {
  const {
    color,
    pixelSize = 8,
    showLabel = true
  } = options

  // Color based on priority
  const priorityColors = {
    1: Cesium.Color.GREEN,
    2: Cesium.Color.LIME,
    3: Cesium.Color.YELLOW,
    4: Cesium.Color.ORANGE,
    5: Cesium.Color.RED
  }

  const entityColor = color || priorityColors[target.priority] || Cesium.Color.YELLOW

  const entity = {
    id: `target-${target.id}`,
    name: target.name || `Target ${target.id}`,
    position: Cesium.Cartesian3.fromDegrees(target.longitude, target.latitude, 0),
    point: {
      pixelSize: pixelSize,
      color: entityColor,
      outlineColor: Cesium.Color.WHITE,
      outlineWidth: 2
    },
    properties: {
      ...target,
      type: 'target'
    }
  }

  if (showLabel) {
    entity.label = {
      text: target.name || `Target ${target.id}`,
      font: '12px sans-serif',
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 2,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: Cesium.VerticalOrigin.TOP,
      pixelOffset: new Cesium.Cartesian2(0, 10)
    }
  }

  return entity
}

/**
 * Create a ground station entity
 * @param {Object} station - Ground station data
 * @param {Object} options - Display options
 * @returns {Object} Entity data object
 */
export function createGroundStationEntity(station, options = {}) {
  const {
    color = Cesium.Color.BLUE,
    showLabel = true,
    showCoverage = true
  } = options

  const entity = {
    id: `station-${station.id}`,
    name: station.name || `Station ${station.id}`,
    position: Cesium.Cartesian3.fromDegrees(station.longitude, station.latitude, 0),
    billboard: {
      image: createStationIcon(),
      scale: 0.5,
      verticalOrigin: Cesium.VerticalOrigin.BOTTOM
    },
    properties: {
      ...station,
      type: 'groundStation'
    }
  }

  if (showLabel) {
    entity.label = {
      text: station.name || `Station ${station.id}`,
      font: '12px sans-serif',
      fillColor: Cesium.Color.WHITE,
      outlineColor: Cesium.Color.BLACK,
      outlineWidth: 2,
      style: Cesium.LabelStyle.FILL_AND_OUTLINE,
      verticalOrigin: Cesium.VerticalOrigin.TOP,
      pixelOffset: new Cesium.Cartesian2(0, 5)
    }
  }

  if (showCoverage && station.min_elevation) {
    // Add coverage cone
    entity.ellipse = {
      semiMinorAxis: 2000000, // Approximate coverage radius
      semiMajorAxis: 2000000,
      material: color.withAlpha(0.1),
      outline: true,
      outlineColor: color,
      outlineWidth: 1,
      height: 0
    }
  }

  return entity
}

/**
 * Create an observation path entity
 * @param {Object} observation - Observation data
 * @param {Object} satellite - Satellite data
 * @param {Object} target - Target data
 * @param {Object} options - Display options
 * @returns {Object} Entity data object
 */
export function createObservationPath(observation, satellite, target, options = {}) {
  const {
    color = Cesium.Color.YELLOW,
    width = 2
  } = options

  const positions = [
    Cesium.Cartesian3.fromDegrees(satellite.longitude, satellite.latitude, satellite.altitude || 500000),
    Cesium.Cartesian3.fromDegrees(target.longitude, target.latitude, 0)
  ]

  return {
    id: `observation-${observation.id}`,
    name: `Observation ${observation.id}`,
    polyline: {
      positions: positions,
      width: width,
      material: new Cesium.PolylineDashMaterialProperty({
        color: color,
        dashLength: 10
      }),
      arcType: Cesium.ArcType.NONE
    },
    properties: {
      ...observation,
      type: 'observation'
    }
  }
}

/**
 * Create a satellite orbit path
 * @param {Array} positions - Array of [lon, lat, alt] positions
 * @param {Object} options - Display options
 * @returns {Object} Entity data object
 */
export function createOrbitPath(positions, options = {}) {
  const {
    color = Cesium.Color.CYAN,
    width = 2
  } = options

  const cartesianPositions = positions.map(p =>
    Cesium.Cartesian3.fromDegrees(p[0], p[1], p[2] || 500000)
  )

  return {
    id: `orbit-${Date.now()}`,
    polyline: {
      positions: cartesianPositions,
      width: width,
      material: color.withAlpha(0.8),
      arcType: Cesium.ArcType.NONE
    },
    properties: {
      type: 'orbit'
    }
  }
}

/**
 * Create an area target polygon
 * @param {Object} area - Area target data with polygon
 * @param {Object} options - Display options
 * @returns {Object} Entity data object
 */
export function createAreaEntity(area, options = {}) {
  const {
    color = Cesium.Color.ORANGE,
    outlineColor = Cesium.Color.WHITE,
    fillAlpha = 0.3
  } = options

  const hierarchy = area.polygon.map(p => Cesium.Cartesian3.fromDegrees(p[0], p[1], 0))

  return {
    id: `area-${area.id}`,
    name: area.name || `Area ${area.id}`,
    polygon: {
      hierarchy: hierarchy,
      material: color.withAlpha(fillAlpha),
      outline: true,
      outlineColor: outlineColor,
      outlineWidth: 2,
      height: 0
    },
    properties: {
      ...area,
      type: 'area'
    }
  }
}

/**
 * Create a visibility cone from satellite to target
 * @param {Object} satellite - Satellite position
 * @param {Object} target - Target position
 * @param {Object} options - Display options
 * @returns {Object} Entity data object
 */
export function createVisibilityCone(satellite, target, options = {}) {
  const {
    color = Cesium.Color.GREEN,
    alpha = 0.2
  } = options

  const satPos = Cesium.Cartesian3.fromDegrees(
    satellite.longitude,
    satellite.latitude,
    satellite.altitude || 500000
  )
  const targetPos = Cesium.Cartesian3.fromDegrees(target.longitude, target.latitude, 0)

  return {
    id: `visibility-${satellite.id}-${target.id}`,
    corridor: {
      positions: [satPos, targetPos],
      width: 50000, // 50km width
      material: color.withAlpha(alpha),
      outline: true,
      outlineColor: color
    },
    properties: {
      type: 'visibility'
    }
  }
}

/**
 * Create station icon as data URL
 * @returns {string} Data URL for station icon
 */
function createStationIcon() {
  // Create a simple SVG icon for ground station
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24">
      <path fill="#0066CC" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
      <circle fill="white" cx="12" cy="9" r="2.5"/>
    </svg>
  `
  return 'data:image/svg+xml;base64,' + btoa(svg)
}

/**
 * Get color for satellite by orbit type
 * @param {string} orbitType - Orbit type
 * @returns {Cesium.Color} Color for orbit type
 */
export function getOrbitTypeColor(orbitType) {
  const colors = {
    'LEO': Cesium.Color.CYAN,
    'MEO': Cesium.Color.YELLOW,
    'GEO': Cesium.Color.GREEN,
    'SSO': Cesium.Color.MAGENTA,
    'POLAR': Cesium.Color.BLUE,
    'ELLIPTICAL': Cesium.Color.ORANGE
  }
  return colors[orbitType] || Cesium.Color.WHITE
}

/**
 * Fly camera to entity
 * @param {Cesium.Viewer} viewer - Cesium viewer
 * @param {string} entityId - Entity ID
 * @param {Object} options - Fly options
 */
export function flyToEntity(viewer, entityId, options = {}) {
  const entity = viewer.entities.getById(entityId)
  if (entity) {
    viewer.flyTo(entity, {
      duration: 2,
      offset: new Cesium.HeadingPitchRange(0, -Cesium.Math.PI_OVER_TWO, 1000000),
      ...options
    })
  }
}

/**
 * Clear all entities of a specific type
 * @param {Cesium.Viewer} viewer - Cesium viewer
 * @param {string} type - Entity type to clear
 */
export function clearEntitiesByType(viewer, type) {
  const entitiesToRemove = []
  viewer.entities.values.forEach(entity => {
    if (entity.properties?.type?.getValue() === type) {
      entitiesToRemove.push(entity)
    }
  })
  entitiesToRemove.forEach(entity => viewer.entities.remove(entity))
}
