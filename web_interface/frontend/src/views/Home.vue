<template>
  <div class="home">
    <!-- 第一行：页面标题 -->
    <div class="header-section">
      <h1 class="main-title">星座任务规划系统</h1>
    </div>

    <!-- 第二行：功能导航 -->
    <el-row :gutter="20" class="nav-section">
      <el-col :span="6" v-for="item in navItems" :key="item.path">
        <div class="nav-card" @click="$router.push(item.path)">
          <el-icon :size="48" class="nav-icon">
            <component :is="item.icon" />
          </el-icon>
          <h3 class="nav-title">{{ item.title }}</h3>
          <p class="nav-desc">{{ item.desc }}</p>
        </div>
      </el-col>
    </el-row>

    <!-- 第三行：规划任务列表 -->
    <div class="tasks-section">
      <div class="section-header">
        <h2>规划任务</h2>
        <el-button type="primary" @click="refreshTasks" :loading="loading">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
      </div>
      <el-table :data="tasks" stripe v-loading="loading" class="tasks-table">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="scenario_name" label="任务名称" />
        <el-table-column prop="algorithm" label="算法" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDatetime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewTask(row)">查看</el-button>
            <el-button size="small" type="success" @click="viewResults(row)">结果</el-button>
            <el-button size="small" type="primary" @click="play3D(row)">
              <el-icon><VideoPlay /></el-icon>播放
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Dish, MapLocation, SetUp, VideoPlay, Refresh } from '@element-plus/icons-vue'
import { formatDatetime } from '@/utils/formatters'
import { planningApi } from '@/api/planning'

const router = useRouter()
const loading = ref(false)
const tasks = ref([])

const navItems = [
  { title: '星座设计', path: '/constellation', icon: 'Dish', desc: '设计Walker星座配置' },
  { title: '场景设计', path: '/scenario', icon: 'MapLocation', desc: '创建观测场景和目标' },
  { title: '算法设计', path: '/algorithm', icon: 'SetUp', desc: '配置规划算法参数' },
  { title: '任务规划计算', path: '/planning', icon: 'VideoPlay', desc: '执行任务规划计算' }
]

onMounted(async () => {
  await refreshTasks()
})

async function refreshTasks() {
  loading.value = true
  try {
    const jobs = await planningApi.getAllJobs({ limit: 20 })
    tasks.value = jobs
  } catch (error) {
    console.error('Failed to load tasks:', error)
    tasks.value = []
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

function viewTask(row) {
  router.push(`/results?job_id=${row.id}`)
}

function viewResults(row) {
  router.push(`/results?job_id=${row.id}&tab=results`)
}

function play3D(row) {
  // 打开三维可视化播放页面
  window.open(`/visualization?job_id=${row.id}`, '_blank')
}
</script>

<style scoped>
.home {
  padding: 40px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 第一行：标题 */
.header-section {
  text-align: center;
  margin-bottom: 40px;
}

.main-title {
  font-size: 36px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

/* 第二行：功能导航 */
.nav-section {
  margin-bottom: 40px;
}

.nav-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 30px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #ebeef5;
  height: 100%;
}

.nav-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.nav-icon {
  color: #409EFF;
  margin-bottom: 16px;
}

.nav-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.nav-desc {
  font-size: 14px;
  color: #909399;
  margin: 0;
  line-height: 1.5;
}

/* 第三行：任务列表 */
.tasks-section {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #ebeef5;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.tasks-table {
  width: 100%;
}
</style>
