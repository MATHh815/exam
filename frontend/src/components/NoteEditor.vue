<template>
  <div class="note-editor">
    <div class="editor-toolbar">
      <div class="toolbar-group">
        <el-tooltip content="加粗" placement="top">
          <button class="toolbar-btn" @click="insertMarkdown('**', '**')">
            <span class="btn-icon bold">B</span>
          </button>
        </el-tooltip>
        <el-tooltip content="斜体" placement="top">
          <button class="toolbar-btn" @click="insertMarkdown('*', '*')">
            <span class="btn-icon italic">I</span>
          </button>
        </el-tooltip>
        <el-tooltip content="代码" placement="top">
          <button class="toolbar-btn" @click="insertMarkdown('`', '`')">
            <span class="btn-icon code">&lt;/&gt;</span>
          </button>
        </el-tooltip>
      </div>

      <div class="toolbar-divider"></div>
      
      <div class="toolbar-group">
        <el-tooltip content="一级标题" placement="top">
          <button class="toolbar-btn" @click="insertMarkdown('# ', '')">H1</button>
        </el-tooltip>
        <el-tooltip content="二级标题" placement="top">
          <button class="toolbar-btn" @click="insertMarkdown('## ', '')">H2</button>
        </el-tooltip>
        <el-tooltip content="三级标题" placement="top">
          <button class="toolbar-btn" @click="insertMarkdown('### ', '')">H3</button>
        </el-tooltip>
      </div>

      <div class="toolbar-divider"></div>

      <div class="toolbar-group">
        <el-tooltip content="无序列表" placement="top">
          <button class="toolbar-btn" @click="insertMarkdown('- ', '')">
            <el-icon><List /></el-icon>
          </button>
        </el-tooltip>
        <el-tooltip content="引用" placement="top">
          <button class="toolbar-btn" @click="insertMarkdown('> ', '')">
            <el-icon><ChatLineSquare /></el-icon>
          </button>
        </el-tooltip>
        <el-tooltip content="代码块" placement="top">
          <button class="toolbar-btn" @click="insertCodeBlock">
            <el-icon><Document /></el-icon>
          </button>
        </el-tooltip>
      </div>

      <div class="toolbar-divider"></div>

      <div class="toolbar-group">
        <el-tooltip content="链接题目" placement="top">
          <button class="toolbar-btn link-btn" @click="showQuestionLinkDialog = true">
            <el-icon><Link /></el-icon>
            <span class="btn-text">链接题目</span>
          </button>
        </el-tooltip>
      </div>

      <div class="toolbar-spacer"></div>

      <el-switch
        v-model="showPreview"
        class="preview-switch"
        active-text="预览"
        inactive-text="编辑"
      />
    </div>

    <div class="editor-content" :class="{ 'split-view': showPreview }">
      <div class="editor-pane" v-show="!showPreview || showPreview">
        <el-input
          ref="textareaRef"
          v-model="localContent"
          type="textarea"
          :rows="rows"
          placeholder="支持 Markdown 格式，点击工具栏「链接题目」按钮搜索题目..."
          @input="handleInput"
          :maxlength="5000"
          show-word-limit
        />
      </div>

      <div class="preview-pane" v-if="showPreview">
        <div class="preview-header">
          <span class="preview-title">预览</span>
          <el-tag size="small" type="success" effect="plain">Markdown 渲染</el-tag>
        </div>
        <div class="markdown-body" v-html="renderedContent"></div>
      </div>
    </div>

    <div class="editor-footer">
      <div class="footer-left">
        <el-tag size="small" type="info" effect="plain">
          <el-icon><Edit /></el-icon>
          支持 Markdown
        </el-tag>
        <el-tag size="small" type="success" effect="plain">
          <el-icon><Link /></el-icon>
          支持题目链接
        </el-tag>
      </div>
      <span class="char-count">{{ localContent.length }} / 5000</span>
    </div>

    <!-- 题目链接对话框 -->
    <el-dialog
      v-model="showQuestionLinkDialog"
      title="链接题目"
      width="700px"
      :close-on-click-modal="false"
      class="question-link-modal"
    >
      <div class="question-link-dialog">
        <el-input
          v-model="questionSearchKeyword"
          placeholder="输入关键词搜索题目..."
          clearable
          @input="handleQuestionSearch"
          size="large"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>

        <div v-loading="searchingQuestions" class="question-list">
          <el-empty 
            v-if="!searchingQuestions && searchResults.length === 0" 
            description="暂无搜索结果"
            :image-size="100"
          />
          
          <div 
            v-for="question in searchResults" 
            :key="question.id"
            class="question-item"
            @click="insertQuestionLink(question)"
          >
            <div class="question-title">
              {{ getQuestionTitle(question) }}
            </div>
            <div class="question-meta">
              <el-tag size="small" type="primary" effect="plain">{{ question.subject }}</el-tag>
              <el-tag size="small" effect="plain">{{ question.chapter }}</el-tag>
            </div>
            <div class="question-preview">{{ getQuestionPreview(question.content) }}</div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="showQuestionLinkDialog = false" size="large">取消</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { ElMessage } from 'element-plus'
