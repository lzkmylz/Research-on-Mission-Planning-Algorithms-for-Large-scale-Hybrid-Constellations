<template>
  <div class="scenario-designer">
    <el-container>
      <el-aside width="300px" class="sidebar">
        <div class="sidebar-header">
          <h3>场景列表</h3>
          <el-button type="primary" size="small" @click="handleCreate">
            <el-icon><Plus /></el-icon>新建
          </el-button>
        </div>
        <el-scrollbar class="scenario-list">
          <el-card
            v-for="scenario in scenarios"
            :key="scenario.id"
            class="scenario-card"
            :class="{ active: selectedScenario?.id === scenario.id }"
            @click="selectScenario(scenario)"
          >
            <div class="scenario-name">{{ scenario.name }}</div>
            <div class="scenario-meta">
              <span>{{ scenario.target_count }} 目标</span>
              <el-tag size="small" :type="getStatusType(scenario.status)">
                {{ scenario.status }}
              </el-tag>
            </div>
          </el-card>
        </el-scrollbar>
      </el-aside>

      <el-main class="main-content">
        <div v-if="!selectedScenario" class="empty-state">
          <el-empty description="请选择或创建一个场景" />
        </div>

        <template v-else>
          <el-tabs v-model="activeTab" class="scenario-tabs">
            <el-tab-pane label="基本信息" name="basic">
              <el-form :model="form" label-width="120px" class="scenario-form">
                <el-form-item label="场景名称">
                  <el-input v-model="form.name" placeholder="输入场景名称" />
                </el-form-item>
                <el-form-item label="场景描述">
                  <el-input
                    v-model="form.description"
                    type="textarea"
                    :rows="3"
                    placeholder="输入场景描述"
                  />
                </el-form-item>
                <el-form-item label="时间窗口">
                  <el-date-picker
                    v-model="form.timeRange"
                    type="datetimerange"
                    range-separator="至"
                    start-placeholder="开始时间"
                    end-placeholder="结束时间"
                    style="width: 100%"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="handleSave">保存</el-button>
                  <el-button @click="handleReset">重置</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="目标管理" name="targets">
              <TargetManager
                :targets="targets"
                @add="handleAddTarget"
                @edit="handleEditTarget"
                @delete="handleDeleteTarget"
                @import="handleImportTargets"
                @export="handleExportTargets"
              />
            </el-tab-pane>

            <el-tab-pane label="约束设置" name="constraints">
              <el-form :model="constraints" label-width="150px" class="scenario-form">
                <el-divider>云层约束</el-divider>
                <el-form-item label="启用云层约束">
                  <el-switch v-model="constraints.cloudEnabled" />
                </el-form-item>
                <el-form-item label="云层覆盖区域" v-if="constraints.cloudEnabled">
                  <el-input
                    v-model="constraints.cloudRegions"
                    type="textarea"
                    :rows="3"
                    placeholder="输入云层覆盖的多边形区域坐标"
                  />
                </el-form-item>

                <el-divider>存储约束</el-divider>
                <el-form-item label="卫星存储上限">
                  <el-input-number v-model="constraints.storageLimit" :min="1" :max="1000" />
                  <span class="unit">GB</span>
                </el-form-item>

                <el-divider>能源约束</el-divider>
                <el-form-item label="单次成像功耗">
                  <el-input-number v-model="constraints.imagingPower" :min="1" :max="1000" />
                  <span class="unit">W</span>
                </el-form-item>

                <el-form-item>
                  <el-button type="primary" @click="handleSaveConstraints">保存约束</el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </template>
      </el-main>
    </el-container>

    <!-- Create Scenario Dialog -->
    <el-dialog v-model="createDialogVisible" title="新建场景" width="500px">
      <el-form :model="newScenario" label-width="100px">
        <el-form-item label="场景名称" required>
          <el-input v-model="newScenario.name" placeholder="输入场景名称" />
        </el-form-item>
        <el-form-item label="场景描述">
          <el-input
            v-model="newScenario.description"
            type="textarea"
            :rows="3"
            placeholder="输入场景描述"
          />
        </el-form-item>
        <el-form-item label="时间窗口" required>
          <el-date-picker
            v-model="newScenario.timeRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import TargetManager from '@/components/TargetManager.vue'
