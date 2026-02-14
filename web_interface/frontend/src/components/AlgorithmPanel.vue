<template>
  <div class="algorithm-panel">
    <el-form :model="config" label-width="150px">
      <el-form-item label="选择算法">
        <el-select v-model="config.algorithmId" style="width: 100%" @change="handleAlgorithmChange">
          <el-option
            v-for="algo in algorithms"
            :key="algo.id"
            :label="algo.name"
            :value="algo.id"
          >
            <span>{{ algo.name }}</span>
            <span class="algorithm-description">{{ algo.description }}</span>
          </el-option>
        </el-select>
      </el-form-item>

      <el-divider>算法参数</el-divider>

      <template v-if="selectedAlgorithm">
        <!-- Genetic Algorithm Parameters -->
        <template v-if="selectedAlgorithm.type === 'genetic'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="种群大小">
                <el-input-number v-model="config.parameters.population_size" :min="10" :max="500" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="最大迭代次数">
                <el-input-number v-model="config.parameters.max_generations" :min="10" :max="2000" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="交叉概率">
                <el-slider v-model="config.parameters.crossover_rate" :min="0" :max="1" :step="0.01" show-input />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="变异概率">
                <el-slider v-model="config.parameters.mutation_rate" :min="0" :max="1" :step="0.01" show-input />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="选择策略">
            <el-select v-model="config.parameters.selection_strategy" style="width: 100%">
              <el-option label="轮盘赌选择" value="roulette" />
              <el-option label="锦标赛选择" value="tournament" />
              <el-option label="排序选择" value="rank" />
            </el-select>
          </el-form-item>
        </template>

        <!-- Tabu Search Parameters -->
        <template v-if="selectedAlgorithm.type === 'tabu'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="最大迭代次数">
                <el-input-number v-model="config.parameters.max_iterations" :min="10" :max="5000" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="禁忌表长度">
                <el-input-number v-model="config.parameters.tabu_list_size" :min="5" :max="200" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="邻域大小">
                <el-input-number v-model="config.parameters.neighborhood_size" :min="5" :max="100" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="早熟收敛阈值">
                <el-input-number v-model="config.parameters.early_stop_threshold" :min="10" :max="500" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <!-- Simulated Annealing Parameters -->
        <template v-if="selectedAlgorithm.type === 'sa'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="初始温度">
                <el-input-number v-model="config.parameters.initial_temperature" :min="1" :max="10000" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="冷却率">
                <el-slider v-model="config.parameters.cooling_rate" :min="0.9" :max="0.999" :step="0.001" show-input />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="终止温度">
                <el-input-number v-model="config.parameters.final_temperature" :min="0.0001" :max="1" :precision="4" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="每个温度迭代次数">
                <el-input-number v-model="config.parameters.iterations_per_temp" :min="1" :max="1000" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <!-- Ant Colony Optimization Parameters -->
        <template v-if="selectedAlgorithm.type === 'aco'">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="蚂蚁数量">
                <el-input-number v-model="config.parameters.num_ants" :min="5" :max="200" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="最大迭代次数">
                <el-input-number v-model="config.parameters.max_iterations" :min="10" :max="2000" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="信息素重要性">
                <el-slider v-model="config.parameters.alpha" :min="0" :max="5" :step="0.1" show-input />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="启发式重要性">
                <el-slider v-model="config.parameters.beta" :min="0" :max="5" :step="0.1" show-input />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="信息素蒸发率">
            <el-slider v-model="config.parameters.evaporation_rate" :min="0" :max="1" :step="0.01" show-input />
          </el-form-item>
        </template>
      </template>

      <el-divider>通用参数</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="随机种子">
            <el-input-number v-model="config.parameters.random_seed" :min="0" :max="999999" style="width: 100%" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="超时时间(秒)">
            <el-input-number v-model="config.parameters.timeout" :min="10" :max="3600" style="width: 100%" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="优化目标">
        <el-checkbox-group v-model="config.objectives">
          <el-checkbox label="completion_rate">任务完成率</el-checkbox>
          <el-checkbox label="total_value">总收益</el-checkbox>
          <el-checkbox label="resource_utilization">资源利用率</el-checkbox>
          <el-checkbox label="fairness">公平性</el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleStart" :loading="isRunning">
          {{ isRunning ? '运行中...' : '开始规划' }}
        </el-button>
        <el-button @click="handleReset">重置参数</el-button>
        <el-button @click="handleLoadPreset">加载预设</el-button>
      </el-form-item>
    </el-form>

    <!-- Algorithm Info Card -->
    <el-card v-if="selectedAlgorithm" class="info-card">
      <template #header>
        <span>算法说明</span>
      </template>
      <p>{{ selectedAlgorithm.description }}</p>
      <el-divider />
      <h4>适用场景</h4>
      <ul>
        <li v-for="scenario in selectedAlgorithm.suitableScenarios" :key="scenario">
          {{ scenario }}
        </li>
      </ul>
      <h4>优缺点</h4>
      <el-row :gutter="20">
        <el-col :span="12">
          <h5>优点</h5>
          <ul>
            <li v-for="pro in selectedAlgorithm.pros" :key="pro">{{ pro }}</li>
          </ul>
        </el-col>
        <el-col :span="12">
          <h5>缺点</h5>
          <ul>
            <li v-for="con in selectedAlgorithm.cons" :key="con">{{ con }}</li>
          </ul>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

