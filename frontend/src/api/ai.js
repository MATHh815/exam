/**
 * AI 智能服务 API
 * 
 * 包含以下功能：
 * - AI 智能分析
 * - AI 智能解答（类似 GPT 对话）
 * - 学习计划生成
 */

import request from '../utils/request'

// ============ AI 配置 ============
// TODO: 后续替换为真实的 AI 接口地址
const AI_CONFIG = {
  // AI 聊天接口地址（预留，后续替换）
  chatEndpoint: '/ai/chat',
  // AI 分析接口地址
  analysisEndpoint: '/ai/analysis',
  // 学习计划生成接口
  studyPlanEndpoint: '/ai/study-plan',
  // 是否使用模拟数据（开发阶段使用）
  useMock: true
}

/**
 * 获取 AI 智能分析
 * @param {Object} params - 分析参数
 * @param {number} params.days - 分析天数范围
 * @returns {Promise}
 */
export function getAIAnalysis(params = {}) {
  if (AI_CONFIG.useMock) {
    return Promise.resolve({ success: true, data: null })
  }
  
  return request({
    url: AI_CONFIG.analysisEndpoint,
    method: 'post',
    data: params
  })
}

/**
 * 生成学习计划
 * @param {Object} params - 计划参数
 * @param {Array} params.weaknesses - 薄弱知识点
 * @param {number} params.days - 计划天数
 * @returns {Promise}
 */
export function generateStudyPlan(params = {}) {
  if (AI_CONFIG.useMock) {
    return Promise.resolve({ success: true, data: { studyPlan: [] } })
  }
  
  return request({
    url: AI_CONFIG.studyPlanEndpoint,
    method: 'post',
    data: params
  })
}

/**
 * AI 智能解答（聊天接口）
 * @param {Object} params - 聊天参数
 * @param {string} params.message - 用户消息
 * @param {Array} params.history - 历史对话记录
 * @param {Object} params.context - 上下文信息（如当前题目）
 * @returns {Promise}
 */
export function sendAIChat(params = {}) {
  if (AI_CONFIG.useMock) {
    // 模拟 AI 回复
    return mockAIResponse(params)
  }
  
  return request({
    url: AI_CONFIG.chatEndpoint,
    method: 'post',
    data: params
  })
}

/**
 * 模拟 AI 回复（开发阶段使用）
 * @param {Object} params - 聊天参数
 * @returns {Promise}
 */
function mockAIResponse(params) {
  return new Promise((resolve) => {
    // 模拟网络延迟
    const delay = 500 + Math.random() * 1500
    
    setTimeout(() => {
      const message = params.message || ''
      const context = params.context
      let response = ''
      
      // 根据问题类型生成不同的模拟回复
      if (message.includes('解释') || message.includes('什么是') || message.includes('是什么')) {
        response = generateExplanationResponse(message, context)
      } else if (message.includes('怎么做') || message.includes('如何') || message.includes('方法') || message.includes('这道题')) {
        response = generateMethodResponse(message, context)
      } else if (message.includes('答案') || message.includes('选') || message.includes('哪个')) {
        response = generateAnswerResponse(message, context)
      } else if (message.includes('错') || message.includes('为什么')) {
        response = generateWhyResponse(message, context)
      } else if (message.includes('分析') || message.includes('选项')) {
        response = generateOptionsAnalysis(message, context)
      } else if (message.includes('知识点') || message.includes('考点')) {
        response = generateKnowledgePointResponse(message, context)
      } else {
        response = generateGeneralResponse(message, context)
      }
      
      resolve({
        success: true,
        data: {
          message: response,
          timestamp: new Date().toISOString()
        }
      })
    }, delay)
  })
}

/**
 * 生成解释类回复
 */
