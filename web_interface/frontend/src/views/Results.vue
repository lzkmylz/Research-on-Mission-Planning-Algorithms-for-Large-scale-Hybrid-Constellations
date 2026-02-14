<template>
  <div class="results">
    <el-container>
      <el-aside width="300px" class="sidebar">
        <div class="sidebar-header">
          <h3>规划任务列表</h3>
          <el-button type="primary" link @click="refreshJobs">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>

        <el-input
          v-model="searchQuery"
          placeholder="搜索任务..."
          clearable
          prefix-icon="Search"
          class="search-input"
        />

        <el-scrollbar class="job-list">
          <div
            v-for="job in filteredJobs"
            :key="job.id"
            class="job-item"
            :class="{ active: selectedJob?.id === job.id }"
            @click="selectJob(job)"
          >
            <div class="job-header">
              <span class="job-id">#{{ job.id }}</span>
              <el-tag size="small" :type="getStatusType(job.status)">
                {{ job.status }}
              </el-tag>
            </div>
            <div class="job-info">
              <p>{{ job.scenario_name }}</p>
              <p class="job-meta">
                {{ job.algorithm }} | {{ formatDatetime(job.created_at) }}
              </p>
            </div>
          </div>
        </el-scrollbar>

        <div class="sidebar-footer">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="totalJobs"
            layout="prev, pager, next"
            small
          />
        </div>
      </el-aside>

      <el-main class="main-content">
        <div v-if="selectedJob" class="result-detail">
          <el-page-header @back="selectedJob = null" title="任务详情" />

          <ResultViewer
            :result="jobResult"
            :loading="loading"
            @export="handleExport"
          />
        </div>

        <div v-else class="empty-state">
          <el-empty description="选择一个任务查看结果">
            <template #image>
              <el-icon :size="80" color="#909399"><Document /></el-icon>
            </template>
          </el-empty>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { Refresh, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import ResultViewer from '@/components/ResultViewer.vue'
import { planningApi } from '@/api/planning'
import { resultsApi } from '@/api/results'
import { formatDatetime } from '@/utils/formatters'

const route = useRoute()

const jobs = ref([])
const selectedJob = ref(null)
const jobResult = ref({})
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const totalJobs = ref(0)

onMounted(async () => {
  await loadJobs()

  // If job_id is provided in URL, select it
  const jobId = route.query.job_id
  if (jobId) {
    const job = jobs.value.find(j => j.id === jobId)
    if (job) {
      await selectJob(job)
    }
  }
})

async function loadJobs() {
  try {
    const response = await planningApi.getAllJobs({
      page: currentPage.value,
      page_size: pageSize.value
    })
    jobs.value = response.jobs || []
    totalJobs.value = response.total || 0
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  }
}

async function selectJob(job) {
  selectedJob.value = job
  if (job.status === 'completed') {
    await loadJobResult(job.id)
  }
}

async function loadJobResult(jobId) {
  loading.value = true
  try {
    const [results, statistics] = await Promise.all([
      resultsApi.getByJobId(jobId),
      resultsApi.getStatistics(jobId)
    ])

    jobResult.value = {
      stats: statistics,
      schedule: results.schedule || [],
      utilization: results.utilization || {},
      coverage: results.coverage || []
    }
  } catch (error) {
    ElMessage.error('加载结果失败')
  } finally {
    loading.value = false
  }
}

function getStatusType(status) {
  const types = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger',
    'cancelled': 'info'
  }
  return types[status] || 'info'
}

async function refreshJobs() {
  await loadJobs()
  ElMessage.success('刷新成功')
}

async function handleExport(type) {
  try {
    const blob = await resultsApi.exportResults(selectedJob.value.id, type)
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `result_${selectedJob.value.id}_${type}.csv`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  }
}

const filteredJobs = computed(() => {
  if (!searchQuery.value) return jobs.value
  const query = searchQuery.value.toLowerCase()
  return jobs.value.filter(job =>
    job.scenario_name?.toLowerCase().includes(query) ||
    job.algorithm?.toLowerCase().includes(query) ||
    job.id?.toString().includes(query)
  )
})
</script>

<style scoped>
.results {
  height: 100vh;
}

.sidebar {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
}

.search-input {
  padding: 15px 20px;
}

.job-list {
  flex: 1;
  padding: 0 20px;
}

.job-item {
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.job-item:hover {
  border-color: #409EFF;
  background: #f5f7fa;
}

.job-item.active {
  border-color: #409EFF;
  background: #ecf5ff;
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.job-id {
  font-weight: bold;
  color: #409EFF;
}

.job-info p {
  margin: 4px 0;
  font-size: 14px;
}

.job-meta {
  color: #909399;
  font-size: 12px;
}

.sidebar-footer {
  padding: 15px 20px;
  border-top: 1px solid #e4e7ed;
}

.main-content {
  padding: 20px;
  background: #f5f7fa;
  overflow-y: auto;
}

.result-detail {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  min-height: 100%;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}
</style>
