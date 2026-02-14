/**
 * Format coordinate value with specified precision
 * @param {number} value - Coordinate value
 * @param {number} precision - Decimal places (default: 4)
 * @returns {string} Formatted coordinate
 */
export function formatCoordinate(value, precision = 4) {
  if (value === null || value === undefined) return '-'
  return value.toFixed(precision)
}

/**
 * Format latitude with N/S indicator
 * @param {number} lat - Latitude
 * @returns {string} Formatted latitude
 */
export function formatLatitude(lat) {
  if (lat === null || lat === undefined) return '-'
  const direction = lat >= 0 ? 'N' : 'S'
  return `${Math.abs(lat).toFixed(4)}° ${direction}`
}

/**
 * Format longitude with E/W indicator
 * @param {number} lon - Longitude
 * @returns {string} Formatted longitude
 */
export function formatLongitude(lon) {
  if (lon === null || lon === undefined) return '-'
  const direction = lon >= 0 ? 'E' : 'W'
  return `${Math.abs(lon).toFixed(4)}° ${direction}`
}

/**
 * Format altitude in km or m
 * @param {number} altitude - Altitude in meters
 * @param {boolean} useKm - Use kilometers (default: true)
 * @returns {string} Formatted altitude
 */
export function formatAltitude(altitude, useKm = true) {
  if (altitude === null || altitude === undefined) return '-'
  if (useKm) {
    return `${(altitude / 1000).toFixed(2)} km`
  }
  return `${altitude.toFixed(2)} m`
}

/**
 * Format datetime string
 * @param {string|Date} datetime - Date/time value
 * @param {boolean} includeTime - Include time (default: true)
 * @returns {string} Formatted datetime
 */
export function formatDatetime(datetime, includeTime = true) {
  if (!datetime) return '-'
  const date = new Date(datetime)
  if (isNaN(date.getTime())) return '-'

  const dateStr = date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })

  if (!includeTime) return dateStr

  const timeStr = date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })

  return `${dateStr} ${timeStr}`
}

/**
 * Format duration in seconds to human readable string
 * @param {number} seconds - Duration in seconds
 * @returns {string} Formatted duration
 */
export function formatDuration(seconds) {
  if (seconds === null || seconds === undefined) return '-'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours}h ${minutes}m ${secs}s`
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`
  }
  return `${secs}s`
}

/**
 * Format file size in bytes to human readable string
 * @param {number} bytes - Size in bytes
 * @returns {string} Formatted size
 */
export function formatFileSize(bytes) {
  if (bytes === null || bytes === undefined) return '-'

  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`
}

/**
 * Format data rate in bits per second
 * @param {number} bps - Bits per second
 * @returns {string} Formatted data rate
 */
export function formatDataRate(bps) {
  if (bps === null || bps === undefined) return '-'

  const units = ['bps', 'Kbps', 'Mbps', 'Gbps']
  let rate = bps
  let unitIndex = 0

  while (rate >= 1000 && unitIndex < units.length - 1) {
    rate /= 1000
    unitIndex++
  }

  return `${rate.toFixed(2)} ${units[unitIndex]}`
}

/**
 * Format percentage value
 * @param {number} value - Value between 0 and 1 or 0 and 100
 * @param {boolean} isDecimal - Value is in decimal form (0-1)
 * @returns {string} Formatted percentage
 */
export function formatPercentage(value, isDecimal = true) {
  if (value === null || value === undefined) return '-'
  const pct = isDecimal ? value * 100 : value
  return `${pct.toFixed(2)}%`
}

/**
 * Format number with thousand separators
 * @param {number} value - Number to format
 * @returns {string} Formatted number
 */
export function formatNumber(value) {
  if (value === null || value === undefined) return '-'
  return value.toLocaleString('zh-CN')
}

/**
 * Format satellite orbit type
 * @param {string} orbitType - Orbit type code
 * @returns {string} Human readable orbit type
 */
export function formatOrbitType(orbitType) {
  const types = {
    'LEO': '低地球轨道 (LEO)',
    'MEO': '中地球轨道 (MEO)',
    'GEO': '地球静止轨道 (GEO)',
    'SSO': '太阳同步轨道 (SSO)',
    'POLAR': '极地轨道',
    'ELLIPTICAL': '椭圆轨道'
  }
  return types[orbitType] || orbitType
}

/**
 * Format sensor type
 * @param {string} sensorType - Sensor type code
 * @returns {string} Human readable sensor type
 */
export function formatSensorType(sensorType) {
  const types = {
    'OPTICAL': '光学相机',
    'SAR': '合成孔径雷达',
    'INFRARED': '红外传感器',
    'MULTISPECTRAL': '多光谱传感器',
    'HYPERSPECTRAL': '高光谱传感器',
    'VIDEO': '视频相机'
  }
  return types[sensorType] || sensorType
}

/**
 * Format target type
 * @param {string} targetType - Target type code
 * @returns {string} Human readable target type
 */
export function formatTargetType(targetType) {
  const types = {
    'POINT': '点目标',
    'AREA': '区域目标',
    'MOVING': '移动目标',
    'GRID': '网格目标'
  }
  return types[targetType] || targetType
}

/**
 * Format priority level
 * @param {number} priority - Priority level (1-5)
 * @returns {string} Formatted priority
 */
export function formatPriority(priority) {
  const levels = {
    1: { text: '最低', type: 'info' },
    2: { text: '低', type: 'success' },
    3: { text: '中', type: 'warning' },
    4: { text: '高', type: 'danger' },
    5: { text: '最高', type: 'danger' }
  }
  return levels[priority] || { text: `优先级 ${priority}`, type: 'info' }
}

/**
 * Format job status
 * @param {string} status - Job status code
 * @returns {Object} Status display info
 */
export function formatJobStatus(status) {
  const statuses = {
    'pending': { text: '等待中', type: 'info' },
    'running': { text: '运行中', type: 'warning' },
    'completed': { text: '已完成', type: 'success' },
    'failed': { text: '失败', type: 'danger' },
    'cancelled': { text: '已取消', type: 'info' }
  }
  return statuses[status] || { text: status, type: 'info' }
}

/**
 * Truncate text with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
export function truncateText(text, maxLength = 50) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