import { 
  List, 
  ChatLineSquare,
  Document,
  Link,
  Search,
  Edit
} from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  rows: {
    type: Number,
    default: 15
  }
})

const emit = defineEmits(['update:modelValue'])

const textareaRef = ref(null)
const localContent = ref(props.modelValue)
const showPreview = ref(false)
const showQuestionLinkDialog = ref(false)
const questionSearchKeyword = ref('')
const searchResults = ref([])
const searchingQuestions = ref(false)
let searchTimeout = null

// 配置 marked
marked.setOptions({
  breaks: true,
  gfm: true
})

// 渲染 Markdown 内容，包括题目链接
const renderedContent = computed(() => {
  if (!localContent.value) return '<p class="empty-hint">暂无内容</p>'
  
  // 先处理题目链接
  let processedContent = localContent.value
  
  // 匹配 [[题:标题]] 格式 - 显示为漂亮的题目链接
  processedContent = processedContent.replace(/\[\[题:(.*?)\]\]/g, (match, title) => {
    // 转义 HTML 特殊字符
    const escapedTitle = title
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;')
    
    return `<a href="#" class="question-link-title" onclick="return false;">📝 ${escapedTitle}</a>`
  })
  
  // 兼容旧格式 [[Q:123]] - 如果存在的话
  processedContent = processedContent.replace(/\[\[Q:(\d+)\]\]/g, (match, id) => {
    return `<a href="#" class="question-link-id" onclick="return false;">📝 题目 #${id}</a>`
  })
  
  // 渲染 Markdown
  const html = marked(processedContent)
  return DOMPurify.sanitize(html, {
    ADD_ATTR: ['onclick']
  })
})

watch(() => props.modelValue, (newVal) => {
  localContent.value = newVal
})

const handleInput = () => {
  emit('update:modelValue', localContent.value)
}

const insertMarkdown = (before, after) => {
  const textarea = textareaRef.value?.textarea
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selectedText = localContent.value.substring(start, end)
  const beforeText = localContent.value.substring(0, start)
  const afterText = localContent.value.substring(end)

  localContent.value = beforeText + before + selectedText + after + afterText
  emit('update:modelValue', localContent.value)

  // 恢复光标位置
  setTimeout(() => {
    textarea.focus()
    const newPos = start + before.length + selectedText.length
    textarea.setSelectionRange(newPos, newPos)
  }, 0)
}

const insertCodeBlock = () => {
  insertMarkdown('\n```\n', '\n```\n')
}

// 搜索题目
const handleQuestionSearch = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  searchTimeout = setTimeout(async () => {
    const keyword = questionSearchKeyword.value.trim()
    if (!keyword) {
      searchResults.value = []
      return
    }
    
    searchingQuestions.value = true
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get('/api/questions', {
        params: {
          keyword: keyword,
          page: 1,
          page_size: 10
        },
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.data.success) {
        searchResults.value = response.data.data.questions || []
      } else {
        searchResults.value = []
      }
    } catch (error) {
      console.error('搜索题目失败:', error)
      ElMessage.error('搜索题目失败')
      searchResults.value = []
    } finally {
      searchingQuestions.value = false
    }
  }, 300)
}

