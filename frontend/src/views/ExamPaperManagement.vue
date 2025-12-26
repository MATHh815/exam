<template>
  <div class="exam-paper-management">
    <div class="page-header">
      <h2>试卷管理</h2>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        创建试卷
      </el-button>
    </div>
    
    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filters">
        <el-form-item label="考试类型">
          <el-select v-model="filters.exam_type" placeholder="全部" clearable>
            <el-option label="公务员考试" value="civil_service" />
            <el-option label="研究生考试" value="postgraduate" />
            <el-option label="事业编考试" value="public_institution" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="发布状态">
          <el-select v-model="filters.is_published" placeholder="全部" clearable>
            <el-option label="已发布" :value="true" />
            <el-option label="未发布" :value="false" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="loadPapers">查询</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- 试卷列表 -->
    <el-card class="table-card" shadow="never">
      <el-table 
        :data="papers" 
        v-loading="loading"
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="试卷名称" min-width="200" />
        <el-table-column prop="exam_type" label="考试类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getExamTypeTagType(row.exam_type)">
              {{ getExamTypeLabel(row.exam_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="时长(分钟)" width="100" />
        <el-table-column prop="total_score" label="总分" width="80" />
        <el-table-column prop="pass_score" label="及格分" width="80" />
        <el-table-column prop="is_published" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'info'">
              {{ row.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" 
              @click="handleEdit(row)"
              link
            >
              编辑
            </el-button>
            <el-button 
              type="success" 
              size="small" 
              @click="handleManageQuestions(row)"
              link
            >
              管理题目
            </el-button>
            <el-button 
              v-if="!row.is_published"
              type="warning" 
              size="small" 
              @click="handlePublish(row)"
              link
            >
              发布
            </el-button>
            <el-button 
              type="danger" 
              size="small" 
              @click="handleDelete(row)"
              link
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadPapers"
        @current-change="loadPapers"
        class="pagination"
      />
    </el-card>
    
    <!-- 创建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="resetForm"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="试卷名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入试卷名称" />
        </el-form-item>
        
        <el-form-item label="考试类型" prop="exam_type">
          <el-select v-model="form.exam_type" placeholder="请选择考试类型">
            <el-option label="公务员考试" value="civil_service" />
            <el-option label="研究生考试" value="postgraduate" />
            <el-option label="事业编考试" value="public_institution" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="考试时长" prop="duration">
          <el-input-number 
            v-model="form.duration" 
            :min="1" 
            :max="300"
            placeholder="分钟"
          />
          <span style="margin-left: 8px; color: #909399;">分钟</span>
        </el-form-item>
        
        <el-form-item label="总分" prop="total_score">
          <el-input-number 
            v-model="form.total_score" 
            :min="1" 
            :max="1000"
          />
        </el-form-item>
        
        <el-form-item label="及格分" prop="pass_score">
          <el-input-number 
            v-model="form.pass_score" 
            :min="0" 
            :max="1000"
          />
        </el-form-item>
        
        <el-form-item label="试卷描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea"
            :rows="4"
            placeholder="请输入试卷描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 管理题目对话框 -->
    <el-dialog
      v-model="questionsDialogVisible"
      title="管理试卷题目"
      width="900px"
      @close="resetQuestionsDialog"
    >
      <div class="questions-management">
        <!-- 已添加的题目列表 -->
        <div class="added-questions">
          <h3>已添加题目 ({{ paperQuestions.length }})</h3>
          <el-table :data="paperQuestions" stripe>
            <el-table-column prop="order" label="顺序" width="80" />
            <el-table-column prop="question.content" label="题目内容" min-width="200">
              <template #default="{ row }">
                <div class="question-content-preview">
                  {{ row.question?.content || '题目内容' }}
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="question.question_type" label="类型" width="100">
              <template #default="{ row }">
                {{ getQuestionTypeLabel(row.question?.question_type) }}
              </template>
            </el-table-column>
            <el-table-column prop="score" label="分值" width="80" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="removeQuestion(row)"
                  link
                >
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 添加题目表单 -->
        <div class="add-question-form">
          <h3>添加题目</h3>
          <el-form :inline="true" :model="questionForm">
            <el-form-item label="题目ID">
              <el-input-number 
                v-model="questionForm.question_id" 
                :min="1"
                placeholder="题目ID"
              />
            </el-form-item>
            
            <el-form-item label="顺序">
              <el-input-number 
                v-model="questionForm.order" 
                :min="1"
                placeholder="顺序"
              />
            </el-form-item>
            
            <el-form-item label="分值">
              <el-input-number 
                v-model="questionForm.score" 
                :min="1"
                :max="100"
                placeholder="分值"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="addQuestion">添加</el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getExamPapers,
  createExamPaper,
  updateExamPaper,
  deleteExamPaper,
  publishExamPaper,
  addQuestionToPaper,
  getExamPaper
} from '../api/exams'

// 数据
const loading = ref(false)
const papers = ref([])
const filters = reactive({
  exam_type: '',
  is_published: null
})
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = computed(() => {
  return form.id ? '编辑试卷' : '创建试卷'
})
const submitting = ref(false)
const formRef = ref(null)
const form = reactive({
  id: null,
  name: '',
  exam_type: '',
  duration: 120,
  total_score: 100,
  pass_score: 60,
  description: ''
})

const formRules = {
  name: [
    { required: true, message: '请输入试卷名称', trigger: 'blur' }
  ],
  exam_type: [
    { required: true, message: '请选择考试类型', trigger: 'change' }
  ],
  duration: [
    { required: true, message: '请输入考试时长', trigger: 'blur' }
  ],
  total_score: [
    { required: true, message: '请输入总分', trigger: 'blur' }
  ],
  pass_score: [
    { required: true, message: '请输入及格分', trigger: 'blur' }
  ]
}

// 题目管理对话框
const questionsDialogVisible = ref(false)
const currentPaper = ref(null)
const paperQuestions = ref([])
const questionForm = reactive({
  question_id: null,
  order: 1,
  score: 5
})

/**
 * 加载试卷列表
 */
async function loadPapers() {
  try {
    loading.value = true
    
    const params = {
      ...filters,
      page: pagination.page,
      page_size: pagination.page_size
    }
    
    const response = await getExamPapers(params)
    
    if (response.success) {
      papers.value = response.data.papers
      pagination.total = response.data.total
    } else {
      throw new Error(response.error?.message || '获取试卷列表失败')
    }
  } catch (error) {
    console.error('加载试卷失败:', error)
    ElMessage.error(error.message || '加载试卷失败')
  } finally {
    loading.value = false
  }
}

/**
 * 重置筛选条件
 */
function resetFilters() {
  filters.exam_type = ''
  filters.is_published = null
  pagination.page = 1
  loadPapers()
}

/**
 * 获取考试类型标签
 */
function getExamTypeLabel(type) {
  const map = {
    'civil_service': '公务员',
    'postgraduate': '研究生',
    'public_institution': '事业编'
  }
  return map[type] || type
}

/**
 * 获取考试类型标签类型
 */
function getExamTypeTagType(type) {
  const map = {
    'civil_service': 'primary',
    'postgraduate': 'success',
    'public_institution': 'warning'
  }
  return map[type] || ''
}

/**
 * 获取题目类型标签
 */
function getQuestionTypeLabel(type) {
  const map = {
    'single_choice': '单选',
    'multiple_choice': '多选',
    'true_false': '判断',
    'fill_blank': '填空',
    'essay': '简答'
  }
  return map[type] || type
}

/**
 * 创建试卷
 */
function handleCreate() {
  resetForm()
  dialogVisible.value = true
}

/**
 * 编辑试卷
 */
function handleEdit(paper) {
  form.id = paper.id
  form.name = paper.name
  form.exam_type = paper.exam_type
  form.duration = paper.duration
  form.total_score = paper.total_score
  form.pass_score = paper.pass_score
  form.description = paper.description || ''
  dialogVisible.value = true
}

/**
 * 提交表单
 */
async function handleSubmit() {
  try {
    await formRef.value.validate()
    
    submitting.value = true
    
    const data = {
      name: form.name,
      exam_type: form.exam_type,
      duration: form.duration,
      total_score: form.total_score,
      pass_score: form.pass_score,
      description: form.description
    }
    
    let response
    if (form.id) {
      response = await updateExamPaper(form.id, data)
    } else {
      response = await createExamPaper(data)
    }
    
    if (response.success) {
      ElMessage.success(form.id ? '更新成功' : '创建成功')
      dialogVisible.value = false
      loadPapers()
    } else {
      throw new Error(response.error?.message || '操作失败')
    }
  } catch (error) {
    if (error !== false) {
      console.error('提交失败:', error)
      ElMessage.error(error.message || '操作失败')
    }
  } finally {
    submitting.value = false
  }
}

/**
 * 发布试卷
 */
async function handlePublish(paper) {
  try {
    await ElMessageBox.confirm(
      `确定要发布试卷《${paper.name}》吗？发布后用户可以参加考试。`,
      '发布确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await publishExamPaper(paper.id)
    
    if (response.success) {
      ElMessage.success('发布成功')
      loadPapers()
    } else {
      throw new Error(response.error?.message || '发布失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('发布失败:', error)
      ElMessage.error(error.message || '发布失败')
    }
  }
}

/**
 * 删除试卷
 */
async function handleDelete(paper) {
  try {
    await ElMessageBox.confirm(
      `确定要删除试卷《${paper.name}》吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await deleteExamPaper(paper.id)
    
    if (response.success) {
      ElMessage.success('删除成功')
      loadPapers()
    } else {
      throw new Error(response.error?.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error(error.message || '删除失败')
    }
  }
}

/**
 * 管理题目
 */
async function handleManageQuestions(paper) {
  currentPaper.value = paper
  
  try {
    // 获取试卷题目
    const response = await getExamPaper(paper.id, true)
    if (response.success) {
      paperQuestions.value = response.data.questions || []
    }
  } catch (error) {
    console.error('获取题目失败:', error)
  }
  
  questionsDialogVisible.value = true
}

/**
 * 添加题目到试卷
 */
async function addQuestion() {
  if (!questionForm.question_id) {
    ElMessage.warning('请输入题目ID')
    return
  }
  
  try {
    const response = await addQuestionToPaper(currentPaper.value.id, {
      question_id: questionForm.question_id,
      order: questionForm.order,
      score: questionForm.score
    })
    
    if (response.success) {
      ElMessage.success('添加成功')
      // 重新加载题目列表
      const paperResponse = await getExamPaper(currentPaper.value.id, true)
      if (paperResponse.success) {
        paperQuestions.value = paperResponse.data.questions || []
      }
      // 重置表单
      questionForm.question_id = null
      questionForm.order = paperQuestions.value.length + 1
    } else {
      throw new Error(response.error?.message || '添加失败')
    }
  } catch (error) {
    console.error('添加题目失败:', error)
    ElMessage.error(error.message || '添加题目失败')
  }
}

/**
 * 移除题目
 */
function removeQuestion(paperQuestion) {
  ElMessage.info('移除题目功能需要后端支持，暂未实现')
}

/**
 * 重置表单
 */
function resetForm() {
  form.id = null
  form.name = ''
  form.exam_type = ''
  form.duration = 120
  form.total_score = 100
  form.pass_score = 60
  form.description = ''
  
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

/**
 * 重置题目对话框
 */
function resetQuestionsDialog() {
  currentPaper.value = null
  paperQuestions.value = []
  questionForm.question_id = null
  questionForm.order = 1
  questionForm.score = 5
}

onMounted(() => {
  loadPapers()
})
</script>

<style scoped>
.exam-paper-management {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.filter-card,
.table-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.questions-management {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.added-questions h3,
.add-question-form h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.question-content-preview {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.add-question-form {
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
