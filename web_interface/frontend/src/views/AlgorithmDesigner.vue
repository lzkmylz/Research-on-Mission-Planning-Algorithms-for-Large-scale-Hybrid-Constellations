<template>
  <div class="algorithm-designer">
    <el-container>
      <el-aside width="300px" class="sidebar">
        <div class="sidebar-header">
          <h3>算法配置</h3>
          <el-button type="primary" size="small" @click="handleCreate">
            <el-icon><Plus /></el-icon>新建
          </el-button>
        </div>

        <el-scrollbar class="config-list">
          <el-card
            v-for="config in savedConfigs"
            :key="config.id"
            class="config-card"
            :class="{ active: selectedConfig?.id === config.id }"
            @click="selectConfig(config)"
          >
            <div class="config-name">{{ config.name }}</div>
            <div class="config-meta">
              <el-tag size="small">{{ getAlgorithmName(config.algorithm_id) }}</el-tag>
              <span class="config-time">{{ formatTime(config.created_at) }}</span>
            </div>
          </el-card>
        </el-scrollbar>
      </el-aside>

      <el-main class="main-content">
        <div v-if="!selectedConfig && !isCreating" class="empty-state">
          <el-empty description="请选择或创建一个算法配置" />
        </div>

        <template v-else>
          <div class="config-header">
            <h2>{{ isCreating ? '新建算法配置' : '编辑算法配置' }}</h2>
            <div class="header-actions">
              <el-button v-if="!isCreating" type="danger" @click="handleDelete">
                删除
              </el-button>
              <el-button type="primary" @click="handleSave">
                保存
              </el-button>
            </div>
          </div>

          <AlgorithmPanel
            ref="algorithmPanelRef"
            :algorithms="algorithms"
            :is-running="false"
            @start="handleTest"
          />

          <!-- Config Info Section -->
          <el-card class="config-info-card">
            <template #header>
              <span>配置信息</span>
            </template>
            <el-form :model="configForm" label-width="120px">
              <el-form-item label="配置名称">
                <el-input v-model="configForm.name" placeholder="输入配置名称" />
              </el-form-item>
              <el-form-item label="配置描述">
                <el-input
                  v-model="configForm.description"
                  type="textarea"
                  :rows="2"
                  placeholder="输入配置描述"
                />
              </el-form-item>
              <el-form-item label="设为默认">
                <el-switch v-model="configForm.isDefault" />
              </el-form-item>
            </el-form>
          </el-card>
        </template>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import AlgorithmPanel from '@/components/AlgorithmPanel.vue'

const algorithmPanelRef = ref(null)
const savedConfigs = ref([])
const selectedConfig = ref(null)
const isCreating = ref(false)

const configForm = reactive({
  name: '',
  description: '',
  isDefault: false
})

const algorithms = ref([
  {
    id: 'ga',
    name: '遗传算法 (GA)',
    type: 'genetic',
    description: '基于自然选择和遗传机制的优化算法，适用于大规模复杂问题',
    suitableScenarios: ['大规模星座', '多约束条件', '多目标优化'],
    pros: ['全局搜索能力强', '并行性好', '适用范围广'],
    cons: ['参数敏感', '收敛速度较慢', '计算资源需求大']
  },
  {
    id: 'tabu',
    name: '禁忌搜索 (TS)',
    type: 'tabu',
    description: '基于局部搜索的元启发式算法，通过禁忌表避免循环',
    suitableScenarios: ['中等规模问题', '实时性要求', '局部精细搜索'],
    pros: ['收敛速度快', '内存效率高', '避免局部最优'],
    cons: ['依赖初始解', '参数调节复杂', '全局搜索能力有限']
  },
  {
    id: 'sa',
    name: '模拟退火 (SA)',
    type: 'sa',
    description: '模拟物理退火过程的随机优化算法',
    suitableScenarios: ['组合优化', '连续变量优化', '多峰函数'],
    pros: ['理论保证收敛', '实现简单', '鲁棒性好'],
    cons: ['冷却 schedule 敏感', '收敛慢', '参数调节困难']
  },
  {
    id: 'aco',
    name: '蚁群优化 (ACO)',
    type: 'aco',
    description: '模拟蚂蚁觅食行为的群体智能算法',
    suitableScenarios: ['路径规划', '组合优化', '动态环境'],
    pros: ['正反馈机制', '分布式计算', '适应动态变化'],
    cons: ['收敛慢', '参数敏感', '易陷入局部最优']
  }
])

onMounted(() => {
  loadConfigs()
})

function loadConfigs() {
  // Load from localStorage for now
  const stored = localStorage.getItem('algorithmConfigs')
  if (stored) {
    savedConfigs.value = JSON.parse(stored)
  }
}

function saveConfigs() {
  localStorage.setItem('algorithmConfigs', JSON.stringify(savedConfigs.value))
}

function selectConfig(config) {
  selectedConfig.value = config
  isCreating.value = false
  configForm.name = config.name
  configForm.description = config.description
  configForm.isDefault = config.isDefault || false
}

function handleCreate() {
  isCreating.value = true
  selectedConfig.value = null
  configForm.name = ''
  configForm.description = ''
  configForm.isDefault = false
}

function handleSave() {
  if (!configForm.name) {
    ElMessage.warning('请输入配置名称')
    return
  }

  const panelData = algorithmPanelRef.value?.config
  if (!panelData) {
    ElMessage.warning('请配置算法参数')
    return
  }

  const configData = {
    id: isCreating.value ? Date.now().toString() : selectedConfig.value.id,
    name: configForm.name,
    description: configForm.description,
    algorithm_id: panelData.algorithmId,
    parameters: panelData.parameters,
    objectives: panelData.objectives,
    isDefault: configForm.isDefault,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }

  if (isCreating.value) {
    savedConfigs.value.push(configData)
  } else {
    const index = savedConfigs.value.findIndex(c => c.id === selectedConfig.value.id)
    if (index !== -1) {
      savedConfigs.value[index] = configData
    }
  }

  saveConfigs()
  ElMessage.success('保存成功')
  isCreating.value = false
  selectedConfig.value = configData
}

function handleDelete() {
  if (!selectedConfig.value) return

  ElMessageBox.confirm(
    `确定要删除配置 "${selectedConfig.value.name}" 吗？`,
    '确认删除',
    { type: 'warning' }
  ).then(() => {
    const index = savedConfigs.value.findIndex(c => c.id === selectedConfig.value.id)
    if (index !== -1) {
      savedConfigs.value.splice(index, 1)
      saveConfigs()
      selectedConfig.value = null
      ElMessage.success('删除成功')
    }
  })
}

function handleTest(config) {
  ElMessage.info(`正在测试算法: ${config.algorithmId}`)
  // TODO: Implement test functionality
}

function getAlgorithmName(algorithmId) {
  const algo = algorithms.value.find(a => a.id === algorithmId)
  return algo ? algo.name : algorithmId
}

function formatTime(time) {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleDateString()
}
</script>

<style scoped>
.algorithm-designer {
  height: 100vh;
}

.sidebar {
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  padding: 20px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.config-list {
  height: calc(100% - 60px);
}

.config-card {
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.config-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.config-card.active {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.config-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.config-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-time {
  font-size: 12px;
  color: #909399;
}

.main-content {
  padding: 20px;
  background: #fff;
  overflow-y: auto;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.config-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.config-info-card {
  margin-top: 20px;
}
</style>
