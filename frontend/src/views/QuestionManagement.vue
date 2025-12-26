<template>
  <div class="question-management">
    <el-card class="header-card">
      <div class="page-header">
        <div class="header-left">
          <h2>题库管理</h2>
          <el-tag type="info">共 {{ total }} 道题目</el-tag>
        </div>
        <div class="header-right">
          <el-button type="primary" @click="showCreateDialog">
            <el-icon><Plus /></el-icon>
            新建题目
          </el-button>
          <el-button type="success" @click="showImportDialog">
            <el-icon><Upload /></el-icon>
            批量导入
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 筛选条件 -->
    <el-card class="filter-card">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="考试类型">
          <el-select v-model="filters.exam_type" placeholder="全部" clearable @change="handleFilter">
            <el-option label="公务员考试" value="civil_service" />
            <el-option label="研究生考试" value="postgraduate" />
            <el-option label="事业编考试" value="public_institution" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="题目类型">
          <el-select v-model="filters.question_type" placeholder="全部" clearable @change="handleFilter">
            <el-option label="单选题" value="single_choice" />
            <el-option label="多选题" value="multiple_choice" />
            <el-option label="判断题" value="true_false" />
            <el-option label="填空题" value="fill_blank" />
            <el-option label="简答题" value="essay" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="科目">
          <el-input v-model="filters.subject" placeholder="请输入科目" clearable @change="handleFilter" />
        </el-form-item>
        
        <el-form-item label="难度">
          <el-select v-model="filters.difficulty" placeholder="全部" clearable @change="handleFilter">
            <el-option label="★" :value="1" />
            <el-option label="★★" :value="2" />
            <el-option label="★★★" :value="3" />
            <el-option label="★★★★" :value="4" />
            <el-option label="★★★★★" :value="5" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="关键词">
          <el-input v-model="filters.keyword" placeholder="搜索题目内容" clearable>
            <template #append>
              <el-button :icon="Search" @click="handleFilter" />
            </template>
          </el-input>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 题目列表 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="questions"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        
        <el-table-column label="题目类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getQuestionTypeColor(row.question_type)" size="small">
              {{ getQuestionTypeLabel(row.question_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column label="考试类型" width="120">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              {{ getExamTypeLabel(row.exam_type) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="subject" label="科目" width="100" />
        
        <el-table-column label="题目内容" min-width="300">
          <template #default="{ row }">
            <div class="question-content-preview">
              {{ truncateText(row.content, 100) }}
            </div>
          </template>
        </el-table-column>
        
        <el-table-column label="难度" width="120">
          <template #default="{ row }">
            <el-rate
              v-model="row.difficulty"
              disabled
              show-score
              text-color="#ff9900"
            />
          </template>
        </el-table-column>
        
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button type="warning" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑题目对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新建题目' : '编辑题目'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="questionFormRef"
        :model="questionForm"
        :rules="questionRules"
        label-width="100px"
      >
        <el-form-item label="考试类型" prop="exam_type">
          <el-select v-model="questionForm.exam_type" placeholder="请选择考试类型">
            <el-option label="公务员考试" value="civil_service" />
            <el-option label="研究生考试" value="postgraduate" />
            <el-option label="事业编考试" value="public_institution" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="题目类型" prop="question_type">
          <el-select v-model="questionForm.question_type" placeholder="请选择题目类型">
            <el-option label="单选题" value="single_choice" />
            <el-option label="多选题" value="multiple_choice" />
            <el-option label="判断题" value="true_false" />
            <el-option label="填空题" value="fill_blank" />
            <el-option label="简答题" value="essay" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="科目" prop="subject">
          <el-input v-model="questionForm.subject" placeholder="请输入科目" />
        </el-form-item>
        
        <el-form-item label="章节">
          <el-input v-model="questionForm.chapter" placeholder="请输入章节" />
        </el-form-item>
        
        <el-form-item label="难度" prop="difficulty">
          <el-rate v-model="questionForm.difficulty" show-text />
        </el-form-item>
        
        <el-form-item label="题目内容" prop="content">
          <el-input
            v-model="questionForm.content"
            type="textarea"
            :rows="4"
            placeholder="请输入题目内容"
          />
        </el-form-item>
        
        <el-form-item
          v-if="isChoiceQuestion"
          label="选项"
          prop="options"
        >
          <div class="options-input">
            <div
              v-for="(option, index) in questionForm.options"
              :key="index"
              class="option-item"
            >
              <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
              <el-input
                v-model="questionForm.options[index]"
                placeholder="请输入选项内容"
              />
              <el-button
                v-if="questionForm.options.length > 2"
                type="danger"
                :icon="Delete"
                circle
                @click="removeOption(index)"
              />
            </div>
            <el-button type="primary" text @click="addOption">
              <el-icon><Plus /></el-icon>
              添加选项
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="正确答案" prop="correct_answer">
          <el-input
            v-if="!isChoiceQuestion"
            v-model="questionForm.correct_answer"
            placeholder="请输入正确答案"
          />
          <el-select
            v-else-if="questionForm.question_type === 'single_choice' || questionForm.question_type === 'true_false'"
            v-model="questionForm.correct_answer"
            placeholder="请选择正确答案"
          >
            <el-option
              v-for="(option, index) in questionForm.options"
              :key="index"
              :label="`${String.fromCharCode(65 + index)}. ${option}`"
              :value="String.fromCharCode(65 + index)"
            />
          </el-select>
          <el-select
            v-else-if="questionForm.question_type === 'multiple_choice'"
            v-model="questionForm.correct_answer"
            multiple
            placeholder="请选择正确答案（可多选）"
          >
            <el-option
              v-for="(option, index) in questionForm.options"
              :key="index"
              :label="`${String.fromCharCode(65 + index)}. ${option}`"
              :value="String.fromCharCode(65 + index)"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="题目解析">
          <el-input
            v-model="questionForm.explanation"
            type="textarea"
            :rows="4"
            placeholder="请输入题目解析"
          />
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select
            v-model="questionForm.tags"
            multiple
            filterable
            allow-create
            placeholder="请输入标签"
          >
            <el-option
              v-for="tag in commonTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 批量导入对话框 -->
    <el-dialog
      v-model="importDialogVisible"
      title="批量导入题目"
      width="600px"
    >
      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p>请上传 JSON 格式的题目文件，格式示例：</p>
        <pre style="margin-top: 10px; background: #f5f7fa; padding: 10px; border-radius: 4px;">
{
  "questions": [
    {
      "exam_type": "civil_service",
      "question_type": "single_choice",
      "subject": "行测",
      "content": "题目内容",
      "options": ["选项A", "选项B", "选项C", "选项D"],
      "correct_answer": "A",
      "explanation": "解析内容",
      "difficulty": 3
    }
  ]
}</pre>
      </el-alert>
      
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :limit="1"
        accept=".json"
        :on-change="handleFileChange"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            只能上传 JSON 文件
          </div>
        </template>
      </el-upload>
      
      <template #footer>
        <el-button @click="importDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImport" :loading="importing">
          开始导入
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看题目对话框 -->
    <el-dialog
      v-model="viewDialogVisible"
      title="题目详情"
      width="800px"
    >
      <QuestionCard
        v-if="currentQuestion"
        :question="currentQuestion"
        :show-explanation="true"
        :show-correct-answer="true"
        :disabled="true"
      />
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Search, Delete, UploadFilled } from '@element-plus/icons-vue'
import {
  getQuestions,
  createQuestion,
  updateQuestion,
  deleteQuestion,
  importQuestions
} from '../api/questions'
import QuestionCard from '../components/QuestionCard.vue'

// 数据状态
const loading = ref(false)
const questions = ref([])
const total = ref(0)

// 分页
const pagination = reactive({
  page: 1,
  page_size: 20
})

// 筛选条件
const filters = reactive({
  exam_type: '',
  question_type: '',
  subject: '',
  difficulty: null,
  keyword: ''
})

// 对话框状态
const dialogVisible = ref(false)
const dialogMode = ref('create') // 'create' | 'edit'
const submitting = ref(false)

// 导入对话框
const importDialogVisible = ref(false)
const importing = ref(false)
const uploadFile = ref(null)

// 查看对话框
const viewDialogVisible = ref(false)
const currentQuestion = ref(null)

// 表单
const questionFormRef = ref(null)
const questionForm = reactive({
  exam_type: '',
  question_type: '',
  subject: '',
  chapter: '',
  difficulty: 3,
  content: '',
  options: ['', '', '', ''],
  correct_answer: '',
  explanation: '',
  tags: []
})

// 表单验证规则
const questionRules = {
  exam_type: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
  question_type: [{ required: true, message: '请选择题目类型', trigger: 'change' }],
  subject: [{ required: true, message: '请输入科目', trigger: 'blur' }],
  difficulty: [{ required: true, message: '请选择难度', trigger: 'change' }],
  content: [{ required: true, message: '请输入题目内容', trigger: 'blur' }],
  correct_answer: [{ required: true, message: '请输入正确答案', trigger: 'blur' }]
}

// 常用标签
const commonTags = ['重点', '易错', '高频', '基础', '提高']

// 是否为选择题
const isChoiceQuestion = computed(() => {
  return ['single_choice', 'multiple_choice', 'true_false'].includes(questionForm.question_type)
})

// 加载题目列表
const loadQuestions = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...filters
    }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })
    
    const response = await getQuestions(params)
    if (response.success) {
      questions.value = response.data.questions
      total.value = response.data.total
    }
  } catch (error) {
    ElMessage.error('加载题目列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 筛选处理
const handleFilter = () => {
  pagination.page = 1
  loadQuestions()
}

// 分页处理
const handlePageChange = (page) => {
  pagination.page = page
  loadQuestions()
}

const handleSizeChange = (size) => {
  pagination.page_size = size
  pagination.page = 1
  loadQuestions()
}

// 显示创建对话框
const showCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

// 显示编辑对话框
const handleEdit = (row) => {
  dialogMode.value = 'edit'
  Object.assign(questionForm, {
    id: row.id,
    exam_type: row.exam_type,
    question_type: row.question_type,
    subject: row.subject,
    chapter: row.chapter || '',
    difficulty: row.difficulty,
    content: row.content,
    options: row.options || ['', '', '', ''],
    correct_answer: row.correct_answer,
    explanation: row.explanation || '',
    tags: row.tags || []
  })
  dialogVisible.value = true
}

// 查看题目
const handleView = (row) => {
  currentQuestion.value = row
  viewDialogVisible.value = true
}

// 删除题目
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这道题目吗？删除后可以在回收站中恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await deleteQuestion(row.id)
    if (response.success) {
      ElMessage.success('删除成功')
      loadQuestions()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error(error)
    }
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!questionFormRef.value) return
  
  await questionFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      const data = { ...questionForm }
      
      // 处理选项数据
      if (isChoiceQuestion.value) {
        data.options = data.options.filter(opt => opt.trim() !== '')
      } else {
        delete data.options
      }
      
      let response
      if (dialogMode.value === 'create') {
        response = await createQuestion(data)
      } else {
        const { id, ...updateData } = data
        response = await updateQuestion(id, updateData)
      }
      
      if (response.success) {
        ElMessage.success(dialogMode.value === 'create' ? '创建成功' : '更新成功')
        dialogVisible.value = false
        loadQuestions()
      }
    } catch (error) {
      ElMessage.error(dialogMode.value === 'create' ? '创建失败' : '更新失败')
      console.error(error)
    } finally {
      submitting.value = false
    }
  })
}

