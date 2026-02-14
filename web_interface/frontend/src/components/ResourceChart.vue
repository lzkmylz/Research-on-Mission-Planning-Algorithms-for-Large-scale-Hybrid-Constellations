<template>
  <div class="resource-chart">
    <v-chart class="chart" :option="chartOption" autoresize />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, BarChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DataZoomComponent,
  ToolboxComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

use([
  CanvasRenderer,
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DataZoomComponent,
  ToolboxComponent
])

const props = defineProps({
  type: {
    type: String,
    default: 'line', // 'line', 'bar', 'stack'
    validator: (value) => ['line', 'bar', 'stack'].includes(value)
  },
  data: {
    type: Array,
    default: () => []
  },
  categories: {
    type: Array,
    default: () => []
  },
  series: {
    type: Array,
    default: () => []
  },
  title: {
    type: String,
    default: ''
  },
  xAxisName: {
    type: String,
    default: ''
  },
  yAxisName: {
    type: String,
    default: ''
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  showToolbox: {
    type: Boolean,
    default: true
  }
})

const chartOption = computed(() => {
  const isStack = props.type === 'stack'
  const chartType = isStack ? 'bar' : props.type

  const seriesData = props.series.length > 0
    ? props.series.map(s => ({
        name: s.name,
        type: chartType,
        stack: isStack ? 'total' : null,
        data: s.data,
        smooth: true,
        areaStyle: isStack ? { opacity: 0.8 } : null,
        emphasis: { focus: 'series' },
        markPoint: s.markPoint,
        markLine: s.markLine
      }))
    : [{
        name: '数据',
        type: chartType,
        data: props.data,
        smooth: true,
        areaStyle: isStack ? { opacity: 0.8 } : null
      }]

  return {
    title: props.title ? { text: props.title, left: 'center' } : null,
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: props.showLegend ? {
      data: props.series.map(s => s.name),
      bottom: 0
    } : null,
    toolbox: props.showToolbox ? {
      feature: {
        dataZoom: { yAxisIndex: 'none' },
        restore: {},
        saveAsImage: {}
      }
    } : null,
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: props.type === 'bar' || props.type === 'stack',
      data: props.categories,
      name: props.xAxisName,
      axisLabel: { rotate: props.categories.length > 20 ? 45 : 0 }
    },
    yAxis: {
      type: 'value',
      name: props.yAxisName,
      axisLabel: { formatter: '{value}' }
    },
    dataZoom: [
      { type: 'inside', start: 0, end: 100 },
      { start: 0, end: 100 }
    ],
    series: seriesData,
    color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399', '#8E44AD']
  }
})
</script>

<style scoped>
.resource-chart {
  width: 100%;
  height: 100%;
}

.chart {
  width: 100%;
  height: 400px;
}
</style>
