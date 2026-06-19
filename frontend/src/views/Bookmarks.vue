<template>
  <div class="bookmarks-page">
    <div class="page-header">
      <div class="header-left">
        <h2>我的收藏</h2>
        <p class="subtitle">收藏重要题目，方便随时复习</p>
      </div>
    </div>

    <BookmarkList 
      ref="bookmarkListRef"
      @view-question="handleViewQuestion"
      @edit="handleEditBookmark"
    />

    <!-- 编辑收藏对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑收藏"
      width="500px"
    >
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="标签">
          <el-select
            v-model="editForm.tags"
            multiple
            filterable
            allow-create
            placeholder="添加标签（可自定义）"
            style="width: 100%"
          >
            <el-option label="重点" value="重点" />
            <el-option label="易错" value="易错" />
            <el-option label="难题" value="难题" />
            <el-option label="常考" value="常考" />
          </el-select>
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="editForm.note"
            type="textarea"
            :rows="4"
            placeholder="添加备注信息"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateBookmark" :loading="updating">
          更新
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看题目对话框 -->
    <el-dialog
      v-model="showQuestionDialog"
      title="题目详情"
      width="700px"
    >
      <div v-if="selectedQuestion" class="question-detail">
        <div class="question-header">
          <el-tag type="primary">{{ selectedQuestion.exam_type }}</el-tag>
          <el-tag>{{ selectedQuestion.question_type }}</el-tag>
          <el-tag :type="getDifficultyType(selectedQuestion.difficulty)">
            {{ getDifficultyLabel(selectedQuestion.difficulty) }}
          </el-tag>
        </div>

        <div class="question-meta">
          <span>{{ selectedQuestion.subject }} - {{ selectedQuestion.chapter }}</span>
        </div>

        <el-divider />

        <div class="question-content">
          <div class="question-text">{{ selectedQuestion.content }}</div>
        </div>

        <div class="question-options" v-if="selectedQuestion.options">
          <div 
            v-for="(option, index) in parseOptions(selectedQuestion.options)" 
            :key="index"
            class="option-item"
            :class="{ 'is-answer': isCorrectOption(index, selectedQuestion.answer) }"
          >
            <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
            <span class="option-text">{{ option }}</span>
          </div>
        </div>

        <el-divider />

        <div class="question-answer">
          <div class="answer-label">正确答案：</div>
          <div class="answer-value">{{ selectedQuestion.answer }}</div>
        </div>

        <div class="question-explanation" v-if="selectedQuestion.explanation">
          <div class="explanation-label">解析：</div>
          <div class="explanation-text">{{ selectedQuestion.explanation }}</div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import BookmarkList from '../components/BookmarkList.vue'
import { updateBookmark } from '../api/bookmarks'

const bookmarkListRef = ref(null)
const showEditDialog = ref(false)
const showQuestionDialog = ref(false)
const updating = ref(false)
const editingBookmark = ref(null)
const selectedQuestion = ref(null)

const editForm = reactive({
  tags: [],
  note: ''
})

const handleViewQuestion = (question) => {
  selectedQuestion.value = question
  showQuestionDialog.value = true
}

const handleEditBookmark = (bookmark) => {
  editingBookmark.value = bookmark
  editForm.tags = bookmark.tags || []
  editForm.note = bookmark.note || ''
  showEditDialog.value = true
}

const handleUpdateBookmark = async () => {
  if (!editingBookmark.value) return

  updating.value = true
  try {
    await updateBookmark(editingBookmark.value.id, {
      tags: editForm.tags,
      note: editForm.note
    })
    ElMessage.success('更新成功')
    showEditDialog.value = false
    bookmarkListRef.value?.refresh()
  } catch (error) {
    ElMessage.error('更新失败')
  } finally {
    updating.value = false
  }
}

const parseOptions = (options) => {
  if (typeof options === 'string') {
    try {
      return JSON.parse(options)
    } catch {
      return options.split('\n').filter(o => o.trim())
    }
  }
  return options || []
}

const isCorrectOption = (index, answer) => {
  const optionLabel = String.fromCharCode(65 + index)
  return answer.includes(optionLabel)
}

const getDifficultyLabel = (difficulty) => {
  const labels = { 1: '简单', 2: '中等', 3: '困难' }
  return labels[difficulty] || '未知'
}

const getDifficultyType = (difficulty) => {
  const types = { 1: 'success', 2: 'warning', 3: 'danger' }
  return types[difficulty] || 'info'
}
</script>

<style scoped>
.bookmarks-page {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-left h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.subtitle {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.question-detail {
  padding: 12px 0;
}

.question-header {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.question-meta {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 16px;
}

.question-content {
  margin-bottom: 16px;
}

.question-text {
  font-size: 15px;
  line-height: 1.8;
  color: var(--el-text-color-primary);
}

.question-options {
  margin-bottom: 16px;
}

.option-item {
  display: flex;
  padding: 12px;
  margin-bottom: 8px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  transition: all 0.3s;
}

.option-item.is-answer {
  background: var(--el-color-success-light-9);
  border: 1px solid var(--el-color-success);
}

.option-label {
  font-weight: 600;
  margin-right: 8px;
  min-width: 24px;
}

.option-text {
  flex: 1;
  line-height: 1.6;
}

.question-answer {
  padding: 12px;
  background: var(--el-color-success-light-9);
  border-radius: 4px;
  margin-bottom: 16px;
}

.answer-label {
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--el-color-success);
}

.answer-value {
  font-size: 16px;
  font-weight: 600;
}

.question-explanation {
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.explanation-label {
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.explanation-text {
  line-height: 1.8;
  color: var(--el-text-color-regular);
}
</style>