function generateExplanationResponse(message, context) {
  // 如果有题目上下文，结合题目生成解释
  if (context && context.question) {
    const q = context.question
    return `好的，让我来为你解释第 ${context.questionNumber} 题涉及的知识点。\n\n**题目类型**：${getQuestionTypeLabel(q.type)}\n**难度等级**：${getDifficultyLabel(q.difficulty)}\n\n**核心概念**：\n这道题主要考查的是基础理论知识的理解和应用。\n\n**关键要点**：\n1. 理解题目中的核心概念\n2. 注意区分相似概念的区别\n3. 结合实际情境进行分析\n\n**学习建议**：\n- 多做同类型的练习题\n- 整理相关知识点的笔记\n- 注意总结常见的考点\n\n还有什么不清楚的地方吗？`
  }
  
  const explanations = [
    `好的，让我来为你解释一下。\n\n这个概念的核心要点是：\n\n1. **基本定义**：这是一个在考试中经常出现的知识点，理解它的本质含义非常重要。\n\n2. **关键特征**：需要注意区分它与相似概念的区别，避免混淆。\n\n3. **实际应用**：在解题时，要结合具体情境来分析。\n\n如果还有不清楚的地方，可以继续问我！`,
    `这是一个很好的问题！\n\n简单来说：\n\n**核心概念**：这个知识点主要涉及到基础理论的应用。\n\n**记忆技巧**：可以通过联想记忆法来加深印象。\n\n**常见考点**：\n- 概念辨析\n- 实际应用\n- 综合分析\n\n希望这个解释对你有帮助！`,
    `让我详细解释一下这个问题。\n\n**首先**，我们需要理解基本概念。\n\n**其次**，要掌握其核心特点：\n1. 特点一：具有明确的定义和范围\n2. 特点二：与其他概念有明显区别\n3. 特点三：在实际中有广泛应用\n\n**最后**，建议多做相关练习题来巩固理解。\n\n还有什么疑问吗？`
  ]
  return explanations[Math.floor(Math.random() * explanations.length)]
}

/**
 * 生成方法类回复
 */
function generateMethodResponse(message, context) {
  // 如果有题目上下文，针对具体题目给出方法
  if (context && context.question) {
    const q = context.question
    const questionNum = context.questionNumber
    
    return `针对第 ${questionNum} 题，我推荐以下解题方法：\n\n**题目类型**：${getQuestionTypeLabel(q.type)}\n\n**解题步骤**：\n\n📝 **第一步：审题**\n仔细阅读题目，找出关键信息和限定条件。\n\n📝 **第二步：分析选项**\n${q.options ? `这道题有 ${q.options.length} 个选项，我们需要：\n- 排除明显错误的选项\n- 对比相似选项的区别\n- 找出最符合题意的答案` : '根据题目要求进行分析'}\n\n📝 **第三步：验证答案**\n选择答案后，再检查一遍是否符合题目要求。\n\n**小技巧**：\n- 注意题目中的"绝对词"（如"一定"、"必须"等）\n- 遇到不确定的选项，可以用排除法\n- 相信第一直觉，不要轻易改答案\n\n需要我帮你分析具体的选项吗？`
  }
  
  const methods = [
    `这类题目有一个很好的解题思路：\n\n**第一步**：仔细审题，找出关键信息\n- 标记题目中的关键词\n- 理解题目要求\n\n**第二步**：分析选项\n- 排除明显错误的选项\n- 对比相似选项的区别\n\n**第三步**：验证答案\n- 将选择的答案代入题目验证\n- 确保逻辑自洽\n\n**小技巧**：遇到不确定的题目，可以用排除法缩小范围。`,
    `解决这类问题，我推荐以下方法：\n\n📝 **方法一：直接法**\n根据已知条件直接推导答案\n\n📝 **方法二：排除法**\n逐一排除不符合条件的选项\n\n📝 **方法三：代入法**\n将选项代入题目验证\n\n💡 **注意事项**：\n- 注意题目中的限定词\n- 不要遗漏隐含条件\n- 检查答案的合理性`,
    `针对这个问题，建议按以下步骤来做：\n\n**1. 理解题意** 🎯\n确保完全理解题目在问什么\n\n**2. 提取信息** 📋\n找出所有有用的已知条件\n\n**3. 建立联系** 🔗\n将已知条件与所学知识联系起来\n\n**4. 得出结论** ✅\n根据分析得出最终答案\n\n多练习几道类似的题目，你会越来越熟练的！`
  ]
  return methods[Math.floor(Math.random() * methods.length)]
}

/**
 * 生成答案类回复
 */
