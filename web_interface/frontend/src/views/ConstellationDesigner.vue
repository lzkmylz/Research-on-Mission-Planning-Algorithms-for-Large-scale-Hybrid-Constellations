<template>
  <div class="constellation-designer">
    <el-container>
      <el-aside width="250px" class="sidebar">
        <div class="sidebar-header">
          <h3>星座设计</h3>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="nav-menu"
          @select="handleMenuSelect"
        >
          <el-menu-item index="single">
            <el-icon><Dish /></el-icon>
            <span>单星设计</span>
          </el-menu-item>
          <el-menu-item index="walker">
            <el-icon><Connection /></el-icon>
            <span>Walker星座生成</span>
          </el-menu-item>
          <el-menu-item index="payload">
            <el-icon><Box /></el-icon>
            <span>载荷设计</span>
          </el-menu-item>
          <el-divider />
          <el-menu-item index="home">
            <el-icon><HomeFilled /></el-icon>
            <span>返回首页</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-main class="main-content">
        <!-- 单星设计 -->
        <div v-if="activeMenu === 'single'" class="single-satellite-page">
          <div class="page-header">
            <h2>单星设计</h2>
            <div class="toolbar">
              <el-input
                v-model="searchQuery"
                placeholder="搜索卫星名称"
                clearable
                style="width: 200px"
                @keyup.enter="handleSearch"
                @clear="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
              <el-button type="primary" @click="showCreateSatelliteDialog">
                <el-icon><Plus /></el-icon>新建
              </el-button>
              <el-button type="danger" :disabled="selectedSatellites.length === 0" @click="batchDeleteSatellites">
                <el-icon><Delete /></el-icon>删除
              </el-button>
            </div>
          </div>
          <div class="page-content">
            <el-table
              :data="filteredSatellites"
              stripe
              @selection-change="handleSatelliteSelectionChange"
              v-loading="satelliteLoading"
            >
              <el-table-column type="selection" width="55" />
              <el-table-column prop="name" label="卫星名称" min-width="120" />
              <el-table-column prop="norad_id" label="NORAD ID" width="100" />
              <el-table-column prop="orbit_type" label="轨道类型" width="90" />
              <el-table-column prop="semi_major_axis_km" label="半长轴(km)" width="110">
                <template #default="{ row }">
                  {{ row.semi_major_axis_km.toFixed(2) }}
                </template>
              </el-table-column>
              <el-table-column prop="eccentricity" label="偏心率" width="90">
                <template #default="{ row }">
                  {{ row.eccentricity.toFixed(4) }}
                </template>
              </el-table-column>
              <el-table-column prop="payloads" label="载荷" width="120">
                <template #default="{ row }">
                  <el-tooltip v-if="row.payloads && row.payloads.length > 0" placement="top">
                    <template #content>
                      <div v-for="(p, idx) in row.payloads" :key="idx">
                        {{ p.name }} ({{ getPayloadTypeLabel(p.type) }})
                      </div>
                    </template>
                    <el-tag size="small" :type="getPayloadTagType(row.payloads[0].type)">
                      {{ getPayloadTypeLabel(row.payloads[0].type) }}
                      <span v-if="row.payloads.length > 1">+{{ row.payloads.length - 1 }}</span>
                    </el-tag>
                  </el-tooltip>
                  <el-tag v-else size="small" type="info">无载荷</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="solar_panel_power_w" label="功率(W)" width="90" />
              <el-table-column prop="storage_capacity_gb" label="存储(GB)" width="95" />
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="editSatellite(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteSatelliteByRow(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="satellitePage"
                v-model:page-size="satellitePageSize"
                :page-sizes="[20, 50, 100]"
                :total="totalSatellites"
                layout="total, sizes, prev, pager, next"
                @size-change="handleSatelliteSizeChange"
                @current-change="handleSatellitePageChange"
              />
            </div>
          </div>

          <!-- 新建/编辑卫星对话框 -->
          <el-dialog
            v-model="editDialogVisible"
            :title="isEditing ? '编辑卫星参数' : '新建卫星'"
            width="700px"
            :close-on-click-modal="false"
          >
            <el-tabs v-model="editActiveTab" v-if="editForm">
              <!-- 基本信息 -->
              <el-tab-pane label="基本信息" name="basic">
                <el-form :model="editForm" label-width="160px">
                  <el-form-item label="卫星名称" required>
                    <el-input v-model="editForm.name" placeholder="输入卫星名称" />
                  </el-form-item>
                  <el-form-item label="NORAD ID">
                    <el-input v-model="editForm.norad_id" placeholder="输入NORAD ID" />
                  </el-form-item>
                  <el-form-item label="卫星编号">
                    <el-input v-model="editForm.satellite_code" placeholder="如: SAT-001" />
                  </el-form-item>
                  <el-form-item label="所属星座">
                    <el-input v-model="editForm.constellation_name" placeholder="输入所属星座名称" />
                  </el-form-item>
                </el-form>
              </el-tab-pane>

              <!-- 轨道六根数 (NASA格式) -->
              <el-tab-pane label="轨道六根数" name="orbit">
                <el-alert
                  title="NASA标准开普勒轨道六根数"
                  description="a: 半长轴  e: 偏心率  i: 轨道倾角  Ω: 升交点赤经  ω: 近地点幅角  M: 平近点角"
                  type="info"
                  :closable="false"
                  style="margin-bottom: 15px"
                />
                <el-form :model="editForm" label-width="160px">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="半长轴 a (km)">
                        <el-input-number
                          v-model="editForm.semi_major_axis_km"
                          :min="6500"
                          :max="50000"
                          :precision="3"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="偏心率 e">
                        <el-input-number
                          v-model="editForm.eccentricity"
                          :min="0"
                          :max="1"
                          :precision="6"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="轨道倾角 i (°)">
                        <el-input-number
                          v-model="editForm.inclination_deg"
                          :min="0"
                          :max="180"
                          :precision="4"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="升交点赤经 Ω (°)">
                        <el-input-number
                          v-model="editForm.raan_deg"
                          :min="0"
                          :max="360"
                          :precision="4"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="近地点幅角 ω (°)">
                        <el-input-number
                          v-model="editForm.arg_perigee_deg"
                          :min="0"
                          :max="360"
                          :precision="4"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="平近点角 M (°)">
                        <el-input-number
                          v-model="editForm.mean_anomaly_deg"
                          :min="0"
                          :max="360"
                          :precision="4"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-divider />
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="参考历元 (UTC)">
                        <el-date-picker
                          v-model="editForm.epoch"
                          type="datetime"
                          placeholder="选择历元时间"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="轨道类型">
                        <el-select v-model="editForm.orbit_type" style="width: 100%">
                          <el-option label="LEO (低地球轨道)" value="LEO" />
                          <el-option label="MEO (中地球轨道)" value="MEO" />
                          <el-option label="GEO (地球同步轨道)" value="GEO" />
                          <el-option label="SSO (太阳同步轨道)" value="SSO" />
                          <el-option label="GTO (地球同步转移轨道)" value="GTO" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                </el-form>
              </el-tab-pane>

              <!-- 载荷配置 -->
              <el-tab-pane label="载荷配置" name="payload">
                <div v-if="editForm.payloads" class="payload-list">
                  <!-- 载荷列表 -->
                  <div class="payload-list-header">
                    <span>载荷列表 ({{ editForm.payloads.length }})</span>
                    <el-button type="primary" size="small" @click="showAddPayloadDialog">
                      <el-icon><Plus /></el-icon>添加载荷
                    </el-button>
                  </div>

                  <el-table :data="editForm.payloads" size="small" style="margin-top: 10px">
                    <el-table-column prop="name" label="名称" min-width="100" />
                    <el-table-column prop="type" label="类型" width="90">
                      <template #default="{ row }">
                        <el-tag size="small" :type="getPayloadTagType(row.type)">
                          {{ getPayloadTypeLabel(row.type) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    <el-table-column prop="resolution_m" label="分辨率" width="80">
                      <template #default="{ row }">
                        {{ row.resolution_m }}m
                      </template>
                    </el-table-column>
                    <el-table-column prop="swath_km" label="幅宽" width="70">
                      <template #default="{ row }">
                        {{ row.swath_km }}km
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="120" fixed="right">
                      <template #default="{ $index }">
                        <el-button size="small" text @click="editPayload($index)">编辑</el-button>
                        <el-button size="small" text type="danger" @click="deletePayload($index)">删除</el-button>
                      </template>
                    </el-table-column>
                  </el-table>

                  <el-empty v-if="editForm.payloads.length === 0" description="暂无载荷，请点击添加" />
                </div>
              </el-tab-pane>

              <!-- 能源配置 -->
              <el-tab-pane label="能源配置" name="power">
                <el-form :model="editForm" label-width="180px">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="太阳能板功率 (W)">
                        <el-input-number
                          v-model="editForm.solar_panel_power_w"
                          :min="0"
                          :max="10000"
                          :precision="1"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="电池容量 (Ah)">
                        <el-input-number
                          v-model="editForm.battery_capacity_ah"
                          :min="0"
                          :max="500"
                          :precision="2"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="电池电压 (V)">
                        <el-input-number
                          v-model="editForm.battery_voltage_v"
                          :min="0"
                          :max="100"
                          :precision="1"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="平均功耗 (W)">
                        <el-input-number
                          v-model="editForm.avg_power_consumption_w"
                          :min="0"
                          :max="5000"
                          :precision="1"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="成像功耗 (W)">
                    <el-input-number
                      v-model="editForm.imaging_power_w"
                      :min="0"
                      :max="1000"
                      :precision="1"
                      style="width: 100%"
                    />
                  </el-form-item>
                  <el-form-item label="数传功耗 (W)">
                    <el-input-number
                      v-model="editForm.downlink_power_w"
                      :min="0"
                      :max="500"
                      :precision="1"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-form>
              </el-tab-pane>

              <!-- 存储配置 -->
              <el-tab-pane label="存储配置" name="storage">
                <el-form :model="editForm" label-width="180px">
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="固态存储容量 (GB)">
                        <el-input-number
                          v-model="editForm.storage_capacity_gb"
                          :min="0"
                          :max="10000"
                          :precision="0"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="存储类型">
                        <el-select v-model="editForm.storage_type" style="width: 100%">
                          <el-option label="SSD固态硬盘" value="ssd" />
                          <el-option label="MLC闪存" value="mlc" />
                          <el-option label="SLC闪存" value="slc" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="写入速率 (Mbps)">
                    <el-input-number
                      v-model="editForm.storage_write_rate_mbps"
                      :min="0"
                      :max="10000"
                      :precision="0"
                      style="width: 100%"
                    />
                  </el-form-item>
                  <el-form-item label="读取速率 (Mbps)">
                    <el-input-number
                      v-model="editForm.storage_read_rate_mbps"
                      :min="0"
                      :max="10000"
                      :precision="0"
                      style="width: 100%"
                    />
                  </el-form-item>
                  <el-divider />
                  <el-row :gutter="20">
                    <el-col :span="12">
                      <el-form-item label="数传速率 (Mbps)">
                        <el-input-number
                          v-model="editForm.downlink_rate_mbps"
                          :min="0"
                          :max="10000"
                          :precision="0"
                          style="width: 100%"
                        />
                      </el-form-item>
                    </el-col>
                    <el-col :span="12">
                      <el-form-item label="调制方式">
                        <el-select v-model="editForm.modulation" style="width: 100%">
                          <el-option label="QPSK" value="qpsk" />
                          <el-option label="8PSK" value="8psk" />
                          <el-option label="16QAM" value="16qam" />
                          <el-option label="BPSK" value="bpsk" />
                        </el-select>
                      </el-form-item>
                    </el-col>
                  </el-row>
                  <el-form-item label="天线增益 (dBi)">
                    <el-input-number
                      v-model="editForm.antenna_gain_dbi"
                      :min="0"
                      :max="50"
                      :precision="1"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-form>
              </el-tab-pane>
            </el-tabs>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="editDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="saveSatelliteEdit">保存</el-button>
              </span>
            </template>
          </el-dialog>

          <!-- 载荷编辑对话框 -->
          <el-dialog
            v-model="payloadDialogVisible"
            :title="isEditingPayload ? '编辑载荷' : '添加载荷'"
            width="500px"
            :close-on-click-modal="false"
          >
            <el-form :model="payloadForm" label-width="120px">
              <el-form-item label="载荷名称" required>
                <el-input v-model="payloadForm.name" placeholder="输入载荷名称" />
              </el-form-item>
              <el-form-item label="载荷类型">
                <el-select v-model="payloadForm.type" style="width: 100%">
                  <el-option label="光学相机" value="optical" />
                  <el-option label="SAR雷达" value="sar" />
                  <el-option label="红外相机" value="infrared" />
                  <el-option label="多光谱相机" value="multispectral" />
                  <el-option label="通信载荷" value="communication" />
                  <el-option label="科学仪器" value="scientific" />
                </el-select>
              </el-form-item>
              <el-row :gutter="20">
                <el-col :span="12">
                  <el-form-item label="分辨率 (m)">
                    <el-input-number
                      v-model="payloadForm.resolution_m"
                      :min="0.1"
                      :max="1000"
                      :precision="2"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="幅宽 (km)">
                    <el-input-number
                      v-model="payloadForm.swath_km"
                      :min="1"
                      :max="2000"
                      :precision="1"
                      style="width: 100%"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
              <el-form-item label="工作模式">
                <el-checkbox-group v-model="payloadForm.operation_modes">
                  <el-checkbox label="strip">推扫</el-checkbox>
                  <el-checkbox label="stare">凝视</el-checkbox>
                  <el-checkbox label="scan">扫描</el-checkbox>
                  <el-checkbox label="video">视频</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item label="载荷质量 (kg)">
                <el-input-number
                  v-model="payloadForm.mass_kg"
                  :min="0"
                  :max="10000"
                  :precision="2"
                  style="width: 100%"
                />
              </el-form-item>
            </el-form>
            <template #footer>
              <span class="dialog-footer">
                <el-button @click="payloadDialogVisible = false">取消</el-button>
                <el-button type="primary" @click="savePayloadToSatellite">保存</el-button>
              </span>
            </template>
          </el-dialog>
        </div>

        <!-- Walker星座生成 -->
        <div v-else-if="activeMenu === 'walker'" class="content-panel">
          <h2>Walker星座生成</h2>
          <div class="panel-content">
            <el-form :model="walkerForm" label-width="140px">
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
                <el-button type="primary" @click="generateWalkerConstellation">
                  <el-icon><Plus /></el-icon>生成Walker星座
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 载荷设计 -->
        <div v-else-if="activeMenu === 'payload'" class="content-panel">
          <h2>载荷设计</h2>
          <div class="panel-content">
            <el-form :model="payloadForm" label-width="140px">
              <el-form-item label="载荷名称">
                <el-input v-model="payloadForm.name" placeholder="输入载荷名称" />
              </el-form-item>
              <el-form-item label="载荷类型">
                <el-select v-model="payloadForm.type" style="width: 100%">
                  <el-option label="光学相机" value="optical" />
                  <el-option label="SAR雷达" value="sar" />
                  <el-option label="红外相机" value="infrared" />
                  <el-option label="多光谱相机" value="multispectral" />
                </el-select>
              </el-form-item>
              <el-form-item label="分辨率(m)">
                <el-input-number v-model="payloadForm.resolution" :min="0.1" :max="100" :precision="1" style="width: 100%" />
              </el-form-item>
              <el-form-item label="幅宽(km)">
                <el-input-number v-model="payloadForm.swath" :min="1" :max="1000" style="width: 100%" />
              </el-form-item>
              <el-form-item label="工作模式">
                <el-checkbox-group v-model="payloadForm.modes">
                  <el-checkbox label="strip">推扫</el-checkbox>
                  <el-checkbox label="stare">凝视</el-checkbox>
                  <el-checkbox label="scan">扫描</el-checkbox>
                </el-checkbox-group>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="savePayload">
                  <el-icon><Check /></el-icon>保存载荷
                </el-button>
              </el-form-item>
            </el-form>
          </div>
        </div>

        <!-- 3D可视化区域 (仅Walker星座生成和载荷设计时显示) -->
        <template v-if="activeMenu !== 'single'">
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
        </template>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Plus, Delete, Dish, Connection, Box, HomeFilled, Check, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import CesiumViewer from '@/components/CesiumViewer.vue'
import SatelliteEditor from '@/components/SatelliteEditor.vue'
import { constellationApi } from '@/api/constellations'
import { satelliteApi } from '@/api/satellites'
import { useConstellationStore } from '@/stores/constellation'

const router = useRouter()
const store = useConstellationStore()
const cesiumViewer = ref(null)
const activeMenu = ref('walker')
const showOrbits = ref(true)
const showCoverage = ref(false)
const showLabels = ref(true)

const constellations = ref([])
const selectedConstellation = ref(null)
const selectedSatellite = ref(null)
const satellites = ref([])

// 单星设计相关数据
const searchQuery = ref('')
const selectedSatellites = ref([])
const satelliteLoading = ref(false)
const satellitePage = ref(1)
const satellitePageSize = ref(20)
const totalSatellites = ref(0)
const satelliteList = ref([])
const editDialogVisible = ref(false)
const editForm = ref(null)
const editActiveTab = ref('basic')
const isEditing = ref(false)

// 载荷管理相关
const payloadDialogVisible = ref(false)
const isEditingPayload = ref(false)
const editingPayloadIndex = ref(-1)
const payloadForm = ref({
  name: '',
  type: 'optical',
  resolution_m: 2.0,
  swath_km: 50,
  operation_modes: ['strip'],
  mass_kg: 100
})

const walkerForm = ref({
  name: 'Walker Constellation',
  altitude: 500,
  inclination: 97.4,
  numPlanes: 6,
  satsPerPlane: 10
})

// 计算属性：过滤后的卫星列表（现在直接使用API返回的数据）
const filteredSatellites = computed(() => {
  return satelliteList.value
})

onMounted(async () => {
  await loadConstellations()
  await loadSatelliteList()
})

function handleMenuSelect(index) {
  if (index === 'home') {
    router.push('/')
  } else {
    activeMenu.value = index
  }
}

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
  ElMessage.info('功能开发中')
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

// 载荷管理方法
function showAddPayloadDialog() {
  isEditingPayload.value = false
  editingPayloadIndex.value = -1
  payloadForm.value = {
    name: '',
    type: 'optical',
    resolution_m: 2.0,
    swath_km: 50,
    operation_modes: ['strip'],
    mass_kg: 100
  }
  payloadDialogVisible.value = true
}

function editPayload(index) {
  if (!editForm.value.payloads || index < 0 || index >= editForm.value.payloads.length) {
    return
  }
  isEditingPayload.value = true
  editingPayloadIndex.value = index
  const payload = editForm.value.payloads[index]
  payloadForm.value = {
    name: payload.name || '',
    type: payload.type || 'optical',
    resolution_m: payload.resolution_m || 2.0,
    swath_km: payload.swath_km || 50,
    operation_modes: payload.operation_modes || ['strip'],
    mass_kg: payload.mass_kg || 100
  }
  payloadDialogVisible.value = true
}

async function deletePayload(index) {
  if (!editForm.value.payloads || index < 0 || index >= editForm.value.payloads.length) {
    return
  }
  try {
    await ElMessageBox.confirm(
      `确定要删除载荷 "${editForm.value.payloads[index].name}" 吗？`,
      '确认删除'
    )
    editForm.value.payloads.splice(index, 1)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function savePayloadToSatellite() {
  if (!payloadForm.value.name) {
    ElMessage.warning('请输入载荷名称')
    return
  }

  if (!editForm.value.payloads) {
    editForm.value.payloads = []
  }

  const payloadData = {
    name: payloadForm.value.name,
    type: payloadForm.value.type,
    resolution_m: payloadForm.value.resolution_m,
    swath_km: payloadForm.value.swath_km,
    operation_modes: payloadForm.value.operation_modes,
    mass_kg: payloadForm.value.mass_kg
  }

  if (isEditingPayload.value && editingPayloadIndex.value >= 0) {
    // 更新现有载荷
    editForm.value.payloads[editingPayloadIndex.value] = payloadData
    ElMessage.success('载荷更新成功')
  } else {
    // 添加新载荷
    editForm.value.payloads.push(payloadData)
    ElMessage.success('载荷添加成功')
  }

  payloadDialogVisible.value = false
}

// 单星设计相关方法
async function loadSatelliteList() {
  satelliteLoading.value = true
  try {
    // 从后端API获取卫星列表
    const response = await satelliteApi.getAll({
      skip: (satellitePage.value - 1) * satellitePageSize.value,
      limit: satellitePageSize.value,
      search: searchQuery.value || undefined
    })

    satelliteList.value = response.items || []
    totalSatellites.value = response.total || 0
  } catch (error) {
    console.error('加载卫星列表失败:', error)
    ElMessage.error('加载卫星列表失败')
    satelliteList.value = []
    totalSatellites.value = 0
  } finally {
    satelliteLoading.value = false
  }
}

// 注意：generateMockSatellites 函数已移除，现在使用后端API获取真实数据

function handleSatelliteSelectionChange(selection) {
  selectedSatellites.value = selection
}

function showCreateSatelliteDialog() {
  // 初始化新建卫星的默认数据
  isEditing.value = false
  editForm.value = {
    // 基本信息
    id: '',
    name: '',
    norad_id: '',
    satellite_code: '',
    constellation_name: '',

    // 轨道六根数 (NASA格式: a, e, i, Ω, ω, M)
    semi_major_axis_km: 6878.137,
    eccentricity: 0.001,
    inclination_deg: 97.4,
    raan_deg: 0,
    arg_perigee_deg: 0,
    mean_anomaly_deg: 0,
    epoch: new Date(),
    orbit_type: 'LEO',

    // 载荷配置 (多载荷数组)
    payloads: [
      {
        name: '主载荷',
        type: 'optical',
        resolution_m: 2.0,
        swath_km: 50,
        operation_modes: ['strip'],
        mass_kg: 100
      }
    ],

    // 能源配置
    solar_panel_power_w: 500,
    battery_capacity_ah: 40,
    battery_voltage_v: 28,
    avg_power_consumption_w: 200,
    imaging_power_w: 80,
    downlink_power_w: 60,

    // 存储配置
    storage_capacity_gb: 500,
    storage_type: 'ssd',
    storage_write_rate_mbps: 500,
    storage_read_rate_mbps: 800,
    downlink_rate_mbps: 450,
    modulation: 'qpsk',
    antenna_gain_dbi: 15
  }
  editActiveTab.value = 'basic'
  editDialogVisible.value = true
}

async function batchDeleteSatellites() {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedSatellites.value.length} 颗卫星吗？`,
      '确认删除',
      { type: 'warning' }
    )
    const ids = selectedSatellites.value.map(s => s.id)

    // 调用后端API批量删除
    const results = await satelliteApi.batchDelete(ids)
    const successCount = results.filter(r => r.success).length
    const failCount = results.length - successCount

    if (failCount > 0) {
      ElMessage.warning(`删除完成：成功 ${successCount} 个，失败 ${failCount} 个`)
    } else {
      ElMessage.success(`成功删除 ${successCount} 颗卫星`)
    }

    // 重新加载列表
    await loadSatelliteList()
    selectedSatellites.value = []
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

function editSatellite(satellite) {
  // 深拷贝卫星数据到编辑表单，包含完整的轨道六根数和能力配置
  isEditing.value = true
  editForm.value = {
    // 基本信息
    id: satellite.id,
    name: satellite.name || '',
    norad_id: satellite.norad_id || '',
    satellite_code: satellite.satellite_code || '',
    constellation_name: satellite.constellation_name || '',

    // 轨道六根数 (NASA格式: a, e, i, Ω, ω, M)
    semi_major_axis_km: satellite.semi_major_axis_km || 6878.137, // 地球半径 + 500km
    eccentricity: satellite.eccentricity || 0.001,
    inclination_deg: satellite.inclination_deg || 97.4,
    raan_deg: satellite.raan_deg || 0,
    arg_perigee_deg: satellite.arg_perigee_deg || 0,
    mean_anomaly_deg: satellite.mean_anomaly_deg || 0,
    epoch: satellite.epoch || new Date(),
    orbit_type: satellite.orbit_type || 'LEO',

    // 载荷配置 (多载荷数组)
    payloads: satellite.payloads && satellite.payloads.length > 0
      ? satellite.payloads.map(p => ({ ...p }))
      : [{
          name: '主载荷',
          type: satellite.payload_type || 'optical',
          resolution_m: satellite.resolution_m || 2.0,
          swath_km: satellite.swath_km || 50,
          operation_modes: satellite.operation_modes || ['strip'],
          mass_kg: satellite.payload_mass_kg || 100
        }],

    // 能源配置
    solar_panel_power_w: satellite.solar_panel_power_w || 500,
    battery_capacity_ah: satellite.battery_capacity_ah || 40,
    battery_voltage_v: satellite.battery_voltage_v || 28,
    avg_power_consumption_w: satellite.avg_power_consumption_w || 200,
    imaging_power_w: satellite.imaging_power_w || 80,
    downlink_power_w: satellite.downlink_power_w || 60,

    // 存储配置
    storage_capacity_gb: satellite.storage_capacity_gb || 500,
    storage_type: satellite.storage_type || 'ssd',
    storage_write_rate_mbps: satellite.storage_write_rate_mbps || 500,
    storage_read_rate_mbps: satellite.storage_read_rate_mbps || 800,
    downlink_rate_mbps: satellite.downlink_rate_mbps || 450,
    modulation: satellite.modulation || 'qpsk',
    antenna_gain_dbi: satellite.antenna_gain_dbi || 15
  }
  editActiveTab.value = 'basic'
  editDialogVisible.value = true
}

async function saveSatelliteEdit() {
  if (!editForm.value.name) {
    ElMessage.warning('请输入卫星名称')
    return
  }

  try {
    if (isEditing.value) {
      // 更新现有卫星 - 调用后端API
      const updateData = { ...editForm.value }
      delete updateData.id  // 移除id，不作为更新数据
      delete updateData.created_at  // 移除只读字段
      delete updateData.updated_at

      await satelliteApi.update(editForm.value.id, updateData)
      ElMessage.success('卫星参数保存成功')
    } else {
      // 新建卫星 - 调用后端API
      const createData = { ...editForm.value }
      delete createData.id  // 后端会生成id

      await satelliteApi.create(createData)
      ElMessage.success('新建卫星成功')
    }

    // 重新加载列表
    await loadSatelliteList()
    editDialogVisible.value = false
  } catch (error) {
    console.error('保存卫星失败:', error)
    ElMessage.error('保存失败: ' + (error.response?.data?.detail || error.message))
  }
}

// 注意：此方法已废弃，保留是为了兼容性
// 现在所有卫星数据都通过后端API管理，不再使用localStorage
function saveCustomSatelliteToStorage(satellite) {
  console.warn('saveCustomSatelliteToStorage is deprecated. Use satelliteApi instead.')
}

async function deleteSatelliteByRow(satellite) {
  try {
    await ElMessageBox.confirm(`确定要删除卫星 "${satellite.name}" 吗？`, '确认删除')

    // 调用后端 API 删除卫星
    await satelliteApi.delete(satellite.id)

    // 重新加载列表
    await loadSatelliteList()
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除卫星失败:', error)
      ElMessage.error('删除失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

async function handleSatelliteSizeChange(size) {
  satellitePageSize.value = size
  satellitePage.value = 1
  await loadSatelliteList()
}

async function handleSatellitePageChange(page) {
  satellitePage.value = page
  await loadSatelliteList()
}

async function handleSearch() {
  satellitePage.value = 1
  await loadSatelliteList()
}

// 载荷类型标签转换
function getPayloadTypeLabel(type) {
  const labels = {
    optical: '光学',
    sar: 'SAR',
    infrared: '红外',
    multispectral: '多光谱',
    communication: '通信',
    scientific: '科学'
  }
  return labels[type] || type
}

// 载荷类型标签样式
function getPayloadTagType(type) {
  const types = {
    optical: 'primary',
    sar: 'success',
    infrared: 'warning',
    multispectral: 'info',
    communication: '',
    scientific: 'danger'
  }
  return types[type] || ''
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

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.nav-menu {
  border-right: none;
}

.main-content {
  position: relative;
  padding: 0;
}

.content-panel {
  position: absolute;
  top: 20px;
  left: 20px;
  width: 400px;
  max-height: calc(100% - 100px);
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 10;
  overflow-y: auto;
}

.content-panel h2 {
  margin: 0;
  padding: 16px 20px;
  font-size: 16px;
  border-bottom: 1px solid #e4e7ed;
}

.panel-content {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
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
  z-index: 10;
}

/* 单星设计页面样式 */
.single-satellite-page {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
  color: #303133;
}

.page-content {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 编辑对话框样式优化 */
:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-input-number) {
  width: 100%;
}

/* 轨道参数提示样式 */
:deep(.el-alert__title) {
  font-weight: 600;
  font-size: 14px;
}

:deep(.el-alert__description) {
  font-size: 13px;
  margin-top: 5px;
}

/* 载荷列表样式 */
.payload-list {
  padding: 10px;
}

.payload-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding: 0 5px;
}

.payload-list-header span {
  font-weight: 500;
  color: #303133;
}
</style>
