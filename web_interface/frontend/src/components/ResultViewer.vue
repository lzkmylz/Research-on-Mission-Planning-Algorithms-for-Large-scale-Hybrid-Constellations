<template>
  <div class="result-viewer">
    <el-row :gutter="20">
      <!-- Summary Statistics -->
      <el-col :span="24">
        <el-card class="summary-card">
          <template #header>
            <span>规划结果概览</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="4">
              <div class="stat-item">
                <div class="stat-value">{{ formatNumber(stats.totalObservations) }}</div>
                <div class="stat-label">总观测数</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="stat-item">
                <div class="stat-value">{{ formatPercentage(stats.completionRate) }}</div>
                <div class="stat-label">任务完成率</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="stat-item">
                <div class="stat-value">{{ formatNumber(stats.totalValue) }}</div>
                <div class="stat-label">总收益</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="stat-item">
                <div class="stat-value">{{ formatDuration(stats.runtime) }}</div>
                <div class="stat-label">运行时间</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="stat-item">
                <div class="stat-value">{{ formatPercentage(stats.satelliteUtilization) }}</div>
                <div class="stat-label">卫星利用率</div>
              </div>
            </el-col>
            <el-col :span="4">
              <div class="stat-item">
                <div class="stat-value">{{ formatPercentage(stats.groundStationUtilization) }}</div>
                <div class="stat-label">地面站利用率</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <!-- Observation Schedule Table -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>观测计划</span>
            <el-button style="float: right; padding: 3px 0" type="primary" text @click="exportSchedule">
              导出
            </el-button>
          </template>
          <el-table :data="schedule" height="400" v-loading="loading">
            <el-table-column prop="satellite_name" label="卫星" width="120" />
            <el-table-column prop="target_name" label="目标" width="120" />
            <el-table-column label="开始时间" width="160">
              <template #default="{ row }">
                {{ formatDatetime(row.start_time) }}
              </template>
            </el-table-column>
            <el-table-column label="结束时间" width="160">
              <template #default="{ row }">
                {{ formatDatetime(row.end_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="持续时间" width="100">
              <template #default="{ row }">
                {{ formatDuration(row.duration) }}
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)">{{ row.priority }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- Charts -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>资源利用率</span>
          </template>
          <v-chart class="chart" :option="utilizationChartOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <!-- Timeline Chart -->
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>观测时间线 (Gantt)</span>
          </template>
          <v-chart class="timeline-chart" :option="timelineChartOption" autoresize />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-20">
      <!-- Target Coverage -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>目标覆盖情况</span>
          </template>
          <v-chart class="chart" :option="coverageChartOption" autoresize />
        </el-card>
      </el-col>

      <!-- Priority Distribution -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>优先级分布</span>
          </template>
          <v-chart class="chart" :option="priorityChartOption" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, CustomChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DataZoomComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import {
  formatNumber,
  formatPercentage,
  formatDuration,
  formatDatetime
} from '@/utils/formatters'

use([
  CanvasRenderer,
  BarChart,
  PieChart,
  CustomChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DataZoomComponent
])

const props = defineProps({
  result: {
    type: Object,
    default: () => ({
      stats: {},
      schedule: [],
      utilization: {},
      coverage: []
    })
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['export'])

const stats = computed(() => props.result?.stats || {})
const schedule = computed(() => props.result?.schedule || [])

function getPriorityType(priority) {
  const types = { 1: 'info', 2: 'success', 3: 'warning', 4: 'danger', 5: 'danger' }
  return types[priority] || 'info'
}

function exportSchedule() {
  emit('export', 'schedule')
}

// Utilization Chart
const utilizationChartOption = computed(() => {
  const data = props.result?.utilization || {}
  return {
    tooltip: { trigger: 'axis' },
    legend: { data: ['利用率'] },
    xAxis: {
      type: 'category',
      data: Object.keys(data),
      axisLabel: { rotate: 45 }
    },
    yAxis: {
      type: 'value',
      max: 100,
      axisLabel: { formatter: '{value}%' }
    },
    series: [{
      name: '利用率',
      type: 'bar',
      data: Object.values(data).map(v => (v * 100).toFixed(2)),
      itemStyle: { color: '#409EFF' }
    }]
  }
})

// Timeline Chart (Gantt)
const timelineChartOption = computed(() => {
  const schedule = props.result?.schedule || []
  const satellites = [...new Set(schedule.map(s => s.satellite_name))]

  const seriesData = schedule.map(obs => ({
    name: obs.satellite_name,
    value: [
      satellites.indexOf(obs.satellite_name),
      new Date(obs.start_time).getTime(),
      new Date(obs.end_time).getTime(),
      obs.duration
    ],
    itemStyle: {
      color: getPriorityColor(obs.priority)
    }
  }))

  function renderGanttItem(params, api) {
    const categoryIndex = api.value(0)
    const start = api.coord([api.value(1), categoryIndex])
    const end = api.coord([api.value(2), categoryIndex])
    const height = api.size([0, 1])[1] * 0.6

    return {
      type: 'rect',
      shape: {
        x: start[0],
        y: start[1] - height / 2,
        width: end[0] - start[0],
        height: height
      },
      style: api.style()
    }
  }

  return {
    tooltip: {
      formatter: function (params) {
        return `${params.name}<br/>` +
               `开始: ${formatDatetime(params.value[1])}<br/>` +
               `结束: ${formatDatetime(params.value[2])}<br/>` +
               `持续: ${formatDuration(params.value[3])}`
      }
    },
    dataZoom: [{ type: 'slider', xAxisIndex: 0, filterMode: 'weakFilter' }],
    grid: { height: 300 },
    xAxis: {
      type: 'time',
      axisLabel: { formatter: '{HH}:{mm}' }
    },
    yAxis: {
      type: 'category',
      data: satellites,
      axisLabel: { interval: 0 }
    },
    series: [{
      type: 'custom',
      renderItem: renderGanttItem,
      itemStyle: { opacity: 0.8 },
      encode: { x: [1, 2], y: 0 },
      data: seriesData
    }]
  }
})

// Coverage Chart
const coverageChartOption = computed(() => {
  const coverage = props.result?.coverage || []
  const completed = coverage.filter(c => c.completed).length
  const total = coverage.length

  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: '5%' },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {c} ({d}%)' },
      data: [
        { value: completed, name: '已完成', itemStyle: { color: '#67C23A' } },
        { value: total - completed, name: '未完成', itemStyle: { color: '#F56C6C' } }
      ]
    }]
  }
})

// Priority Distribution Chart
const priorityChartOption = computed(() => {
  const schedule = props.result?.schedule || []
  const priorityCount = {}
  schedule.forEach(obs => {
    priorityCount[obs.priority] = (priorityCount[obs.priority] || 0) + 1
  })

  const colors = ['#909399', '#67C23A', '#E6A23C', '#F56C6C', '#F56C6C']

  return {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: Object.keys(priorityCount).map(p => `优先级 ${p}`)
    },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: Object.entries(priorityCount).map(([p, count]) => ({
        value: count,
        itemStyle: { color: colors[p - 1] || '#409EFF' }
      }))
    }]
  }
})

function getPriorityColor(priority) {
  const colors = ['#909399', '#67C23A', '#E6A23C', '#F56C6C', '#F56C6C']
  return colors[priority - 1] || '#409EFF'
}
</script>

<style scoped>
.result-viewer {
  padding: 20px;
}

.mt-20 {
  margin-top: 20px;
}

.summary-card {
  margin-bottom: 20px;
}

.stat-item {
  text-align: center;
  padding: 15px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-top: 5px;
}

.chart {
  height: 300px;
}

.timeline-chart {
  height: 400px;
}
</style>
