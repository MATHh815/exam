<template>
  <div 
    class="ai-chat-container" 
    :class="{ 'is-expanded': isExpanded, 'is-fullscreen': isFullscreen, 'is-dragging': isDragging }"
    :style="containerStyle"
  >
    <!-- 悬浮按钮 -->
    <div 
      v-if="!isExpanded" 
      class="chat-fab"
      @click="toggleChat"
      @mousedown="startDragFab"
    >
      <div class="fab-icon">
        <el-icon :size="28"><ChatDotRound /></el-icon>
      </div>
      <div class="fab-pulse"></div>
      <span class="fab-label">AI 助手</span>
    </div>

    <!-- 聊天窗口 -->
    <transition name="chat-slide">
      <div v-if="isExpanded" class="chat-window">
        <!-- 头部（可拖动区域） -->
        <div 
          class="chat-header"
          @mousedown="startDrag"
          :class="{ 'draggable': !isFullscreen }"
        >
          <div class="header-info">
            <div class="ai-avatar">
              <el-icon :size="24"><Cpu /></el-icon>
            </div>
            <div class="header-text">
              <h4>AI 智能助手</h4>
              <span class="status">
                <span class="status-dot"></span>
                在线
              </span>
            </div>
          </div>
          <div class="header-actions">
            <el-tooltip content="清空对话" placement="top">
              <el-icon class="action-icon" @click="clearChat"><Delete /></el-icon>
            </el-tooltip>
            <el-tooltip :content="isFullscreen ? '退出全屏' : '全屏模式'" placement="top">
              <el-icon class="action-icon" @click="toggleFullscreen">
                <FullScreen v-if="!isFullscreen" />
                <ScaleToOriginal v-else />
              </el-icon>
            </el-tooltip>
            <el-tooltip content="最小化" placement="top">
              <el-icon class="action-icon" @click="toggleChat"><Minus /></el-icon>
            </el-tooltip>
            <el-tooltip content="关闭" placement="top">
              <el-icon class="action-icon" @click="closeChat"><Close /></el-icon>
            </el-tooltip>
          </div>
        </div>

        <!-- 消息列表 -->
        <div class="chat-messages" ref="messagesContainer">
          <!-- 欢迎消息 -->
          <div v-if="messages.length === 0" class="welcome-message">
            <div class="welcome-icon">
              <el-icon :size="48"><MagicStick /></el-icon>
            </div>
            <h3>你好！我是 AI 学习助手</h3>
            <p>有什么不会的题目可以问我，我会尽力帮你解答！</p>
            <div class="quick-questions">
              <div 
                v-for="(q, index) in quickQuestions" 
                :key="index"
                class="quick-question"
                @click="sendQuickQuestion(q)"
              >
                {{ q }}
              </div>
            </div>
          </div>

          <!-- 消息列表 -->
          <div 
            v-for="(msg, index) in messages" 
            :key="index"
            class="message-item"
            :class="msg.role"
          >
            <div class="message-avatar">
              <el-icon v-if="msg.role === 'assistant'" :size="20"><Cpu /></el-icon>
              <el-icon v-else :size="20"><User /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-bubble" v-html="formatMessage(msg.content)"></div>
              <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
          </div>

          <!-- 加载中 -->
          <div v-if="isLoading" class="message-item assistant">
            <div class="message-avatar">
              <el-icon :size="20"><Cpu /></el-icon>
            </div>
            <div class="message-content">
              <div class="message-bubble typing">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input">
          <div class="input-wrapper">
            <el-input
              v-model="inputMessage"
              type="textarea"
              :rows="1"
              :autosize="{ minRows: 1, maxRows: 4 }"
              placeholder="输入你的问题..."
              @keydown.enter.exact.prevent="sendMessage"
              :disabled="isLoading"
            />
          </div>
          <el-button 
            type="primary" 
            :icon="Promotion"
            circle
            :disabled="!inputMessage.trim() || isLoading"
            @click="sendMessage"
          />
        </div>

        <!-- 底部提示 -->
        <div class="chat-footer">
          <span>AI 回答仅供参考，请结合实际情况判断</span>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, watch, onMounted, onUnmounted } from 'vue'
