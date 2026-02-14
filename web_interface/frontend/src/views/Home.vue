<template>
  <div class="home">
    <div class="hero">
      <h1>星座任务规划系统</h1>
      <p class="subtitle">大规模成像星座任务规划与调度优化平台</p>
      <div class="actions">
        <el-button type="primary" size="large" @click="$router.push('/constellation')">
          <el-icon><Dish /></el-icon>
          设计星座
        </el-button>
        <el-button type="success" size="large" @click="$router.push('/planning')">
          <el-icon><Timer /></el-icon>
          开始规划
        </el-button>
        <el-button size="large" @click="$router.push('/results')">
          <el-icon><DataAnalysis /></el-icon>
          查看结果
        </el-button>
      </div>
    </div>

    <el-row :gutter="20" class="features">
      <el-col :span="6">
        <el-card class="feature-card">
          <el-icon class="feature-icon"><Dish /></el-icon>
          <h3>星座设计</h3>
          <p>支持Walker、Flower等多种星座构型设计，可视化编辑卫星参数</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="feature-card">
          <el-icon class="feature-icon"><Location /></el-icon>
          <h3>目标管理</h3>
          <p>点目标、区域目标、移动目标管理，支持GeoJSON导入导出</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="feature-card">
          <el-icon class="feature-icon"><Cpu /></el-icon>
          <h3>智能规划</h3>
          <p>遗传算法、禁忌搜索、模拟退火、蚁群优化等多种算法</p>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="feature-card">
          <el-icon class="feature-icon"><View /></el-icon>
          <h3>三维可视化</h3>
          <p>基于Cesium的三维地球可视化，实时展示卫星轨道和观测计划</p>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="stats-card">
      <template #header>
        <span>系统状态</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ stats.constellations }}</div>
            <div class="stat-label">星座数量</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ stats.satellites }}</div>
            <div class="stat-label">卫星数量</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ stats.targets }}</div>
            <div class="stat-label">目标数量</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ stats.jobs }}</div>
            <div class="stat-label">规划任务</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-card class="recent-card">
      <template #header>
        <span>最近任务</span>
      </template>
      <el-table :data="recentJobs" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="scenario_name" label="场景" />
        <el-table-column prop="algorithm" label="算法" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间">
          <template #default="{ row }">
            {{ formatDatetime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewResult(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Dish, Timer, DataAnalysis, Location, Cpu, View } from '@element-plus/icons-vue'
import { formatDatetime } from '@/utils/formatters'
import { planningApi } from '@/api/planning'

const router = useRouter()
const loading = ref(false)
const stats = ref({
  constellations: 0,
  satellites: 0,
  targets: 0,
  jobs: 0
})
const recentJobs = ref([])

onMounted(async () => {
  await loadStats()
  await loadRecentJobs()
})

async function loadStats() {
  // TODO: Load from API
  stats.value = {
    constellations: 3,
    satellites: 200,
    targets: 1000,
    jobs: 12
  }
}

async function loadRecentJobs() {
  loading.value = true
  try {
    const jobs = await planningApi.getAllJobs({ limit: 5 })
    recentJobs.value = jobs
  } catch (error) {
    console.error('Failed to load jobs:', error)
  } finally {
    loading.value = false
  }
}

function getStatusType(status) {
  const types = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return types[status] || 'info'
}

function viewResult(job) {
  router.push(`/results?job_id=${job.id}`)
}
</script>

<style scoped>
.home {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

.hero {
  text-align: center;
  padding: 60px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  margin-bottom: 40px;
}

.hero h1 {
  font-size: 48px;
  margin-bottom: 16px;
  font-weight: 600;
}

.subtitle {
  font-size: 20px;
  opacity: 0.9;
  margin-bottom: 32px;
}

.actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.actions .el-button {
  font-size: 16px;
  padding: 16px 32px;
}

.features {
  margin-bottom: 40px;
}

.feature-card {
  text-align: center;
  padding: 30px 20px;
  height: 100%;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 48px;
  color: #409EFF;
  margin-bottom: 16px;
}

.feature-card h3 {
  font-size: 18px;
  margin-bottom: 12px;
  color: #303133;
}

.feature-card p {
  color: #606266;
  line-height: 1.6;
}

.stats-card {
  margin-bottom: 40px;
}

.stat-item {
  text-align: center;
  padding: 20px;
}

.stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.recent-card {
  margin-bottom: 40px;
}
</style>
