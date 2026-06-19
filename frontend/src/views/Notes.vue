<template>
  <div class="notes-page">
    <div class="page-header">
      <div class="header-left">
        <h2>我的笔记</h2>
        <p class="subtitle">记录学习心得，整理知识要点</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建笔记
      </el-button>
    </div>

    <div class="search-bar">
      <div class="search-header">
        <div class="stats-info">
          <el-icon class="stats-icon"><Document /></el-icon>
          <span class="stats-text">共 <span class="stats-number">{{ total }}</span> 条笔记</span>
        </div>
      </div>

      <div class="filter-section">
        <div class="filter-row">
          <div class="filter-item filter-search">
            <label class="filter-label">搜索笔记</label>
            <el-input
              v-model="searchKeyword"
              placeholder="输入关键词搜索笔记内容..."
              clearable
              @change="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <div class="filter-item">
            <label class="filter-label">科目筛选</label>
            <el-select 
              v-model="filters.subject" 
              placeholder="全部科目" 
              clearable 
              @change="handleSearch"
            >
              <el-option label="行测" value="行测" />
              <el-option label="申论" value="申论" />
              <el-option label="数学" value="数学" />
              <el-option label="英语" value="英语" />
              <el-option label="政治" value="政治" />
            </el-select>
          </div>

          <div class="filter-item">
            <label class="filter-label">排序方式</label>
            <el-select 
              v-model="filters.sort_by" 
              placeholder="选择排序" 
              @change="handleSearch"
            >
              <el-option label="最新创建" value="created_at_desc" />
              <el-option label="最早创建" value="created_at_asc" />
              <el-option label="最近更新" value="updated_at_desc" />
            </el-select>
          </div>
        </div>
      </div>
    </div>

    <div v-loading="loading" class="notes-container">
      <el-empty v-if="!loading && notes.length === 0" description="暂无笔记" />

      <div v-else class="notes-grid">
        <el-card 
          v-for="note in notes" 
          :key="note.id" 
          class="note-card"
          shadow="hover"
          @click="handleViewNote(note)"
        >
          <div class="note-header">
            <div class="note-meta">
              <el-tag size="small" type="primary">{{ note.question.subject }}</el-tag>
              <el-tag size="small">{{ note.question.chapter }}</el-tag>
            </div>
            <el-dropdown @command="(cmd) => handleCommand(cmd, note)">
              <el-button link>
                <el-icon><MoreFilled /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="edit">编辑</el-dropdown-item>
                  <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>

          <div class="note-content">
            <div class="note-preview">{{ getPreviewText(note.content) }}</div>
          </div>

          <div class="note-tags" v-if="note.tags && note.tags.length > 0">
            <el-tag 
              v-for="tag in note.tags" 
              :key="tag" 
              size="small" 
              type="info"
              effect="plain"
            >
              {{ tag }}
            </el-tag>
          </div>

          <div class="note-footer">
            <span class="note-time">{{ formatDate(note.updated_at || note.created_at) }}</span>
            <span class="note-length">{{ note.content.length }} 字</span>
          </div>
        </el-card>
      </div>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchNotes"
        @size-change="handleSizeChange"
        style="margin-top: 20px; justify-content: center"
      />
    </div>

    <!-- 创建/编辑笔记对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingNote ? '编辑笔记' : '新建笔记'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="noteForm" label-width="80px">
        <el-form-item label="题目ID" v-if="!editingNote">
          <el-input-number 
            v-model="noteForm.question_id" 
            :min="1" 
            placeholder="请输入题目ID"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="标签">
          <el-select
            v-model="noteForm.tags"
            multiple
            filterable
            allow-create
            placeholder="添加标签（可自定义）"
            style="width: 100%"
          >
            <el-option label="重点" value="重点" />
            <el-option label="易错" value="易错" />
            <el-option label="技巧" value="技巧" />
            <el-option label="公式" value="公式" />
          </el-select>
        </el-form-item>

        <el-form-item label="笔记内容">
          <NoteEditor v-model="noteForm.content" :rows="15" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="handleCancelEdit">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingNote ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看笔记对话框 -->
    <el-dialog
      v-model="showViewDialog"
      title="笔记详情"
      width="800px"
    >
      <div v-if="selectedNote" class="note-detail">
        <div class="detail-header">
          <div class="detail-meta">
            <el-tag type="primary">{{ selectedNote.question.subject }}</el-tag>
            <el-tag>{{ selectedNote.question.chapter }}</el-tag>
            <el-tag type="info">题目 #{{ selectedNote.question_id }}</el-tag>
          </div>
          <div class="detail-actions">
            <el-button size="small" @click="handleEditNote(selectedNote)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDeleteNote(selectedNote)">删除</el-button>
          </div>
        </div>

        <el-divider />

        <div class="detail-content markdown-body" v-html="renderMarkdown(selectedNote.content)"></div>

        <div v-if="selectedNote.tags && selectedNote.tags.length > 0" class="detail-tags">
          <el-tag 
            v-for="tag in selectedNote.tags" 
            :key="tag" 
            type="info"
            effect="plain"
          >
            {{ tag }}
          </el-tag>
        </div>

        <div class="detail-footer">
          <span>创建于 {{ formatDate(selectedNote.created_at) }}</span>
          <span v-if="selectedNote.updated_at">更新于 {{ formatDate(selectedNote.updated_at) }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Plus, Search, MoreFilled, Document } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import NoteEditor from '../components/NoteEditor.vue'