const props = defineProps({
  algorithms: {
    type: Array,
    default: () => [
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
    ]
  },
  isRunning: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['start', 'reset', 'load-preset'])

const config = reactive({
  algorithmId: 'ga',
  parameters: {
    // GA defaults
    population_size: 50,
    max_generations: 500,
    crossover_rate: 0.8,
    mutation_rate: 0.1,
    selection_strategy: 'tournament',
    // Tabu defaults
    max_iterations: 1000,
    tabu_list_size: 50,
    neighborhood_size: 20,
    early_stop_threshold: 100,
    // SA defaults
    initial_temperature: 1000,
    cooling_rate: 0.95,
    final_temperature: 0.001,
    iterations_per_temp: 100,
    // ACO defaults
    num_ants: 30,
    alpha: 1,
    beta: 2,
    evaporation_rate: 0.5,
    // Common
    random_seed: 42,
    timeout: 600
  },
  objectives: ['completion_rate', 'total_value']
})

const selectedAlgorithm = computed(() => {
  return props.algorithms.find(a => a.id === config.algorithmId)
})

function handleAlgorithmChange() {
  // Reset parameters to defaults for selected algorithm
  const defaults = getDefaultParameters(selectedAlgorithm.value?.type)
  config.parameters = { ...config.parameters, ...defaults }
}

function getDefaultParameters(type) {
  const defaults = {
    genetic: {
      population_size: 50,
      max_generations: 500,
      crossover_rate: 0.8,
      mutation_rate: 0.1,
      selection_strategy: 'tournament'
    },
    tabu: {
      max_iterations: 1000,
      tabu_list_size: 50,
      neighborhood_size: 20,
      early_stop_threshold: 100
    },
    sa: {
      initial_temperature: 1000,
      cooling_rate: 0.95,
      final_temperature: 0.001,
      iterations_per_temp: 100
    },
    aco: {
      num_ants: 30,
      max_iterations: 500,
      alpha: 1,
      beta: 2,
      evaporation_rate: 0.5
    }
  }
  return defaults[type] || {}
}

function handleStart() {
  emit('start', {
    algorithmId: config.algorithmId,
    parameters: config.parameters,
    objectives: config.objectives
  })
}

function handleReset() {
  handleAlgorithmChange()
  config.objectives = ['completion_rate', 'total_value']
  emit('reset')
}

function handleLoadPreset() {
  emit('load-preset')
}
</script>

<style scoped>
.algorithm-panel {
  padding: 20px;
}

.algorithm-description {
  float: right;
  color: #8492a6;
  font-size: 13px;
}

.info-card {
  margin-top: 20px;
}

.info-card h4 {
  margin: 15px 0 10px;
  color: #303133;
}

.info-card h5 {
  margin: 10px 0 5px;
  color: #606266;
}

.info-card ul {
  margin: 5px 0;
  padding-left: 20px;
}

.info-card li {
  margin: 3px 0;
  color: #606266;
}
</style>