// 重置表单
const resetForm = () => {
  Object.assign(questionForm, {
    exam_type: '',
    question_type: '',
    subject: '',
    chapter: '',
    difficulty: 3,
    content: '',
    options: ['', '', '', ''],
    correct_answer: '',
    explanation: '',
    tags: []
  })
  questionFormRef.value?.clearValidate()
}

// 添加选项
const addOption = () => {
  questionForm.options.push('')
}

// 删除选项
const removeOption = (index) => {
  questionForm.options.splice(index, 1)
}

// 显示导入对话框
const showImportDialog = () => {
  uploadFile.value = null
  importDialogVisible.value = true
}

// 文件选择处理
const handleFileChange = (file) => {
  uploadFile.value = file.raw
}

// 批量导入
const handleImport = async () => {
  if (!uploadFile.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }
  
  importing.value = true
  try {
    const reader = new FileReader()
    reader.onload = async (e) => {
      try {
        const data = JSON.parse(e.target.result)
        const response = await importQuestions(data)
        
        if (response.success) {
          ElMessage.success(response.data.message)
          importDialogVisible.value = false
          loadQuestions()
        }
      } catch (error) {
        ElMessage.error('文件格式错误或导入失败')
        console.error(error)
      } finally {
        importing.value = false
      }
    }
    reader.readAsText(uploadFile.value)
  } catch (error) {
    ElMessage.error('导入失败')
    console.error(error)
    importing.value = false
  }
}

