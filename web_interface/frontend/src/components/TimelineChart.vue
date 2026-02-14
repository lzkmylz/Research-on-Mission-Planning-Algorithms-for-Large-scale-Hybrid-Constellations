<template>
  <div class="timeline-chart">
    <v-chart class="chart" :option="chartOption" autoresize @click="handleChartClick" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { CustomChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  DataZoomComponent,
  MarkLineComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { formatDatetime, formatDuration } from '@/utils/formatters'

use([
  CanvasRenderer,
  CustomChart,
  GridComponent,
  TooltipComponent,
  DataZoomComponent,
  MarkLineComponent
])

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  },
  startTime: {
    type: [String, Date, Number],
    default: null
  },
  endTime: {
    type: [String, Date, Number],
    default: null
  },
  colorBy: {
    type: String,
    default: 'priority' // 'priority', 'type', 'status'
  },
  showCurrentTime: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click', 'hover'])

const chartOption = computed(() => {
  const categories = props.categories.length > 0
    ? props.categories
    : [...new Set(props.data.map(d => d.category || d.satellite_name))]

  const seriesData = props.data.map(item => ({
    name: item.name || item.target_name,
    value: [
      categories.indexOf(item.category || item.satellite_name),
      new Date(item.start_time || item.start).getTime(),
      new Date(item.end_time || item.end).getTime(),
      item.duration || (new Date(item.end).getTime() - new Date(item.start).getTime()) / 1000,
      item.priority || 1,
      item.id
    ],
    itemStyle: {
      color: getItemColor(item)
    }
  }))

  function renderGanttItem(params, api) {
    const categoryIndex = api.value(0)
    const start = api.coord([api.value(1), categoryIndex])
    const end = api.coord([api.value(2), categoryIndex])
    const height = api.size([0, 1])[1] * 0.6

    const rectShape = {
      x: start[0],
      y: start[1] - height / 2,
      width: end[0] - start[0],
      height: height
    }

    return {
      type: 'rect',
      shape: rectShape,
      style: api.style({ fill: api.visual('color') })
    }
  }

  const markLines = []
  if (props.showCurrentTime) {
    markLines.push({
      xAxis: new Date().getTime(),
      label: { formatter: '当前时间' },
      lineStyle: { color: '#F56C6C', type: 'dashed' }
    })
  }

  return {
    tooltip: {
      trigger: 'item',
      formatter: function (params) {
        const item = params.data
        return `<strong>${item.name}</strong><br/>` +
               `开始: ${formatDatetime(item.value[1])}<br/>` +
               `结束: ${formatDatetime(item.value[2])}<br/>` +
               `持续: ${formatDuration(item.value[3])}<br/>` +
               `优先级: ${item.value[4]}`
      }
    },
    dataZoom: [
      { type: 'slider', xAxisIndex: 0, filterMode: 'weakFilter' },
      { type: 'inside', xAxisIndex: 0, filterMode: 'weakFilter' }
    ],
    grid: {
      height: 'auto',
      left: 150,
      right: 50,
      top: 50,
      bottom: 80
    },
    xAxis: {
      type: 'time',
      min: props.startTime ? new Date(props.startTime).getTime() : undefined,
      max: props.endTime ? new Date(props.endTime).getTime() : undefined,
      axisLabel: {
        formatter: function (value) {
          const date = new Date(value)
          return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
        }
      },
      splitLine: { show: true }
    },
    yAxis: {
      type: 'category',
      data: categories,
      axisLabel: { interval: 0 },
      splitLine: { show: true }
    },
    series: [{
      type: 'custom',
      renderItem: renderGanttItem,
      itemStyle: { opacity: 0.85 },
      encode: {
        x: [1, 2],
        y: 0,
        tooltip: [1, 2, 3, 4]
      },
      data: seriesData,
      markLine: { data: markLines }
    }]
  }
})

function getItemColor(item) {
  if (props.colorBy === 'priority') {
    const colors = ['#909399', '#67C23A', '#E6A23C', '#F56C6C', '#F56C6C']
    return colors[(item.priority || 1) - 1] || '#409EFF'
  } else if (props.colorBy === 'type') {
    const typeColors = {
      'imaging': '#409EFF',
      'downlink': '#67C23A',
      'uplink': '#E6A23C',
      'maneuver': '#F56C6C'
    }
    return typeColors[item.type] || '#409EFF'
  } else if (props.colorBy === 'status') {
    const statusColors = {
      'completed': '#67C23A',
      'scheduled': '#409EFF',
      'failed': '#F56C6C',
      'cancelled': '#909399'
    }
    return statusColors[item.status] || '#409EFF'
  }
  return '#409EFF'
}

function handleChartClick(params) {
  if (params.data) {
    emit('click', {
      id: params.data.value[5],
      name: params.data.name,
      startTime: params.data.value[1],
      endTime: params.data.value[2],
      priority: params.data.value[4]
    })
  }
}
</script>

<style scoped>
.timeline-chart {
  width: 100%;
  height: 100%;
}

.chart {
  width: 100%;
  height: 500px;
}
</style>