import { 
  ChatDotRound, Cpu, Delete, Minus, Close, 
  MagicStick, User, Promotion, FullScreen, ScaleToOriginal
} from '@element-plus/icons-vue'
import { sendAIChat } from '../api/ai'
import { marked } from 'marked'

const props = defineProps({
  // 是否默认展开
  defaultExpanded: {
    type: Boolean,
    default: false
  },
  // 当前题目上下文（可选）
  questionContext: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close'])

// 状态
const isExpanded = ref(props.defaultExpanded)
const isFullscreen = ref(false)
const inputMessage = ref('')
const messages = ref([])
const isLoading = ref(false)
const messagesContainer = ref(null)

// 拖动相关状态
const isDragging = ref(false)
const position = ref({ x: null, y: null })
const dragOffset = ref({ x: 0, y: 0 })
const hasDragged = ref(false)

// 计算容器样式（支持拖动位置）
const containerStyle = computed(() => {
  if (isFullscreen.value) return {}
  if (position.value.x !== null && position.value.y !== null) {
    return {
      bottom: 'auto',
      right: 'auto',
      left: `${position.value.x}px`,
      top: `${position.value.y}px`
    }
  }
  return {}
})

/**
 * 开始拖动悬浮按钮
 */
function startDragFab(e) {
  if (e.button !== 0) return // 只响应左键
  hasDragged.value = false
  
  const rect = e.currentTarget.getBoundingClientRect()
  dragOffset.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
  
  document.addEventListener('mousemove', onDragFab)
  document.addEventListener('mouseup', stopDragFab)
}

/**
 * 拖动悬浮按钮
 */
function onDragFab(e) {
  hasDragged.value = true
  isDragging.value = true
  
  let newX = e.clientX - dragOffset.value.x
  let newY = e.clientY - dragOffset.value.y
  
  // 边界限制
  const maxX = window.innerWidth - 60
  const maxY = window.innerHeight - 60
  newX = Math.max(0, Math.min(newX, maxX))
  newY = Math.max(0, Math.min(newY, maxY))
  
  position.value = { x: newX, y: newY }
}

/**
 * 停止拖动悬浮按钮
 */
function stopDragFab(e) {
  document.removeEventListener('mousemove', onDragFab)
  document.removeEventListener('mouseup', stopDragFab)
  
  setTimeout(() => {
    isDragging.value = false
    // 如果拖动了，阻止点击事件
    if (hasDragged.value) {
      e.preventDefault()
      e.stopPropagation()
    }
  }, 10)
}

/**
 * 开始拖动窗口
 */
function startDrag(e) {
  if (isFullscreen.value) return
  if (e.target.closest('.action-icon')) return // 点击按钮时不拖动
  if (e.button !== 0) return // 只响应左键
  
  isDragging.value = true
  
  const container = e.currentTarget.closest('.ai-chat-container')
  const rect = container.getBoundingClientRect()
  
  dragOffset.value = {
    x: e.clientX - rect.left,
    y: e.clientY - rect.top
  }
  
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

/**
 * 拖动中
 */
function onDrag(e) {
  if (!isDragging.value) return
  
  let newX = e.clientX - dragOffset.value.x
  let newY = e.clientY - dragOffset.value.y
  
  // 边界限制
  const maxX = window.innerWidth - 380
  const maxY = window.innerHeight - 560
  newX = Math.max(0, Math.min(newX, maxX))
  newY = Math.max(0, Math.min(newY, maxY))
  
  position.value = { x: newX, y: newY }
}

/**
 * 停止拖动
 */
function stopDrag() {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 快捷问题（根据是否有题目上下文动态调整）
const quickQuestions = computed(() => {
  if (props.questionContext) {
    return [
      '这道题怎么做？',
      '帮我分析一下选项',
      '这个知识点怎么理解？',
      '为什么不选其他选项？'
    ]
  }
  return [
    '这道题怎么做？',
    '帮我分析一下选项',
    '这个知识点怎么理解？',
    '有什么解题技巧吗？'
  ]
})

/**
 * 切换聊天窗口
 */
function toggleChat() {
  isExpanded.value = !isExpanded.value
  if (!isExpanded.value) {
    isFullscreen.value = false
  }
}

/**
 * 切换全屏模式
 */
function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
}

/**
 * 关闭聊天窗口
 */
function closeChat() {
  isExpanded.value = false
  emit('close')
}

/**
 * 清空对话
 */
function clearChat() {
  messages.value = []
}

/**
 * 发送快捷问题
 */
function sendQuickQuestion(question) {
  inputMessage.value = question
  sendMessage()
}

/**
 * 发送消息
 */
async function sendMessage() {
  const message = inputMessage.value.trim()
  if (!message || isLoading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: message,
    timestamp: new Date()
  })

  inputMessage.value = ''
  isLoading.value = true

  // 滚动到底部
  await nextTick()
  scrollToBottom()

  try {
    // 调用 AI 接口
    const response = await sendAIChat({
      message,
      history: messages.value.slice(-10), // 最近10条对话作为上下文
      context: props.questionContext
    })

    if (response.success && response.data) {
      // 添加 AI 回复
      messages.value.push({
        role: 'assistant',
        content: response.data.message,
        timestamp: new Date(response.data.timestamp)
      })
    } else {
      throw new Error('AI 回复失败')
    }
  } catch (error) {
    console.error('AI 聊天错误:', error)
    messages.value.push({
      role: 'assistant',
      content: '抱歉，我暂时无法回答这个问题。请稍后再试，或者换一种方式提问。',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
    await nextTick()
    scrollToBottom()
  }
}

/**
 * 格式化消息（支持 Markdown）
 */
function formatMessage(content) {
  if (!content) return ''
  try {
    // 配置 marked
    marked.setOptions({
      breaks: true,
      gfm: true
    })
    return marked.parse(content)
  } catch {
    return content.replace(/\n/g, '<br>')
  }
}

/**
 * 格式化时间
 */
function formatTime(date) {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 滚动到底部
 */
function scrollToBottom() {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// 监听题目上下文变化
watch(() => props.questionContext, (newContext) => {
  if (newContext && isExpanded.value) {
    // 可以自动发送一条关于当前题目的消息
  }
})

// 清理事件监听器
onUnmounted(() => {
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
  document.removeEventListener('mousemove', onDragFab)
  document.removeEventListener('mouseup', stopDragFab)
})

// 暴露方法
defineExpose({
  toggleChat,
  closeChat,
  clearChat,
  sendQuickQuestion
})
</script>

<style scoped>
.ai-chat-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 1000;
}

/* 拖动状态 */
.ai-chat-container.is-dragging {
  user-select: none;
}

.ai-chat-container.is-dragging * {
  user-select: none;
}

/* 悬浮按钮 */
.chat-fab {
  position: relative;
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
}

.ai-chat-container.is-dragging .chat-fab {
  cursor: grabbing;
  transition: none;
}

.chat-fab:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
}

.ai-chat-container.is-dragging .chat-fab:hover {
  transform: none;
}

.fab-icon {
  color: white;
  z-index: 2;
}

.fab-pulse {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  animation: pulse 2s ease-out infinite;
}

@keyframes pulse {
  0% { transform: scale(1); opacity: 0.5; }
  100% { transform: scale(1.5); opacity: 0; }
}

.fab-label {
  position: absolute;
  right: 70px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  white-space: nowrap;
  opacity: 0;
  transform: translateX(10px);
  transition: all 0.3s ease;
  pointer-events: none;
}

.chat-fab:hover .fab-label {
  opacity: 1;
  transform: translateX(0);
}

/* 聊天窗口 */
.chat-window {
  width: 380px;
  height: 560px;
  background: #1e1e2d;
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

/* 全屏模式 */
.ai-chat-container.is-fullscreen {
  bottom: 0;
  right: 0;
  top: 0;
  left: 0;
  padding: 20px;
}

.ai-chat-container.is-fullscreen .chat-window {
  width: 100%;
  height: 100%;
  max-width: 900px;
  max-height: 100%;
  margin: 0 auto;
  border-radius: 20px;
}

/* 头部 */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* 可拖动的头部 */
.chat-header.draggable {
  cursor: grab;
}

.chat-header.draggable:active {
  cursor: grabbing;
}

.ai-chat-container.is-dragging .chat-header {
  cursor: grabbing;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-text h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.status-dot {
  width: 8px;
  height: 8px;
  background: #10b981;
  border-radius: 50%;
  animation: blink 2s ease-in-out infinite;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-icon:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

/* 消息列表 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

/* 欢迎消息 */
.welcome-message {
  text-align: center;
  padding: 20px;
}

.welcome-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a78bfa;
}

.welcome-message h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: white;
}

.welcome-message p {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.quick-question {
  padding: 8px 14px;
  background: rgba(102, 126, 234, 0.2);
  border: 1px solid rgba(102, 126, 234, 0.3);
  border-radius: 20px;
  font-size: 13px;
  color: #a78bfa;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-question:hover {
  background: rgba(102, 126, 234, 0.3);
  transform: translateY(-2px);
}

/* 消息项 */
.message-item {
  display: flex;
  gap: 10px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-item.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-item.assistant .message-avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.message-item.user .message-avatar {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
}

.message-content {
  max-width: 75%;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.message-item.assistant .message-bubble {
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.9);
  border-bottom-left-radius: 4px;
}

.message-item.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message-bubble :deep(p) {
  margin: 0 0 8px 0;
}

.message-bubble :deep(p:last-child) {
  margin-bottom: 0;
}

.message-bubble :deep(strong) {
  color: #a78bfa;
}

.message-bubble :deep(ul), 
.message-bubble :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.message-bubble :deep(li) {
  margin: 4px 0;
}

.message-bubble :deep(code) {
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.message-time {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  margin-top: 4px;
  padding: 0 4px;
}

.message-item.user .message-time {
  text-align: right;
}

/* 打字动画 */
.message-bubble.typing {
  display: flex;
  gap: 4px;
  padding: 16px 20px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  animation: typing 1.4s ease-in-out infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-8px); }
}

/* 输入区域 */
.chat-input {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.2);
}

.input-wrapper {
  flex: 1;
}

.input-wrapper :deep(.el-textarea__inner) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  resize: none;
  padding: 10px 14px;
}

.input-wrapper :deep(.el-textarea__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.input-wrapper :deep(.el-textarea__inner:focus) {
  border-color: #667eea;
}

.chat-input :deep(.el-button) {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.chat-input :deep(.el-button:hover) {
  opacity: 0.9;
}

.chat-input :deep(.el-button:disabled) {
  opacity: 0.5;
}

/* 底部提示 */
.chat-footer {
  padding: 8px 20px;
  text-align: center;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.4);
  background: rgba(0, 0, 0, 0.1);
}

/* 动画 */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.3s ease;
}

.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(20px) scale(0.95);
}

/* 响应式 */
@media (max-width: 480px) {
  .ai-chat-container {
    bottom: 16px;
    right: 16px;
  }
  
  .chat-window {
    width: calc(100vw - 32px);
    height: calc(100vh - 100px);
    max-height: 600px;
  }
  
  .fab-label {
    display: none;
  }
}
</style>
