<template>
  <div class="bookmark-list">
    <div class="list-header">
      <div class="header-top">
        <div class="stats-info">
          <el-icon class="stats-icon"><Star /></el-icon>
          <span class="stats-text">共 <span class="stats-number">{{ total }}</span> 个收藏</span>
        </div>
      </div>

      <div class="filter-section">
        <div class="filter-row">
          <div class="filter-item">
            <label class="filter-label">考试类型</label>
            <el-select 
              v-model="filters.exam_type" 
              placeholder="全部类型" 
              clearable 
              @change="handleFilterChange"
            >
              <el-option label="公务员" value="公务员" />
              <el-option label="考研" value="考研" />
              <el-option label="事业编" value="事业编" />
            </el-select>
          </div>

          <div class="filter-item">
            <label class="filter-label">难度</label>
            <el-select 
              v-model="filters.difficulty" 
              placeholder="全部难度" 
              clearable 
              @change="handleFilterChange"
            >
              <el-option label="简单" :value="1" />
              <el-option label="中等" :value="2" />
              <el-option label="困难" :value="3" />
            </el-select>
          </div>

          <div class="filter-item filter-search">
            <label class="filter-label">标签搜索</label>
            <el-input
              v-model="filters.tag"
              placeholder="输入标签名称"
              clearable
              @change="handleFilterChange"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>

          <div class="filter-item">
            <label class="filter-label">排序方式</label>
            <el-select 
              v-model="filters.sort_by" 
              placeholder="选择排序" 
              @change="handleFilterChange"
            >
              <el-option label="最新收藏" value="created_at_desc" />
              <el-option label="最早收藏" value="created_at_asc" />
              <el-option label="难度升序" value="difficulty_asc" />
              <el-option label="难度降序" value="difficulty_desc" />
            </el-select>
          </div>
        </div>
      </div>
    </div>

    <el-divider />

    <div v-loading="loading" class="bookmarks-container">
      <el-empty v-if="!loading && bookmarks.length === 0" description="暂无收藏" />

      <div v-else class="bookmark-items">
        <el-card 
          v-for="bookmark in bookmarks" 
          :key="bookmark.id" 
          class="bookmark-card"
          shadow="hover"
        >
          <div class="bookmark-header">
            <div class="question-info">
              <el-tag size="small" type="primary">{{ bookmark.question.exam_type }}</el-tag>
              <el-tag size="small">{{ bookmark.question.question_type }}</el-tag>
              <el-tag size="small" :type="getDifficultyType(bookmark.question.difficulty)">
                {{ getDifficultyLabel(bookmark.question.difficulty) }}
              </el-tag>
            </div>
            <el-button 
              link 
              type="danger" 
              @click="handleDelete(bookmark)"
            >
              <el-icon><Delete /></el-icon>
              取消收藏
            </el-button>
          </div>

          <div class="question-content">
            <div class="question-text">{{ bookmark.question.content }}</div>
          </div>

          <div class="bookmark-meta">
            <div class="meta-item">
              <el-icon><Folder /></el-icon>
              <span>{{ bookmark.question.subject }} - {{ bookmark.question.chapter }}</span>
            </div>
            <div class="meta-item">
              <el-icon><Calendar /></el-icon>
              <span>收藏于 {{ formatDate(bookmark.created_at) }}</span>
            </div>
          </div>

          <div v-if="bookmark.tags && bookmark.tags.length > 0" class="bookmark-tags">
            <el-tag 
              v-for="tag in bookmark.tags" 
              :key="tag" 
              size="small" 
              type="info"
              effect="plain"
            >
              {{ tag }}
            </el-tag>
          </div>

          <div v-if="bookmark.note" class="bookmark-note">
            <div class="note-label">备注：</div>
            <div class="note-content">{{ bookmark.note }}</div>
          </div>

          <div class="bookmark-actions">
            <el-button size="small" @click="$emit('view-question', bookmark.question)">
              查看题目
            </el-button>
            <el-button size="small" @click="$emit('edit', bookmark)">
              编辑收藏
            </el-button>
          </div>
        </el-card>
      </div>

      <el-pagination
        v-if="total > pageSize"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="handlePageChange"
        @size-change="handleSizeChange"
        style="margin-top: 20px; justify-content: center"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Delete, Folder, Calendar, Star } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getBookmarks, deleteBookmark } from '../api/bookmarks'

const emit = defineEmits(['view-question', 'edit', 'refresh'])

const loading = ref(false)
const bookmarks = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

const filters = reactive({
  exam_type: '',
  difficulty: null,
  tag: '',
  sort_by: 'created_at_desc'
})

const fetchBookmarks = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value,  // 修复：使用 per_page 而不是 page_size
      exam_type: filters.exam_type || undefined,
      difficulty: filters.difficulty || undefined,
      tags: filters.tag || undefined,  // 修复：使用 tags 参数
      sort_by: filters.sort_by ? filters.sort_by.replace('_at', '') : 'created_desc'  // 修复：转换排序参数格式
    }
    
    // 移除空值
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })

    const res = await getBookmarks(params)
    bookmarks.value = res.bookmarks || []
    total.value = res.total || 0
  } catch (error) {
    console.error('获取收藏列表失败:', error)
    ElMessage.error('获取收藏列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchBookmarks()
}

const handlePageChange = () => {
  fetchBookmarks()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchBookmarks()
}

const handleDelete = async (bookmark) => {
  try {
    await ElMessageBox.confirm('确定要取消收藏这道题目吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteBookmark(bookmark.id)
    ElMessage.success('已取消收藏')
    fetchBookmarks()
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消收藏失败')
    }
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const getDifficultyLabel = (difficulty) => {
  const labels = { 1: '简单', 2: '中等', 3: '困难' }
  return labels[difficulty] || '未知'
}

const getDifficultyType = (difficulty) => {
  const types = { 1: 'success', 2: 'warning', 3: 'danger' }
  return types[difficulty] || 'info'
}

onMounted(() => {
  fetchBookmarks()
})

defineExpose({
  refresh: fetchBookmarks
})
</script>

<style scoped>
.bookmark-list {
  padding: 0;
}

.list-header {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  backdrop-filter: blur(10px);
}

.header-top {
  margin-bottom: 20px;
}

.stats-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stats-icon {
  font-size: 24px;
  color: #ffd700;
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

.bookmarks-container {
  min-height: 400px;
}

.bookmark-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.bookmark-card {
  transition: all 0.3s;
}

.bookmark-card:hover {
  transform: translateY(-2px);
}

.bookmark-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.question-info {
  display: flex;
  gap: 8px;
}

.question-content {
  margin-bottom: 12px;
}

.question-text {
  font-size: 15px;
  line-height: 1.6;
  color: var(--el-text-color-primary);
}

.bookmark-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.bookmark-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.bookmark-note {
  padding: 8px 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  margin-bottom: 12px;
}

.note-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.note-content {
  font-size: 14px;
  color: var(--el-text-color-regular);
  line-height: 1.5;
}

.bookmark-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>