function generateAnswerResponse(message, context) {
  if (context && context.question) {
    const q = context.question
    const questionNum = context.questionNumber || ''
    const optionsText = q.options ? q.options.map((opt, i) => {
      const letter = String.fromCharCode(65 + i)
      return `${letter}. ${opt}`
    }).join('\n') : ''
    
    return `好的，让我来帮你分析第 ${questionNum} 题：\n\n**题目内容**：\n${q.content || '（题目内容）'}\n\n${optionsText ? `**选项**：\n${optionsText}\n\n` : ''}**解题思路**：\n1. 首先，我们需要理解题目的核心考点\n2. 然后，逐一分析各个选项的正确性\n3. 最后，找出最符合题意的答案\n\n**分析**：\n这道题主要考查的是对基础概念的理解和应用能力。建议你：\n- 仔细阅读题目，找出关键词\n- 排除明显错误的选项\n- 对比相似选项的区别\n\n如果你想了解具体某个选项为什么对或错，可以继续问我！`
  }
  
  return `关于这道题的答案：\n\n我建议你按以下步骤来分析：\n\n1. **审题**：仔细阅读题目，找出关键信息\n2. **分析**：对比各个选项的区别\n3. **验证**：选择后再检查一遍\n\n如果你能把具体的题目内容发给我，我可以给你更详细的解答！`
}

/**
 * 生成原因类回复
 */
function generateWhyResponse(message, context) {
  // 如果有题目上下文
  if (context && context.question) {
    return `让我帮你分析一下第 ${context.questionNumber} 题可能出错的原因：\n\n🔍 **常见错误原因**：\n\n1. **概念混淆**\n   - 相似概念没有区分清楚\n   - 建议：制作对比表格，明确区别\n\n2. **审题不仔细**\n   - 忽略了题目中的关键词或限定条件\n   - 建议：标记关键词，多读几遍题目\n\n3. **知识点遗忘**\n   - 相关知识点记忆不牢固\n   - 建议：复习相关章节，做好笔记\n\n**针对这道题的建议**：\n- 重新阅读题目，找出关键信息\n- 逐一分析每个选项\n- 把这道题加入错题本，定期复习\n\n💪 错误是学习的机会，分析清楚原因后，下次就不会再犯了！`
  }
  
  const whyResponses = [
    `这是一个很好的问题，让我来分析一下原因：\n\n**主要原因**：\n1. 概念理解不够深入\n2. 容易混淆相似的知识点\n3. 审题时遗漏了关键信息\n\n**改进建议**：\n- 加强基础概念的学习\n- 多做对比分析练习\n- 养成仔细审题的习惯\n\n**记忆口诀**：\n"审题要细心，概念要清晰，选项要对比，答案要验证"\n\n继续加油！`,
    `让我帮你分析一下为什么会出错：\n\n🔍 **可能的原因**：\n\n1. **知识点混淆**\n   - 相似概念没有区分清楚\n   - 建议：制作对比表格\n\n2. **审题不仔细**\n   - 忽略了题目中的限定词\n   - 建议：标记关键词\n\n3. **解题方法不当**\n   - 没有使用最优解法\n   - 建议：总结常用解题技巧\n\n💪 错误是学习的机会，分析清楚原因后，下次就不会再犯了！`,
    `分析错误原因是提高的关键！\n\n**错误类型分析**：\n\n📌 **概念性错误**\n对基本概念理解有偏差\n→ 建议重新学习相关知识点\n\n📌 **计算性错误**\n计算过程中出现失误\n→ 建议养成验算习惯\n\n📌 **理解性错误**\n对题目理解不准确\n→ 建议多做审题训练\n\n**下一步行动**：\n把这道错题加入错题本，定期复习！`
  ]
  return whyResponses[Math.floor(Math.random() * whyResponses.length)]
}

/**
 * 生成选项分析回复
 */
function generateOptionsAnalysis(message, context) {
  if (context && context.question && context.question.options) {
    const q = context.question
    const options = q.options
    
    let analysisText = `好的，让我来帮你分析第 ${context.questionNumber} 题的各个选项：\n\n**题目**：${q.content}\n\n**选项分析**：\n\n`
    
    options.forEach((opt, i) => {
      const letter = String.fromCharCode(65 + i)
      analysisText += `**${letter}. ${opt}**\n`
      analysisText += `分析：这个选项需要结合题目要求来判断。注意关键词和限定条件。\n\n`
    })
    
    analysisText += `**解题建议**：\n1. 先排除明显错误的选项\n2. 对比剩余选项的区别\n3. 选择最符合题意的答案\n\n你觉得哪个选项最可能是正确答案？我们可以一起讨论！`
    
    return analysisText
  }
  
  return `要分析选项，我需要知道具体的题目内容。\n\n你可以：\n1. 直接告诉我题目和选项\n2. 或者在考试界面中，我会自动获取当前题目的信息\n\n这样我就能给你更准确的分析了！`
}

