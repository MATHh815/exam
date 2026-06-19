<template>
  <div class="study-plans-page">
    <div class="page-header">
      <div class="header-left">
        <h2>学习计划</h2>
        <p class="subtitle">制定学习计划，追踪学习进度</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        创建计划
      </el-button>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="study-tabs">
      <el-tab-pane name="active">
        <template #label>
          <span class="tab-label">
            <el-icon><Clock /></el-icon>
            进行中
          </span>
        </template>
        <div v-loading="loading" class="plans-container">
          <el-empty v-if="!loading && activePlans.length === 0" description="暂无进行中的计划" />
          <StudyPlanCard
            v-for="plan in activePlans"
            :key="plan.id"
            :plan="plan"
            @view="handleViewPlan"
            @edit="handleEditPlan"
            @delete="handleDeletePlan"
            @view-report="handleViewReport"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane name="completed">
        <template #label>
          <span class="tab-label">
            <el-icon><CircleCheck /></el-icon>
            已完成
          </span>
        </template>
        <div v-loading="loading" class="plans-container">
          <el-empty v-if="!loading && completedPlans.length === 0" description="暂无已完成的计划" />
          <StudyPlanCard
            v-for="plan in completedPlans"
            :key="plan.id"
            :plan="plan"
            @view="handleViewPlan"
            @edit="handleEditPlan"
            @delete="handleDeletePlan"
            @view-report="handleViewReport"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 创建/编辑计划对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingPlan ? '编辑计划' : '创建计划'"
      width="600px"
      :close-on-click-modal="false"
    >
      <StudyPlanForm
        :plan="editingPlan"
        :loading="submitting"
        @submit="handleSubmit"
        @cancel="handleCancelEdit"
      />
    </el-dialog>

    <!-- 查看计划详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="计划详情"
      width="700px"
    >
      <div v-if="selectedPlan" class="plan-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="计划名称">{{ selectedPlan.name }}</el-descriptions-item>
          <el-descriptions-item label="考试类型">{{ selectedPlan.exam_type }}</el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ formatDate(selectedPlan.start_date) }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ formatDate(selectedPlan.end_date) }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="selectedPlan.is_active ? 'success' : 'info'">
              {{ selectedPlan.is_active ? '进行中' : '已完成' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDate(selectedPlan.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="计划描述" :span="2">
            {{ selectedPlan.description || '无' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">学习目标</el-divider>
        <div class="goals-detail">
          <el-card v-for="goal in selectedPlan.goals" :key="goal.id" class="goal-card">
            <div class="goal-info">
              <div class="goal-name">{{ getGoalTypeLabel(goal.goal_type) }}</div>
              <div class="goal-progress-text">
                {{ goal.current_value }} / {{ goal.target_value }}
                <el-tag v-if="goal.is_completed" type="success" size="small" style="margin-left: 8px">
                  已完成
                </el-tag>
              </div>
            </div>
            <el-progress 
              :percentage="getGoalProgress(goal)" 
              :status="goal.is_completed ? 'success' : ''"
            />
          </el-card>
        </div>
      </div>
    </el-dialog>

    <!-- 学习报告对话框 -->
    <el-dialog
      v-model="showReportDialog"
      title="学习报告"
      width="800px"
    >
      <div v-if="reportData" v-loading="loadingReport" class="report-content">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-statistic title="总练习题数" :value="reportData.total_practice_count" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="总考试次数" :value="reportData.total_exam_count" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="总学习时长" :value="reportData.total_study_duration" suffix="分钟" />
          </el-col>
        </el-row>

        <el-divider />

        <div class="goal-reports">
          <h3>目标完成情况</h3>
          <el-card v-for="goal in reportData.goals" :key="goal.id" class="goal-report-card">
            <div class="goal-report-header">
              <span class="goal-type">{{ getGoalTypeLabel(goal.goal_type) }}</span>
              <el-tag :type="goal.is_completed ? 'success' : 'warning'">
                {{ goal.is_completed ? '已完成' : '进行中' }}
              </el-tag>
            </div>
            <el-progress 
              :percentage="getGoalProgress(goal)" 
              :status="goal.is_completed ? 'success' : ''"
            />
            <div class="goal-stats">
              <span>当前进度：{{ goal.current_value }} / {{ goal.target_value }}</span>
              <span>完成率：{{ getGoalProgress(goal) }}%</span>
            </div>
          </el-card>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Clock, CircleCheck } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import StudyPlanCard from '../components/StudyPlanCard.vue'
import StudyPlanForm from '../components/StudyPlanForm.vue'
import { 
  getStudyPlans, 
  createStudyPlan, 
  updateStudyPlan, 
  deleteStudyPlan,
  getStudyReport 
} from '../api/studyPlans'

const loading = ref(false)
const submitting = ref(false)
const loadingReport = ref(false)
const activeTab = ref('active')
const plans = ref([])
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showReportDialog = ref(false)
const editingPlan = ref(null)
const selectedPlan = ref(null)
const reportData = ref(null)

const activePlans = computed(() => plans.value.filter(p => p.is_active))
const completedPlans = computed(() => plans.value.filter(p => !p.is_active))

const fetchPlans = async () => {
  loading.value = true
  try {
    const res = await getStudyPlans()
    console.log('获取到的学习计划数据:', res)
    plans.value = res.data?.plans || []
  } catch (error) {
    console.error('获取学习计划失败:', error)
    ElMessage.error('获取学习计划失败')
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  // Tab切换时可以添加额外逻辑
}

const handleSubmit = async (formData) => {
  submitting.value = true
  try {
    if (editingPlan.value) {
      await updateStudyPlan(editingPlan.value.id, formData)
      ElMessage.success('更新计划成功')
    } else {
      await createStudyPlan(formData)
      ElMessage.success('创建计划成功')
    }
    showCreateDialog.value = false
    editingPlan.value = null
    fetchPlans()
  } catch (error) {
    ElMessage.error(editingPlan.value ? '更新计划失败' : '创建计划失败')
  } finally {
    submitting.value = false
  }
}

const handleCancelEdit = () => {
  showCreateDialog.value = false
  editingPlan.value = null
}

const handleViewPlan = (plan) => {
  selectedPlan.value = plan
  showDetailDialog.value = true
}

const handleEditPlan = (plan) => {
  editingPlan.value = plan
  showCreateDialog.value = true
}

const handleDeletePlan = async (plan) => {
  try {
    await ElMessageBox.confirm('确定要删除这个学习计划吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteStudyPlan(plan.id)
    ElMessage.success('删除成功')
    fetchPlans()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleViewReport = async (plan) => {
  selectedPlan.value = plan
  showReportDialog.value = true
  loadingReport.value = true
  
  try {
    const res = await getStudyReport(plan.id)
    reportData.value = res
  } catch (error) {
    ElMessage.error('获取学习报告失败')
  } finally {
    loadingReport.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const getGoalTypeLabel = (type) => {
  const labels = {
    'daily_practice': '每日练习',
    'weekly_practice': '每周练习',
    'daily_duration': '每日学习时长',
    'exam_count': '考试次数'
  }
  return labels[type] || type
}

const getGoalProgress = (goal) => {
  if (goal.target_value === 0) return 0
  return Math.min(100, Math.round((goal.current_value / goal.target_value) * 100))
}

onMounted(() => {
  fetchPlans()
})
</script>

<style scoped>
.study-plans-page {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: var(--el-text-color-primary);
}

.subtitle {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.study-tabs {
  margin-top: 8px;
}

.study-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.6);
}

.study-tabs :deep(.el-tabs__item.is-active) {
  color: #fff;
}

.study-tabs :deep(.el-tabs__item:hover) {
  color: rgba(255, 255, 255, 0.9);
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 6px;
}

.plans-container {
  min-height: 400px;
  margin-top: 20px;
}

.plan-detail {
  padding: 12px 0;
}

.goals-detail {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.goal-card {
  padding: 12px;
}

.goal-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.goal-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.goal-progress-text {
  color: var(--el-text-color-secondary);
}

.report-content {
  padding: 12px 0;
}

.goal-reports {
  margin-top: 20px;
}

.goal-reports h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
}

.goal-report-card {
  margin-bottom: 12px;
}

.goal-report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.goal-type {
  font-weight: 600;
}

.goal-stats {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