import { getNotes, createNote, updateNote, deleteNote, searchNotes } from '../api/notes'

const loading = ref(false)
const submitting = ref(false)
const notes = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const searchKeyword = ref('')
const showCreateDialog = ref(false)
const showViewDialog = ref(false)
const editingNote = ref(null)
const selectedNote = ref(null)

const filters = reactive({
  subject: '',
  sort_by: 'created_at_desc'
})

const noteForm = reactive({
  question_id: null,
  content: '',
  tags: []
})

const fetchNotes = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters
    }

    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null) {
        delete params[key]
      }
    })

    const res = searchKeyword.value 
      ? await searchNotes({ ...params, keyword: searchKeyword.value })
      : await getNotes(params)
    
    notes.value = res.notes || []
    total.value = res.total || 0
  } catch (error) {
    ElMessage.error('获取笔记列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchNotes()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchNotes()
}

const handleSubmit = async () => {
  if (!noteForm.content.trim()) {
    ElMessage.warning('请输入笔记内容')
    return
  }

  if (!editingNote.value && !noteForm.question_id) {
    ElMessage.warning('请输入题目ID')
    return
  }

  submitting.value = true
  try {
    if (editingNote.value) {
      await updateNote(editingNote.value.id, {
        content: noteForm.content,
        tags: noteForm.tags
      })
      ElMessage.success('更新笔记成功')
    } else {
      await createNote(noteForm)
      ElMessage.success('创建笔记成功')
    }
    showCreateDialog.value = false
    resetForm()
    fetchNotes()
  } catch (error) {
    ElMessage.error(editingNote.value ? '更新笔记失败' : '创建笔记失败')
  } finally {
    submitting.value = false
  }
}

const handleCancelEdit = () => {
  showCreateDialog.value = false
  resetForm()
}

const handleViewNote = (note) => {
  selectedNote.value = note
  showViewDialog.value = true
}

const handleEditNote = (note) => {
  editingNote.value = note
  noteForm.question_id = note.question_id
  noteForm.content = note.content
  noteForm.tags = note.tags || []
  showViewDialog.value = false
  showCreateDialog.value = true
}

const handleDeleteNote = async (note) => {
  try {
    await ElMessageBox.confirm('确定要删除这条笔记吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteNote(note.id)
    ElMessage.success('删除成功')
    showViewDialog.value = false
    fetchNotes()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleCommand = (command, note) => {
  if (command === 'edit') {
    handleEditNote(note)
  } else if (command === 'delete') {
    handleDeleteNote(note)
  }
}

const resetForm = () => {
  editingNote.value = null
  noteForm.question_id = null
  noteForm.content = ''
  noteForm.tags = []
}

const getPreviewText = (content) => {
  // 移除 Markdown 标记，获取纯文本预览
  const text = content.replace(/[#*`>\-\[\]]/g, '').trim()
  return text.length > 150 ? text.substring(0, 150) + '...' : text
}

const renderMarkdown = (content) => {
  const html = marked(content)
  return DOMPurify.sanitize(html)
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchNotes()
})
</script>

<style scoped>
.notes-page {
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
}

.subtitle {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.search-bar {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  backdrop-filter: blur(10px);
}

.search-header {
  margin-bottom: 20px;
}

.stats-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stats-icon {
  font-size: 24px;
  color: #667eea;
}

.stats-text {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
}

.stats-number {
  font-size: 20px;
  font-weight: 600;
  color: #667eea;
  margin: 0 4px;
}

.filter-section {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 20px;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-search {
  grid-column: span 2;
}

@media (max-width: 768px) {
  .filter-row {
    grid-template-columns: 1fr;
  }
  
  .filter-search {
    grid-column: span 1;
  }
}

.filter-label {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 4px;
}

.filter-item :deep(.el-select),
.filter-item :deep(.el-input) {
  width: 100%;
}

.filter-item :deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none;
  transition: all 0.3s;
}

.filter-item :deep(.el-input__wrapper:hover) {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.5);
}

.filter-item :deep(.el-input__wrapper.is-focus) {
  background: rgba(255, 255, 255, 0.12);
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.filter-item :deep(.el-input__inner) {
  color: #fff;
}

.filter-item :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.filter-item :deep(.el-select__wrapper) {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: none;
}

.filter-item :deep(.el-select__wrapper:hover) {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.5);
}

.filter-item :deep(.el-select__wrapper.is-focused) {
  background: rgba(255, 255, 255, 0.12);
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.filter-item :deep(.el-select__placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.filter-item :deep(.el-select__selected-item) {
  color: #fff;
}

.notes-container {
  min-height: 400px;
}

.notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.note-card {
  cursor: pointer;
  transition: all 0.3s;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.note-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.note-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.note-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.note-content {
  flex: 1;
  margin-bottom: 12px;
}

.note-preview {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.note-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.note-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.note-detail {
  padding: 12px 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-meta {
  display: flex;
  gap: 8px;
}

.detail-content {
  padding: 16px 0;
  line-height: 1.8;
}

.detail-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.detail-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

/* Markdown 样式 */
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 16px 0 8px;
}

.markdown-body :deep(p) {
  margin: 8px 0;
}

.markdown-body :deep(code) {
  background: var(--el-fill-color-light);
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.markdown-body :deep(pre) {
  background: var(--el-fill-color-light);
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid var(--el-color-primary);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--el-text-color-secondary);
}
</style>
