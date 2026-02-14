<template>
  <div class="satellite-editor">
    <el-form :model="form" label-width="120px" :rules="rules" ref="formRef">
      <el-form-item label="卫星名称" prop="name">
        <el-input v-model="form.name" placeholder="输入卫星名称" />
      </el-form-item>

      <el-form-item label="卫星型号" prop="satellite_type">
        <el-select v-model="form.satellite_type" placeholder="选择卫星型号" style="width: 100%">
          <el-option label="光学-高分辨率" value="optical_high" />
          <el-option label="光学-超高分辨率" value="optical_uhr" />
          <el-option label="SAR-高分辨率" value="sar_high" />
          <el-option label="SAR-超高分辨率" value="sar_uhr" />
        </el-select>
      </el-form-item>

      <el-form-item label="轨道类型" prop="orbit_type">
        <el-select v-model="form.orbit_type" placeholder="选择轨道类型" style="width: 100%">
          <el-option label="LEO" value="LEO" />
          <el-option label="SSO" value="SSO" />
          <el-option label="MEO" value="MEO" />
          <el-option label="GEO" value="GEO" />
        </el-select>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="轨道高度(km)" prop="altitude">
            <el-input-number v-model="form.altitude" :min="200" :max="36000" :precision="2" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="倾角(°)" prop="inclination">
            <el-input-number v-model="form.inclination" :min="0" :max="180" :precision="4" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="升交点赤经(°)" prop="raan">
            <el-input-number v-model="form.raan" :min="0" :max="360" :precision="4" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="近地点幅角(°)" prop="arg_perigee">
            <el-input-number v-model="form.arg_perigee" :min="0" :max="360" :precision="4" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="偏心率" prop="eccentricity">
            <el-input-number v-model="form.eccentricity" :min="0" :max="0.99" :precision="6" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="平近点角(°)" prop="mean_anomaly">
            <el-input-number v-model="form.mean_anomaly" :min="0" :max="360" :precision="4" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider>传感器配置</el-divider>

      <el-form-item label="传感器类型" prop="sensor_type">
        <el-select v-model="form.sensor_type" placeholder="选择传感器类型" style="width: 100%">
          <el-option label="光学相机" value="OPTICAL" />
          <el-option label="SAR" value="SAR" />
          <el-option label="红外" value="INFRARED" />
          <el-option label="多光谱" value="MULTISPECTRAL" />
        </el-select>
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="分辨率(m)" prop="resolution">
            <el-input-number v-model="form.resolution" :min="0.1" :max="100" :precision="2" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="视场角(°)" prop="fov">
            <el-input-number v-model="form.fov" :min="1" :max="60" :precision="2" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item>
        <el-button type="primary" @click="handleSubmit">保存</el-button>
        <el-button @click="handleReset">重置</el-button>
        <el-button v-if="satellite" type="danger" @click="handleDelete">删除</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  satellite: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['save', 'delete', 'reset'])

const formRef = ref(null)

const form = ref({
  name: '',
  satellite_type: '',
  orbit_type: 'SSO',
  altitude: 500,
  inclination: 97.4,
  raan: 0,
  arg_perigee: 0,
  eccentricity: 0,
  mean_anomaly: 0,
  sensor_type: 'OPTICAL',
  resolution: 2,
  fov: 15
})

const rules = {
  name: [{ required: true, message: '请输入卫星名称', trigger: 'blur' }],
  satellite_type: [{ required: true, message: '请选择卫星型号', trigger: 'change' }],
  orbit_type: [{ required: true, message: '请选择轨道类型', trigger: 'change' }],
  altitude: [{ required: true, message: '请输入轨道高度', trigger: 'blur' }],
  inclination: [{ required: true, message: '请输入倾角', trigger: 'blur' }]
}

// Watch for satellite prop changes
watch(() => props.satellite, (newSat) => {
  if (newSat) {
    form.value = { ...form.value, ...newSat }
  } else {
    handleReset()
  }
}, { immediate: true })

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (valid) {
      emit('save', { ...form.value })
    }
  })
}

function handleReset() {
  form.value = {
    name: '',
    satellite_type: '',
    orbit_type: 'SSO',
    altitude: 500,
    inclination: 97.4,
    raan: 0,
    arg_perigee: 0,
    eccentricity: 0,
    mean_anomaly: 0,
    sensor_type: 'OPTICAL',
    resolution: 2,
    fov: 15
  }
  formRef.value?.resetFields()
  emit('reset')
}

function handleDelete() {
  emit('delete', props.satellite?.id)
}
</script>

<style scoped>
.satellite-editor {
  padding: 20px;
}
</style>