/**
 * 生成知识点回复
 */
function generateKnowledgePointResponse(message, context) {
  if (context && context.question) {
    const q = context.question
    const examType = context.examType
    
    let examTypeText = ''
    if (examType === 'civil_service') {
      examTypeText = '公务员考试'
    } else if (examType === 'postgraduate') {
      examTypeText = '研究生考试'
    } else if (examType === 'public_institution') {
      examTypeText = '事业编考试'
    }
    
    return `关于第 ${context.questionNumber} 题涉及的知识点：\n\n**考试类型**：${examTypeText || '综合考试'}\n**题目类型**：${getQuestionTypeLabel(q.type)}\n**难度等级**：${getDifficultyLabel(q.difficulty)}\n\n**核心知识点**：\n这道题主要考查的是基础理论知识的理解和应用能力。\n\n**相关考点**：\n1. 基本概念的理解\n2. 概念之间的区别与联系\n3. 实际应用场景分析\n\n**学习建议**：\n- 📚 系统复习相关章节\n- 📝 整理知识点笔记\n- 🔄 多做同类型练习题\n- 💡 总结常见的出题规律\n\n需要我详细解释某个知识点吗？`
  }
  
  return `关于知识点的问题，我可以帮你：\n\n1. **解释概念**：告诉我你想了解的知识点\n2. **分析考点**：结合具体题目分析考查重点\n3. **学习建议**：提供针对性的复习方法\n\n你想了解哪方面的知识点呢？`
}

/**
 * 生成通用回复
 */
function generateGeneralResponse(message, context) {
  // 如果有题目上下文，提供更针对性的回复
  if (context && context.question) {
    return `收到你的问题了！\n\n我看到你正在做第 ${context.questionNumber} 题（共 ${context.totalQuestions} 题）。\n\n作为你的 AI 学习助手，我可以帮你：\n\n📚 **针对当前题目**\n- 分析题目思路\n- 解释各个选项\n- 讲解相关知识点\n\n📝 **学习建议**\n- 提供解题技巧\n- 分析错误原因\n- 推荐复习方向\n\n你可以直接问我：\n- "这道题怎么做？"\n- "帮我分析一下选项"\n- "这个知识点怎么理解？"\n\n有什么我可以帮助你的吗？`
  }
  
  const generalResponses = [
    `收到你的问题了！\n\n作为你的 AI 学习助手，我可以帮你：\n\n📚 **解答疑问**\n- 解释知识点概念\n- 分析题目思路\n- 提供解题方法\n\n📝 **学习建议**\n- 制定学习计划\n- 推荐练习方向\n- 分析薄弱环节\n\n请告诉我你具体想了解什么，我会尽力帮助你！`,
    `你好！我是你的 AI 学习助手 🤖\n\n我可以帮你：\n1. 解答考试相关问题\n2. 分析错题原因\n3. 提供学习建议\n4. 解释知识点\n\n有什么我可以帮助你的吗？`,
    `感谢你的提问！\n\n为了更好地帮助你，你可以：\n\n✨ **直接问我**：\n- "这道题怎么做？"\n- "为什么选 A 不选 B？"\n- "这个概念是什么意思？"\n\n✨ **发送题目**：\n把不会的题目内容发给我，我来帮你分析\n\n期待你的问题！`
  ]
  return generalResponses[Math.floor(Math.random() * generalResponses.length)]
}

// ============ 辅助函数 ============

/**
 * 获取题目类型标签
 */
function getQuestionTypeLabel(type) {
  const typeMap = {
    'single_choice': '单选题',
    'multiple_choice': '多选题',
    'true_false': '判断题',
    'fill_blank': '填空题',
    'essay': '问答题'
  }
  return typeMap[type] || '选择题'
}

/**
 * 获取难度标签
 */
function getDifficultyLabel(difficulty) {
  const difficultyMap = {
    'easy': '简单 ⭐',
    'medium': '中等 ⭐⭐',
    'hard': '困难 ⭐⭐⭐'
  }
  return difficultyMap[difficulty] || '中等'
}

export default {
  getAIAnalysis,
  generateStudyPlan,
  sendAIChat,
  AI_CONFIG
}