import { scenarioApi } from '@/api/scenarios'

const scenarios = ref([])
const selectedScenario = ref(null)
const activeTab = ref('basic')
const createDialogVisible = ref(false)
const targets = ref([])

const form = reactive({
  name: '',
  description: '',
  timeRange: []
})

const constraints = reactive({
  cloudEnabled: false,
  cloudRegions: '',
  storageLimit: 100,
  imagingPower: 50
})

const newScenario = reactive({
  name: '',
  description: '',
  timeRange: []
})

onMounted(async () => {
  await loadScenarios()
})

async function loadScenarios() {
  try {
    const data = await scenarioApi.getAll()
    scenarios.value = data
  } catch (error) {
    ElMessage.error('加载场景列表失败')
  }
}

function selectScenario(scenario) {
  selectedScenario.value = scenario
  form.name = scenario.name
  form.description = scenario.description
  form.timeRange = [scenario.start_time, scenario.end_time]
  loadTargets(scenario.id)
}

async function loadTargets(scenarioId) {
  try {
    const data = await scenarioApi.getTargets(scenarioId)
    targets.value = data
  } catch (error) {
    ElMessage.error('加载目标列表失败')
  }
}

function handleCreate() {
  newScenario.name = ''
  newScenario.description = ''
  newScenario.timeRange = []
  createDialogVisible.value = true
}

async function confirmCreate() {
  if (!newScenario.name || !newScenario.timeRange.length) {
    ElMessage.warning('请填写必填项')
    return
  }

  try {
    const created = await scenarioApi.create({
      name: newScenario.name,
      description: newScenario.description,
      start_time: newScenario.timeRange[0],
      end_time: newScenario.timeRange[1]
    })
    ElMessage.success('场景创建成功')
    createDialogVisible.value = false
    await loadScenarios()
    selectScenario(created)
  } catch (error) {
    ElMessage.error('创建场景失败')
  }
}

async function handleSave() {
  if (!selectedScenario.value) return

  try {
    await scenarioApi.update(selectedScenario.value.id, {
      name: form.name,
      description: form.description,
      start_time: form.timeRange[0],
      end_time: form.timeRange[1]
    })
    ElMessage.success('保存成功')
    await loadScenarios()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

function handleReset() {
  if (selectedScenario.value) {
    form.name = selectedScenario.value.name
    form.description = selectedScenario.value.description
    form.timeRange = [selectedScenario.value.start_time, selectedScenario.value.end_time]
  }
}

async function handleSaveConstraints() {
  ElMessage.success('约束设置已保存')
}

function handleAddTarget(target) {
  console.log('Add target:', target)
}

function handleEditTarget(target) {
  console.log('Edit target:', target)
}

function handleDeleteTarget(targetId) {
  console.log('Delete target:', targetId)
}

function handleImportTargets(data) {
  console.log('Import targets:', data)
}

function handleExportTargets() {
  console.log('Export targets')
}

function getStatusType(status) {
  const types = {
    'active': 'success',
    'inactive': 'info',
    'archived': 'warning'
  }
  return types[status] || 'info'
}
</script>

<style scoped>
.scenario-designer {
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

.scenario-list {
  height: calc(100% - 60px);
}

.scenario-card {
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.scenario-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.scenario-card.active {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.scenario-name {
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.scenario-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.main-content {
  padding: 20px;
  background: #fff;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.scenario-form {
  max-width: 600px;
  padding: 20px;
}

.unit {
  margin-left: 8px;
  color: #606266;
}
</style>