// 工具函数
const getQuestionTypeLabel = (type) => {
  const labels = {
    'single_choice': '单选',
    'multiple_choice': '多选',
    'true_false': '判断',
    'fill_blank': '填空',
    'essay': '简答'
  }
  return labels[type] || type
}

const getQuestionTypeColor = (type) => {
  const colors = {
    'single_choice': 'primary',
    'multiple_choice': 'success',
    'true_false': 'warning',
    'fill_blank': 'info',
    'essay': 'danger'
  }
  return colors[type] || ''
}

const getExamTypeLabel = (type) => {
  const labels = {
    'civil_service': '公务员',
    'postgraduate': '研究生',
    'public_institution': '事业编'
  }
  return labels[type] || type
}

const truncateText = (text, maxLength) => {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 初始化
onMounted(() => {
  loadQuestions()
})
</script>

<style scoped>
.question-management {
  padding: 20px;
}

.header-card {
  margin-bottom: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.header-right {
  display: flex;
  gap: 10px;
}

.filter-card {
  margin-bottom: 20px;
}

.filter-form {
  margin-bottom: 0;
}

.table-card {
  margin-bottom: 20px;
}

.question-content-preview {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.5;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.options-input {
  width: 100%;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.option-label {
  font-weight: bold;
  min-width: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
  }
  
  .header-right .el-button {
    flex: 1;
  }
}
</style>
