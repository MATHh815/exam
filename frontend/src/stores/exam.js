/**
 * 考试状态管理 Store
 * 
 * 管理考试会话、答案临时存储、考试状态等
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  startExam, 
  submitAnswer, 
  submitExam,
  getExamResult,
  saveProgress as saveProgressApi,
  pauseExam as pauseExamApi,
  resumeExam as resumeExamApi
} from '../api/exams'

export const useExamStore = defineStore('exam', () => {
  // 状态
  const currentSession = ref(null) // 当前考试会话
  const currentPaper = ref(null) // 当前试卷信息
  const answers = ref({}) // 临时答案存储 { questionId: answer }
  const examStatus = ref('idle') // 考试状态: idle, in_progress, submitting, completed, paused
  const examResult = ref(null) // 考试结果
  const startTime = ref(null) // 考试开始时间
  const endTime = ref(null) // 考试结束时间
  const timeRemaining = ref(0) // 剩余时间（秒）
  const autoSaveStatus = ref('saved') // 自动保存状态: saved, saving, error
  const currentQuestionIndex = ref(0) // 当前题目索引

  // 计算属性
  const isExamInProgress = computed(() => examStatus.value === 'in_progress' || examStatus.value === 'paused')
  const isExamCompleted = computed(() => examStatus.value === 'completed')
  const isExamPaused = computed(() => examStatus.value === 'paused')
  const hasAnswers = computed(() => Object.keys(answers.value).length > 0)
  const answeredCount = computed(() => Object.keys(answers.value).length)
  const totalQuestions = computed(() => {
    return currentPaper.value?.questions?.length || 0
  })
  const progress = computed(() => {
    if (totalQuestions.value === 0) return 0
    return Math.round((answeredCount.value / totalQuestions.value) * 100)
  })

  /**
   * 开始考试
   * @param {number} paperId - 试卷ID
   * @param {Object} paperData - 试卷数据（包含题目）
   * @param {number|Object} sessionIdOrData - 会话ID或完整会话数据（可选，如果已创建）
   */
  async function beginExam(paperId, paperData, sessionIdOrData = null) {
    try {
      let session
      
      if (sessionIdOrData) {
        // 如果传入的是完整的会话对象
        if (typeof sessionIdOrData === 'object' && sessionIdOrData.end_time) {
          session = sessionIdOrData
        } else {
          // 如果只传入了 sessionId，从后端获取会话信息
          const { getCurrentSession } = await import('../api/exams')
          const sessionResponse = await getCurrentSession(paperId)
          
          if (sessionResponse.success && sessionResponse.data) {
            session = sessionResponse.data
          } else {
            // 如果获取失败，使用试卷时长构建本地会话
            const now = new Date()
            const endTimeDate = new Date(now.getTime() + paperData.duration * 60 * 1000)
            
            session = {
              id: typeof sessionIdOrData === 'object' ? sessionIdOrData.id : sessionIdOrData,
              user_id: null,
              paper_id: paperId,
              start_time: now.toISOString(),
              end_time: endTimeDate.toISOString(),
              status: 'in_progress',
              answers: {}
            }
          }
        }
      } else {
        // 调用 API 创建考试会话
        const response = await startExam(paperId)
        
        if (response.success) {
          session = response.data
        } else {
          throw new Error(response.error?.message || '开始考试失败')
        }
      }
      
      currentSession.value = session
      currentPaper.value = paperData
      answers.value = session.answers || {}
      examStatus.value = 'in_progress'
      startTime.value = session.start_time ? new Date(session.start_time) : new Date()
      currentQuestionIndex.value = session.current_question_index || 0
      
      // 计算结束时间和剩余时间
      // 注意：后端返回的是 UTC 时间，需要正确处理
      if (session.end_time) {
        // 解析 ISO 时间字符串（自动处理时区）
        endTime.value = new Date(session.end_time)
        const now = new Date()
        const remaining = Math.floor((endTime.value.getTime() - now.getTime()) / 1000)
        timeRemaining.value = Math.max(0, remaining)
        console.log('[ExamStore] 计算剩余时间:', {
          endTime: session.end_time,
          endTimeLocal: endTime.value.toLocaleString(),
          now: now.toLocaleString(),
          remaining: remaining
        })
      } else if (paperData.duration) {
        // 如果没有 end_time，使用试卷时长计算
        endTime.value = new Date(startTime.value.getTime() + paperData.duration * 60 * 1000)
        timeRemaining.value = paperData.duration * 60
        console.log('[ExamStore] 使用试卷时长:', paperData.duration, '分钟')
      }
      
      return { success: true, session: currentSession.value }
    } catch (error) {
      console.error('开始考试失败:', error)
      throw error
    }
  }

  /**
   * 恢复进行中的考试
   * @param {Object} session - 考试会话数据
   * @param {Object} paperData - 试卷数据（包含题目）
   */
  async function resumeExam(session, paperData) {
    try {
      currentSession.value = session
      currentPaper.value = paperData
      answers.value = session.answers || {}
      examStatus.value = session.status === 'paused' ? 'paused' : 'in_progress'
      startTime.value = new Date(session.start_time)
      endTime.value = new Date(session.end_time)
      currentQuestionIndex.value = session.current_question_index || 0
      
      // 计算剩余时间
      const now = new Date()
      const remaining = Math.floor((endTime.value.getTime() - now.getTime()) / 1000)
      timeRemaining.value = Math.max(0, remaining)
      
      console.log('[ExamStore] 恢复考试，剩余时间:', {
        endTime: session.end_time,
        endTimeLocal: endTime.value.toLocaleString(),
        now: now.toLocaleString(),
        remaining: remaining
      })
      
      return { success: true, session: currentSession.value }
    } catch (error) {
      console.error('恢复考试失败:', error)
      throw error
    }
  }

  /**
   * 保存答案到本地
   * @param {number} questionId - 题目ID
   * @param {string} answer - 答案
   */
  function saveAnswerLocally(questionId, answer) {
    answers.value[questionId] = answer
  }

  /**
   * 提交单题答案到服务器
   * @param {number} questionId - 题目ID
   * @param {string} answer - 答案
   * @param {number} questionIndex - 当前题目索引（可选）
   */
  async function saveAnswerToServer(questionId, answer, questionIndex = null) {
    if (!currentSession.value) {
      throw new Error('没有活动的考试会话')
    }

    try {
      autoSaveStatus.value = 'saving'
      
      const data = {
        question_id: questionId,
        answer: answer
      }
      
      // 如果提供了题目索引，一起保存
      if (questionIndex !== null) {
        data.question_index = questionIndex
      }
      
      const response = await submitAnswer(currentSession.value.id, data)
      
      if (response.success) {
        autoSaveStatus.value = 'saved'
        // 同时保存到本地
        saveAnswerLocally(questionId, answer)
        return { success: true }
      } else {
        autoSaveStatus.value = 'error'
        throw new Error(response.error?.message || '保存答案失败')
      }
    } catch (error) {
      autoSaveStatus.value = 'error'
      console.error('保存答案失败:', error)
      // 即使服务器保存失败，也保存到本地
      saveAnswerLocally(questionId, answer)
      throw error
    }
  }

  /**
   * 保存当前题目进度到服务器
   * @param {number} questionIndex - 当前题目索引
   */
  async function saveProgressToServer(questionIndex) {
    if (!currentSession.value) {
      return
    }

    try {
      currentQuestionIndex.value = questionIndex
      await saveProgressApi(currentSession.value.id, questionIndex)
    } catch (error) {
      console.error('保存进度失败:', error)
      // 进度保存失败不影响用户操作
    }
  }

  /**
   * 暂停考试
   */
  async function pauseCurrentExam() {
    if (!currentSession.value) {
      throw new Error('没有活动的考试会话')
    }

    try {
      const response = await pauseExamApi(currentSession.value.id)
      
      if (response.success) {
        examStatus.value = 'paused'
        return { success: true }
      } else {
        throw new Error(response.error?.message || '暂停考试失败')
      }
    } catch (error) {
      console.error('暂停考试失败:', error)
      throw error
    }
  }

  /**
   * 恢复暂停的考试
   */
  async function resumeCurrentExam() {
    if (!currentSession.value) {
      throw new Error('没有活动的考试会话')
    }

    try {
      const response = await resumeExamApi(currentSession.value.id)
      
      if (response.success) {
        examStatus.value = 'in_progress'
        return { success: true }
      } else {
        throw new Error(response.error?.message || '恢复考试失败')
      }
    } catch (error) {
      console.error('恢复考试失败:', error)
      throw error
    }
  }

  /**
   * 提交整份试卷
   */
  async function finishExam() {
    if (!currentSession.value) {
      throw new Error('没有活动的考试会话')
    }

    try {
      examStatus.value = 'submitting'
      
      const response = await submitExam(currentSession.value.id)
      
      if (response.success) {
        examStatus.value = 'completed'
        examResult.value = response.data
        return { success: true, result: response.data }
      } else {
        examStatus.value = 'in_progress'
        throw new Error(response.error?.message || '提交试卷失败')
      }
    } catch (error) {
      examStatus.value = 'in_progress'
      console.error('提交试卷失败:', error)
      throw error
    }
  }

  /**
   * 获取考试结果
   * @param {number} resultId - 结果ID
   */
  async function fetchExamResult(resultId) {
    try {
      const response = await getExamResult(resultId, true)
      
      if (response.success) {
        examResult.value = response.data
        return { success: true, result: response.data }
      } else {
        throw new Error(response.error?.message || '获取考试结果失败')
      }
    } catch (error) {
      console.error('获取考试结果失败:', error)
      throw error
    }
  }

  /**
   * 更新剩余时间
   * @param {number} seconds - 剩余秒数
   */
  function updateTimeRemaining(seconds) {
    timeRemaining.value = seconds
  }

  /**
   * 检查是否超时
   */
  function checkTimeout() {
    if (endTime.value && new Date() >= endTime.value) {
      return true
    }
    return false
  }

  /**
   * 获取指定题目的答案
   * @param {number} questionId - 题目ID
   */
  function getAnswer(questionId) {
    return answers.value[questionId] ?? null
  }

  /**
   * 清除考试状态
   */
  function clearExamState() {
    currentSession.value = null
    currentPaper.value = null
    answers.value = {}
    examStatus.value = 'idle'
    examResult.value = null
    startTime.value = null
    endTime.value = null
    timeRemaining.value = 0
    autoSaveStatus.value = 'saved'
    currentQuestionIndex.value = 0
  }

  /**
   * 重置到初始状态
   */
  function reset() {
    clearExamState()
  }

  return {
    // 状态
    currentSession,
    currentPaper,
    answers,
    examStatus,
    examResult,
    startTime,
    endTime,
    timeRemaining,
    autoSaveStatus,
    currentQuestionIndex,
    
    // 计算属性
    isExamInProgress,
    isExamCompleted,
    isExamPaused,
    hasAnswers,
    answeredCount,
    totalQuestions,
    progress,
    
    // 方法
    beginExam,
    resumeExam,
    saveAnswerLocally,
    saveAnswerToServer,
    saveProgressToServer,
    pauseCurrentExam,
    resumeCurrentExam,
    finishExam,
    fetchExamResult,
    updateTimeRemaining,
    checkTimeout,
    getAnswer,
    clearExamState,
    reset
  }
})
