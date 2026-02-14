<template>
  <div class="target-manager">
    <el-row :gutter="20" class="toolbar">
      <el-col :span="8">
        <el-input
          v-model="searchQuery"
          placeholder="搜索目标..."
          clearable
          prefix-icon="Search"
        />
      </el-col>
      <el-col :span="16" class="text-right">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>添加目标
        </el-button>
        <el-button @click="handleImport">
          <el-icon><Upload /></el-icon>导入
        </el-button>
        <el-button @click="handleExport">
          <el-icon><Download /></el-icon>导出
        </el-button>
        <el-button type="danger" @click="handleBatchDelete" :disabled="!selectedTargets.length">
          <el-icon><Delete /></el-icon>删除选中
        </el-button>
      </el-col>
    </el-row>

    <el-table
      :data="filteredTargets"
      style="width: 100%"
      @selection-change="handleSelectionChange"
      v-loading="loading"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="name" label="目标名称" sortable />
      <el-table-column prop="target_type" label="类型" width="100">
        <template #default="{ row }">
          <el-tag :type="getTargetTypeTag(row.target_type)">
            {{ formatTargetType(row.target_type) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="latitude" label="纬度" width="120">
        <template #default="{ row }">
          {{ formatLatitude(row.latitude) }}
        </template>
      </el-table-column>
      <el-table-column prop="longitude" label="经度" width="120">
        <template #default="{ row }">
          {{ formatLongitude(row.longitude) }}
        </template>
      </el-table-column>
      <el-table-column prop="priority" label="优先级" width="100" sortable>
        <template #default="{ row }">
          <el-tag :type="getPriorityType(row.priority)">
            {{ row.priority }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :total="total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      class="pagination"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
    />

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑目标' : '添加目标'"
      width="500px"
    >
      <el-form :model="form" label-width="100px" :rules="formRules" ref="formRef">
        <el-form-item label="目标名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="目标类型" prop="target_type">
          <el-select v-model="form.target_type" style="width: 100%">
            <el-option label="点目标" value="POINT" />
            <el-option label="区域目标" value="AREA" />
            <el-option label="移动目标" value="MOVING" />
            <el-option label="网格目标" value="GRID" />
          </el-select>
        </el-form-item>
        <el-form-item label="纬度" prop="latitude">
          <el-input-number v-model="form.latitude" :min="-90" :max="90" :precision="6" style="width: 100%" />
        </el-form-item>
        <el-form-item label="经度" prop="longitude">
          <el-input-number v-model="form.longitude" :min="-180" :max="180" :precision="6" style="width: 100%" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-rate v-model="form.priority" :max="5" show-score />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- Import Dialog -->
    <el-dialog v-model="importDialogVisible" title="导入目标" width="400px">
      <el-upload
        drag
        action="/api/targets/import"
        :on-success="handleImportSuccess"
        :on-error="handleImportError"
        accept=".geojson,.json,.csv,.kml"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽文件到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 GeoJSON, JSON, CSV, KML 格式
          </div>
        </template>
      </el-upload>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formatLatitude, formatLongitude, formatTargetType } from '@/utils/formatters'

const props = defineProps({
  targets: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['add', 'edit', 'delete', 'batch-delete', 'import', 'export'])

const searchQuery = ref('')
const selectedTargets = ref([])
const currentPage = ref(1)
const pageSize = ref(20)
const dialogVisible = ref(false)
const importDialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const form = ref({
  name: '',
  target_type: 'POINT',
  latitude: 0,
  longitude: 0,
  priority: 3,
  description: ''
})

const formRules = {
  name: [{ required: true, message: '请输入目标名称', trigger: 'blur' }],
  target_type: [{ required: true, message: '请选择目标类型', trigger: 'change' }],
  latitude: [{ required: true, message: '请输入纬度', trigger: 'blur' }],
  longitude: [{ required: true, message: '请输入经度', trigger: 'blur' }],
  priority: [{ required: true, message: '请设置优先级', trigger: 'change' }]
}

const filteredTargets = computed(() => {
  let result = props.targets
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(t =>
      t.name?.toLowerCase().includes(query) ||
      t.description?.toLowerCase().includes(query)
    )
  }
  return result
})

const total = computed(() => filteredTargets.value.length)

function getTargetTypeTag(type) {
  const tags = {
    'POINT': '',
    'AREA': 'success',
    'MOVING': 'warning',
    'GRID': 'info'
  }
  return tags[type] || ''
}

function getPriorityType(priority) {
  const types = {
    1: 'info',
    2: 'success',
    3: 'warning',
    4: 'danger',
    5: 'danger'
  }
  return types[priority] || 'info'
}

function handleSelectionChange(selection) {
  selectedTargets.value = selection
}

function handleAdd() {
  isEdit.value = false
  form.value = {
    name: '',
    target_type: 'POINT',
    latitude: 0,
    longitude: 0,
    priority: 3,
    description: ''
  }
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (valid) {
      if (isEdit.value) {
        emit('edit', form.value)
      } else {
        emit('add', form.value)
      }
      dialogVisible.value = false
    }
  })
}

function handleDelete(row) {
  ElMessageBox.confirm(
    `确定要删除目标 "${row.name}" 吗？`,
    '确认删除',
    { type: 'warning' }
  ).then(() => {
    emit('delete', row.id)
  })
}

function handleBatchDelete() {
  const ids = selectedTargets.value.map(t => t.id)
  ElMessageBox.confirm(
    `确定要删除选中的 ${ids.length} 个目标吗？`,
    '确认删除',
    { type: 'warning' }
  ).then(() => {
    emit('batch-delete', ids)
    selectedTargets.value = []
  })
}

function handleImport() {
  importDialogVisible.value = true
}

function handleImportSuccess(response) {
  ElMessage.success('导入成功')
  emit('import', response)
  importDialogVisible.value = false
}

function handleImportError(error) {
  ElMessage.error('导入失败: ' + error.message)
}

function handleExport() {
  emit('export')
}

function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
}

function handlePageChange(val) {
  currentPage.value = val
}
</script>

<style scoped>
.target-manager {
  padding: 20px;
}

.toolbar {
  margin-bottom: 20px;
}

.text-right {
  text-align: right;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