// 获取题目标题（从题目内容中提取）
const getQuestionTitle = (question) => {
  if (!question || !question.content) return '未知题目'
  
  // 移除 Markdown 格式字符
  let text = question.content.replace(/[#*`>\-\[\]]/g, '').trim()
  
  // 提取第一句话（以句号、问号、感叹号结尾）
  const sentenceMatch = text.match(/^[^。？！.?!]+[。？！.?!]?/)
  if (sentenceMatch) {
    text = sentenceMatch[0]
  }
  
  // 如果太长，截取前30个字符
  if (text.length > 30) {
    text = text.substring(0, 30) + '...'
  }
  
  return text || '未知题目'
}

// 插入题目链接（使用标题格式）
const insertQuestionLink = (question) => {
  const questionTitle = getQuestionTitle(question)
  const linkText = `[[题:${questionTitle}]]`
  const textarea = textareaRef.value?.textarea
  
  if (textarea) {
    const start = textarea.selectionStart
    const beforeText = localContent.value.substring(0, start)
    const afterText = localContent.value.substring(start)
    
    localContent.value = beforeText + linkText + afterText
    emit('update:modelValue', localContent.value)
    
    // 恢复光标位置
    setTimeout(() => {
      textarea.focus()
      const newPos = start + linkText.length
      textarea.setSelectionRange(newPos, newPos)
    }, 0)
  }
  
  showQuestionLinkDialog.value = false
  questionSearchKeyword.value = ''
  searchResults.value = []
  ElMessage.success('已插入题目链接')
}

// 获取题目预览文本
const getQuestionPreview = (content) => {
  const text = content.replace(/[#*`>\-\[\]]/g, '').trim()
  return text.length > 100 ? text.substring(0, 100) + '...' : text
}
</script>

<style scoped>
.note-editor {
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border: 2px solid rgba(102, 126, 234, 0.2);
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
  transition: all 0.3s ease;
}

.note-editor:hover {
  border-color: rgba(102, 126, 234, 0.4);
  box-shadow: 0 12px 48px rgba(102, 126, 234, 0.15);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-bottom: 2px solid rgba(102, 126, 234, 0.15);
  backdrop-filter: blur(10px);
  gap: 12px;
}

.toolbar-group {
  display: flex;
  gap: 6px;
  align-items: center;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 12px;
  border: 1.5px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 500;
  color: #667eea;
  min-width: 36px;
  height: 36px;
}

.toolbar-btn:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.toolbar-btn:active {
  transform: translateY(0);
}

.btn-icon {
  display: inline-block;
  font-size: 14px;
  font-weight: 600;
}

.btn-icon.bold {
  font-weight: 700;
}

.btn-icon.italic {
  font-style: italic;
}

.btn-icon.code {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.btn-text {
  font-size: 13px;
}

.link-btn {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: rgba(102, 126, 234, 0.3);
}

.link-btn:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  background: linear-gradient(to bottom, transparent, rgba(102, 126, 234, 0.3), transparent);
}

.toolbar-spacer {
  flex: 1;
}

.preview-switch {
  --el-switch-on-color: #667eea;
  --el-switch-off-color: #dcdfe6;
}

.preview-switch :deep(.el-switch__label) {
  color: #667eea;
  font-weight: 500;
}

.editor-content {
  display: flex;
  min-height: 400px;
}

.editor-content.split-view {
  display: grid;
  grid-template-columns: 1fr 1fr;
}

.editor-pane {
  flex: 1;
  position: relative;
}

.editor-pane :deep(.el-textarea) {
  height: 100%;
}

.editor-pane :deep(.el-textarea__inner) {
  border: none;
  border-radius: 0;
  box-shadow: none;
  resize: none;
  padding: 20px;
  font-size: 15px;
  line-height: 1.8;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(10px);
  transition: background 0.3s ease;
}

.editor-pane :deep(.el-textarea__inner:focus) {
  background: rgba(255, 255, 255, 0.8);
}

.editor-pane :deep(.el-textarea__inner::placeholder) {
  color: rgba(102, 126, 234, 0.4);
}

.preview-pane {
  flex: 1;
  border-left: 2px solid rgba(102, 126, 234, 0.15);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
  backdrop-filter: blur(10px);
  overflow-y: auto;
  max-height: 600px;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-bottom: 2px solid rgba(102, 126, 234, 0.15);
  backdrop-filter: blur(10px);
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.markdown-body {
  padding: 20px;
  font-size: 15px;
  line-height: 1.8;
  color: #2c3e50;
}

.markdown-body :deep(h1) {
  font-size: 28px;
  font-weight: 700;
  margin: 24px 0 16px;
  padding-bottom: 12px;
  border-bottom: 3px solid transparent;
  border-image: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-image-slice: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.markdown-body :deep(h2) {
  font-size: 24px;
  font-weight: 600;
  margin: 20px 0 12px;
  color: #667eea;
  position: relative;
  padding-left: 16px;
}

.markdown-body :deep(h2::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 70%;
  background: linear-gradient(to bottom, #667eea, #764ba2);
  border-radius: 2px;
}

.markdown-body :deep(h3) {
  font-size: 20px;
  font-weight: 600;
  margin: 16px 0 10px;
  color: #764ba2;
}

.markdown-body :deep(p) {
  margin: 12px 0;
  line-height: 1.8;
}

.markdown-body :deep(code) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  padding: 3px 8px;
  border-radius: 6px;
  font-family: 'Courier New', 'Consolas', monospace;
  font-size: 14px;
  color: #667eea;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.markdown-body :deep(pre) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  padding: 16px;
  border-radius: 12px;
  overflow-x: auto;
  border: 2px solid rgba(102, 126, 234, 0.15);
  margin: 16px 0;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
  border: none;
  color: #2c3e50;
}

.markdown-body :deep(blockquote) {
  border-left: 4px solid #667eea;
  padding: 12px 16px;
  margin: 16px 0;
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.08) 0%, transparent 100%);
  border-radius: 0 8px 8px 0;
  color: #5a6c7d;
  font-style: italic;
}

.markdown-body :deep(ul), 
.markdown-body :deep(ol) {
  padding-left: 28px;
  margin: 12px 0;
}

.markdown-body :deep(li) {
  margin: 6px 0;
  line-height: 1.8;
}

.markdown-body :deep(a) {
  color: #667eea;
  text-decoration: none;
  border-bottom: 1px solid rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
}

.markdown-body :deep(a:hover) {
  color: #764ba2;
  border-bottom-color: #764ba2;
}

/* 题目链接样式 */
.markdown-body :deep(.question-link-title),
.markdown-body :deep(.question-link-id) {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 10px;
  color: #667eea;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-decoration: none;
  margin: 0 6px;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
}

.markdown-body :deep(.question-link-title:hover),
.markdown-body :deep(.question-link-id:hover) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.markdown-body :deep(.question-link-title:active),
.markdown-body :deep(.question-link-id:active) {
  transform: translateY(-1px) scale(1.01);
}

.empty-hint {
  color: rgba(102, 126, 234, 0.4);
  text-align: center;
  padding: 60px 0;
  font-size: 16px;
  font-style: italic;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
  border-top: 2px solid rgba(102, 126, 234, 0.15);
  backdrop-filter: blur(10px);
}

.footer-left {
  display: flex;
  gap: 8px;
}

.footer-left :deep(.el-tag) {
  border-radius: 6px;
  border-color: rgba(102, 126, 234, 0.3);
}

.char-count {
  font-size: 13px;
  font-weight: 500;
  color: #667eea;
}

/* 题目链接对话框 */
.question-link-dialog {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-link-dialog :deep(.el-input__wrapper) {
  border-radius: 12px;
  border: 2px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s ease;
}

.question-link-dialog :deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.4);
}

.question-link-dialog :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.question-list {
  max-height: 400px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.question-item {
  padding: 16px;
  border: 2px solid rgba(102, 126, 234, 0.15);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
}

.question-item:hover {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.question-title {
  font-size: 15px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
  line-height: 1.5;
}

.question-meta {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.question-preview {
  font-size: 13px;
  line-height: 1.6;
  color: #5a6c7d;
  margin-top: 8px;
}

/* 滚动条样式 */
.preview-pane::-webkit-scrollbar,
.question-list::-webkit-scrollbar {
  width: 8px;
}

.preview-pane::-webkit-scrollbar-track,
.question-list::-webkit-scrollbar-track {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 4px;
}

.preview-pane::-webkit-scrollbar-thumb,
.question-list::-webkit-scrollbar-thumb {
  background: linear-gradient(to bottom, #667eea, #764ba2);
  border-radius: 4px;
}

.preview-pane::-webkit-scrollbar-thumb:hover,
.question-list::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(to bottom, #764ba2, #667eea);
}
</style>
