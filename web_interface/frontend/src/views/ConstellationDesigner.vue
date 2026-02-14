<template>
  <div class="constellation-designer">
    <el-container>
      <el-aside width="400px" class="sidebar">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="星座列表" name="list">
            <div class="tab-content">
              <div class="toolbar">
                <el-button type="primary" @click="createConstellation">
                  <el-icon><Plus /></el-icon>新建星座
                </el-button>
                <el-button @click="generateWalker">
                  生成Walker
                </el-button>
              </div>
              <el-table :data="constellations" @row-click="selectConstellation">
                <el-table-column prop="name" label="名称" />
                <el-table-column prop="satellite_count" label="卫星数" width="80" />
                <el-table-column label="操作" width="100">
                  <template #default="{ row }">
                    <el-button type="danger" link @click.stop="deleteConstellation(row)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>

          <el-tab-pane label="卫星详情" name="detail" :disabled="!selectedConstellation">
            <div class="tab-content">
              <SatelliteEditor
                :satellite="selectedSatellite"
                @save="saveSatellite"
                @delete="deleteSatellite"
                @reset="clearSatelliteSelection"
              />
            </div>
          </el-tab-pane>

          <el-tab-pane label="批量生成" name="generate">
            <div class="tab-content">
              <el-form :model="walkerForm" label-width="120px">
                <el-form-item label="星座名称">
                  <el-input v-model="walkerForm.name" placeholder="输入星座名称" />
                </el-form-item>
                <el-form-item label="轨道高度(km)">
                  <el-input-number v-model="walkerForm.altitude" :min="200" :max="2000" style="width: 100%" />
                </el-form-item>
                <el-form-item label="轨道倾角(°)">
                  <el-input-number v-model="walkerForm.inclination" :min="0" :max="180" style="width: 100%" />
                </el-form-item>
                <el-form-item label="轨道面数">
                  <el-input-number v-model="walkerForm.numPlanes" :min="1" :max="20" style="width: 100%" />
                </el-form-item>
                <el-form-item label="每面卫星数">
                  <el-input-number v-model="walkerForm.satsPerPlane" :min="1" :max="50" style="width: 100%" />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="generateWalkerConstellation">生成</el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>
      </el-aside>

      <el-main class="main-content">
        <CesiumViewer
          ref="cesiumViewer"
          :satellites="satellites"
          @entity-click="onEntityClick"
          @viewer-ready="onViewerReady"
        />
        <div class="viewer-controls">
          <el-checkbox v-model="showOrbits">显示轨道</el-checkbox>
          <el-checkbox v-model="showCoverage">显示覆盖</el-checkbox>
          <el-checkbox v-model="showLabels">显示标签</el-checkbox>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CesiumViewer from '@/components/CesiumViewer.vue'
import SatelliteEditor from '@/components/SatelliteEditor.vue'
import { constellationApi } from '@/api/constellations'
import { useConstellationStore } from '@/stores/constellation'

const store = useConstellationStore()
const cesiumViewer = ref(null)
const activeTab = ref('list')
const showOrbits = ref(true)
const showCoverage = ref(false)
const showLabels = ref(true)

const constellations = ref([])
const selectedConstellation = ref(null)
const selectedSatellite = ref(null)
const satellites = ref([])

const walkerForm = ref({
  name: 'Walker Constellation',
  altitude: 500,
  inclination: 97.4,
  numPlanes: 6,
  satsPerPlane: 10
})

onMounted(async () => {
  await loadConstellations()
})

async function loadConstellations() {
  try {
    const data = await constellationApi.getAll()
    constellations.value = data
  } catch (error) {
    ElMessage.error('加载星座列表失败')
  }
}

async function selectConstellation(row) {
  selectedConstellation.value = row
  activeTab.value = 'detail'
  try {
    const data = await constellationApi.getSatellites(row.id)
    satellites.value = data
    store.setSatellites(data)
  } catch (error) {
    ElMessage.error('加载卫星数据失败')
  }
}

function onEntityClick(entity) {
  if (entity.properties?.type === 'satellite') {
    selectedSatellite.value = entity.properties.data
  }
}

function onViewerReady(viewer) {
  console.log('Cesium viewer ready')
}

async function saveSatellite(satellite) {
  try {
    if (satellite.id) {
      await constellationApi.updateSatellite(
        selectedConstellation.value.id,
        satellite.id,
        satellite
      )
    } else {
      await constellationApi.addSatellite(
        selectedConstellation.value.id,
        satellite
      )
    }
    ElMessage.success('保存成功')
    await selectConstellation(selectedConstellation.value)
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

async function deleteSatellite(satelliteId) {
  try {
    await ElMessageBox.confirm('确定要删除这颗卫星吗？', '确认删除')
    await constellationApi.removeSatellite(
      selectedConstellation.value.id,
      satelliteId
    )
    ElMessage.success('删除成功')
    await selectConstellation(selectedConstellation.value)
    selectedSatellite.value = null
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function clearSatelliteSelection() {
  selectedSatellite.value = null
}

async function createConstellation() {
  // TODO: Implement constellation creation dialog
  ElMessage.info('功能开发中')
}

function generateWalker() {
  activeTab.value = 'generate'
}

async function generateWalkerConstellation() {
  try {
    const result = await constellationApi.generateWalker({
      name: walkerForm.value.name,
      altitude_km: walkerForm.value.altitude,
      inclination_deg: walkerForm.value.inclination,
      num_planes: walkerForm.value.numPlanes,
      sats_per_plane: walkerForm.value.satsPerPlane
    })
    ElMessage.success('Walker星座生成成功')
    await loadConstellations()
  } catch (error) {
    ElMessage.error('生成失败')
  }
}

async function deleteConstellation(row) {
  try {
    await ElMessageBox.confirm('确定要删除这个星座吗？', '确认删除')
    await constellationApi.delete(row.id)
    ElMessage.success('删除成功')
    await loadConstellations()
    if (selectedConstellation.value?.id === row.id) {
      selectedConstellation.value = null
      satellites.value = []
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.constellation-designer {
  height: 100vh;
}

.sidebar {
  background: #fff;
  border-right: 1px solid #e4e7ed;
}

.tab-content {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.main-content {
  position: relative;
  padding: 0;
}

.viewer-controls {
  position: absolute;
  bottom: 20px;
  left: 20px;
  background: rgba(255, 255, 255, 0.9);
  padding: 10px 20px;
  border-radius: 8px;
  display: flex;
  gap: 20px;
}
</style>
