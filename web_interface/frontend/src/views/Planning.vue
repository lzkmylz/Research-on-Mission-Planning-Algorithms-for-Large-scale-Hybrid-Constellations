<template>
  <div class="planning">
    <el-container>
      <el-aside width="450px" class="sidebar">
        <el-steps :active="currentStep" finish-status="success" class="steps">
          <el-step title="选择场景" />
          <el-step title="配置算法" />
          <el-step title="执行规划" />
        </el-steps>

        <div class="step-content">
          <!-- Step 1: Select Scenario -->
          <div v-if="currentStep === 0" class="step-panel">
            <h3>选择规划场景</h3>
            <el-select
              v-model="selectedScenario"
              placeholder="选择场景"
              style="width: 100%; margin-bottom: 20px"
            >
              <el-option
                v-for="scenario in scenarios"
                :key="scenario.id"
                :label="scenario.name"
                :value="scenario.id"
              >
                <span>{{ scenario.name }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">
                  {{ scenario.target_count }} 目标
                </span>
              </el-option>
            </el-select>

            <el-card v-if="scenarioDetails" class="scenario-info">
              <template #header>
                <span>场景详情</span>
              </template>
              <p><strong>描述:</strong> {{ scenarioDetails.description }}</p>
              <p><strong>目标数量:</strong> {{ scenarioDetails.target_count }}</p>
              <p><strong>卫星数量:</strong> {{ scenarioDetails.satellite_count }}</p>
              <p><strong>地面站:</strong> {{ scenarioDetails.ground_station_count }}</p>
              <p><strong>时间窗口:</strong> {{ formatDatetime(scenarioDetails.start_time) }} - {{ formatDatetime(scenarioDetails.end_time) }}</p>
            </el-card>

            <div class="step-actions">
              <el-button type="primary" @click="nextStep" :disabled="!selectedScenario">
                下一步
              </el-button>
            </div>
          </div>

          <!-- Step 2: Configure Algorithm -->
          <div v-if="currentStep === 1" class="step-panel">
            <AlgorithmPanel
              :is-running="isRunning"
              @start="startPlanning"
              @reset="resetConfig"
              @load-preset="loadPreset"
            />
            <div class="step-actions">
              <el-button @click="prevStep">上一步</el-button>
            </div>
          </div>

          <!-- Step 3: Execute Planning -->
          <div v-if="currentStep === 2" class="step-panel">
            <div v-if="isRunning || jobStatus === 'pending'" class="progress-panel">
              <el-progress
                :percentage="progress"
                :status="progressStatus"
                :stroke-width="20"
                striped
                striped-flow
              />
              <p class="status-text">{{ statusText }}</p>
              <el-button v-if="isRunning" type="danger" @click="cancelJob">
                取消
              </el-button>
            </div>

            <div v-else-if="jobStatus === 'completed'" class="result-preview">
              <el-result
                icon="success"
                title="规划完成"
                :sub-title="`总收益: ${resultStats.total_value}, 完成率: ${resultStats.completion_rate}%`"
              >
                <template #extra>
                  <el-button type="primary" @click="viewResults">查看详细结果</el-button>
                  <el-button @click="startNewPlanning">新的规划</el-button>
                </template>
              </el-result>
            </div>

            <div v-else-if="jobStatus === 'failed'" class="result-preview">
              <el-result
                icon="error"
                title="规划失败"
                :sub-title="errorMessage"
              >
                <template #extra>
                  <el-button type="primary" @click="retryPlanning">重试</el-button>
                  <el-button @click="startNewPlanning">新的规划</el-button>
                </template>
              </el-result>
            </div>
          </div>
        </div>
      </el-aside>

      <el-main class="main-content">
        <CesiumViewer
          v-if="currentStep === 0"
          :targets="scenarioTargets"
          :satellites="scenarioSatellites"
        />
        <div v-else-if="currentStep === 2 && jobStatus === 'completed'" class="preview-chart">
          <TimelineChart
            :data="schedulePreview"
            :categories="satelliteNames"
            @click="onTimelineClick"
          />
        </div>
        <div v-else class="placeholder">
          <el-empty description="配置完成后将显示预览" />
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import CesiumViewer from '@/components/CesiumViewer.vue'
import AlgorithmPanel from '@/components/AlgorithmPanel.vue'
import TimelineChart from '@/components/TimelineChart.vue'
import { scenarioApi } from '@/api/scenarios'
import { planningApi } from '@/api/planning'
import { formatDatetime } from '@/utils/formatters'

const router = useRouter()
const currentStep = ref(0)
const selectedScenario = ref(null)
const scenarios = ref([])
const scenarioDetails = ref(null)
const scenarioTargets = ref([])
const scenarioSatellites = ref([])

const isRunning = ref(false)
const jobId = ref(null)
const jobStatus = ref(null)
const progress = ref(0)
const statusText = ref('准备中...')
const errorMessage = ref('')
const resultStats = ref({})
const schedulePreview = ref([])
const satelliteNames = ref([])

let progressInterval = null

onMounted(async () => {
  await loadScenarios()
})

onUnmounted(() => {
  if (progressInterval) {
    clearInterval(progressInterval)
  }
})

async function loadScenarios() {
  try {
    const data = await scenarioApi.getAll()
    scenarios.value = data
  } catch (error) {
    ElMessage.error('加载场景列表失败')
  }
}

async function loadScenarioDetails() {
  if (!selectedScenario.value) return
  try {
    const [details, targets, stations] = await Promise.all([
      scenarioApi.getById(selectedScenario.value),
      scenarioApi.getTargets(selectedScenario.value),
      scenarioApi.getGroundStations(selectedScenario.value)
    ])
    scenarioDetails.value = details
    scenarioTargets.value = targets
    // Load constellation satellites
    const constellation = await scenarioApi.getConstellation(selectedScenario.value)
    if (constellation) {
      scenarioSatellites.value = constellation.satellites || []
    }
  } catch (error) {
    ElMessage.error('加载场景详情失败')
  }
}

async function nextStep() {
  if (currentStep.value === 0) {
    await loadScenarioDetails()
  }
  currentStep.value++
}

function prevStep() {
  currentStep.value--
}

async function startPlanning(config) {
  try {
    isRunning.value = true
    jobStatus.value = 'pending'
    progress.value = 0
    statusText.value = '提交任务...'

    const job = await planningApi.createJob(
      selectedScenario.value,
      config.algorithmId,
      config.parameters
    )

    jobId.value = job.id
    currentStep.value = 2
    jobStatus.value = 'running'
    statusText.value = '正在规划...'

    // Start polling progress
    startProgressPolling()
  } catch (error) {
    ElMessage.error('启动规划失败')
    isRunning.value = false
    jobStatus.value = 'failed'
    errorMessage.value = error.message
  }
}

function startProgressPolling() {
  progressInterval = setInterval(async () => {
    try {
      const job = await planningApi.getJob(jobId.value)
      jobStatus.value = job.status
      progress.value = job.progress || 0

      switch (job.status) {
        case 'running':
          statusText.value = `正在规划... ${progress.value.toFixed(1)}%`
          break
        case 'completed':
          clearInterval(progressInterval)
          isRunning.value = false
          progress.value = 100
          statusText.value = '规划完成'
          await loadResults()
          break
        case 'failed':
          clearInterval(progressInterval)
          isRunning.value = false
          errorMessage.value = job.error_message || '规划失败'
          statusText.value = '规划失败'
          break
        case 'cancelled':
          clearInterval(progressInterval)
          isRunning.value = false
          statusText.value = '已取消'
          break
      }
    } catch (error) {
      console.error('Failed to get job status:', error)
    }
  }, 1000)
}

async function loadResults() {
  try {
    const results = await planningApi.getResults(jobId.value)
    resultStats.value = results.statistics || {}
    schedulePreview.value = results.schedule || []
    satelliteNames.value = [...new Set(results.schedule?.map(s => s.satellite_name) || [])]
  } catch (error) {
    console.error('Failed to load results:', error)
  }
}

async function cancelJob() {
  try {
    await planningApi.cancelJob(jobId.value)
    ElMessage.info('任务已取消')
  } catch (error) {
    ElMessage.error('取消失败')
  }
}

function viewResults() {
  router.push(`/results?job_id=${jobId.value}`)
}

function startNewPlanning() {
  currentStep.value = 0
  selectedScenario.value = null
  scenarioDetails.value = null
  jobStatus.value = null
  progress.value = 0
  isRunning.value = false
}

function retryPlanning() {
  jobStatus.value = null
  progress.value = 0
  startPlanning()
}

function resetConfig() {
  ElMessage.success('配置已重置')
}

function loadPreset() {
  ElMessage.info('加载预设配置')
}

function onTimelineClick(item) {
  console.log('Timeline item clicked:', item)
}

const progressStatus = computed(() => {
  if (jobStatus.value === 'failed') return 'exception'
  if (jobStatus.value === 'completed') return 'success'
  return ''
})
</script>

<style scoped>
.planning {
  height: 100vh;
}

.sidebar {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  padding: 20px;
}

.steps {
  margin-bottom: 30px;
}

.step-content {
  min-height: 400px;
}

.step-panel {
  padding: 10px;
}

.step-actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
}

.scenario-info {
  margin-top: 20px;
}

.scenario-info p {
  margin: 10px 0;
}

.main-content {
  padding: 0;
  position: relative;
}

.progress-panel {
  text-align: center;
  padding: 40px 20px;
}

.status-text {
  margin: 20px 0;
  color: #606266;
}

.result-preview {
  padding: 20px;
}

.preview-chart {
  width: 100%;
  height: 100%;
  padding: 20px;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
