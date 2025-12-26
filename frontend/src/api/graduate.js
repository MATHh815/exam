/**
 * 考研院校信息API
 */
import request from '../utils/request'

// ============ AI 智能推荐配置 ============
// TODO: 后续替换为真实的 AI 接口地址
const AI_GRADUATE_CONFIG = {
  // AI 院校推荐接口地址（预留）
  recommendEndpoint: '/ai/graduate/recommend',
  // AI 择校分析接口地址（预留）
  analysisEndpoint: '/ai/graduate/analysis',
  // AI 备考建议接口地址（预留）
  adviceEndpoint: '/ai/graduate/advice',
  // 是否使用模拟数据（开发阶段使用）
  useMock: true
}

/**
 * AI 智能院校推荐
 * @param {Object} params - 推荐参数
 * @param {number} params.total_score - 总分
 * @param {number} params.politics_score - 政治分数
 * @param {number} params.english_score - 英语分数
 * @param {number} params.math_score - 数学分数
 * @param {number} params.professional_score - 专业课分数
 * @param {string} params.category - 学科门类
 * @param {string} params.province - 目标省份
 * @param {string} params.preference - 偏好（如：985优先、地域优先等）
 * @returns {Promise}
 */
export function getAIRecommendation(params = {}) {
  if (AI_GRADUATE_CONFIG.useMock) {
    return mockAIRecommendation(params)
  }
  
  return request({
    url: AI_GRADUATE_CONFIG.recommendEndpoint,
    method: 'post',
    data: params
  })
}

/**
 * AI 择校分析
 * @param {Object} params - 分析参数
 * @param {number} params.school_id - 目标院校ID
 * @param {number} params.major_id - 目标专业ID
 * @param {Object} params.scores - 用户成绩
 * @returns {Promise}
 */
export function getAISchoolAnalysis(params = {}) {
  if (AI_GRADUATE_CONFIG.useMock) {
    return mockAISchoolAnalysis(params)
  }
  
  return request({
    url: AI_GRADUATE_CONFIG.analysisEndpoint,
    method: 'post',
    data: params
  })
}

/**
 * AI 备考建议
 * @param {Object} params - 参数
 * @param {Object} params.scores - 当前成绩
 * @param {Object} params.target - 目标院校/专业
 * @param {number} params.months - 备考月数
 * @returns {Promise}
 */
export function getAIStudyAdvice(params = {}) {
  if (AI_GRADUATE_CONFIG.useMock) {
    return mockAIStudyAdvice(params)
  }
  
  return request({
    url: AI_GRADUATE_CONFIG.adviceEndpoint,
    method: 'post',
    data: params
  })
}

/**
 * 模拟 AI 院校推荐
 */
function mockAIRecommendation(params) {
  return new Promise((resolve) => {
    setTimeout(() => {
      const score = params.total_score || 350
      resolve({
        success: true,
        data: {
          summary: `根据您的成绩（总分 ${score} 分），AI 为您分析了全国 ${score > 380 ? '985/211' : '双一流及普通'}院校的录取情况。`,
          recommendation: generateRecommendationText(params),
          confidence: score > 400 ? 85 : score > 350 ? 70 : 55,
          suggestions: [
            score > 380 ? '您的成绩较为优秀，可以冲刺顶尖院校' : '建议以稳妥院校为主，适当冲刺',
            '建议关注目标院校的调剂信息',
            '复试准备要提前开始，尤其是英语口语'
          ]
        }
      })
    }, 1500)
  })
}

/**
 * 生成推荐文本
 */
function generateRecommendationText(params) {
  const score = params.total_score || 350
  const category = params.category || '工学'
  const province = params.province || ''
  
  let text = `## 📊 AI 智能择校分析报告\n\n`
  text += `### 一、成绩评估\n`
  text += `您的总分 **${score}** 分，`
  
  if (score >= 400) {
    text += `属于高分段，在${category}类专业中具有较强竞争力。\n\n`
    text += `### 二、院校推荐策略\n`
    text += `- **冲刺目标**：清华、北大、复旦等顶尖985院校\n`
    text += `- **稳妥选择**：中上游985或顶尖211院校\n`
    text += `- **保底方案**：普通211或强势双一流院校\n\n`
  } else if (score >= 350) {
    text += `属于中等偏上水平，建议采取"稳中求进"策略。\n\n`
    text += `### 二、院校推荐策略\n`
    text += `- **冲刺目标**：中等985或顶尖211院校\n`
    text += `- **稳妥选择**：普通211或强势双一流院校\n`
    text += `- **保底方案**：普通双一流或省属重点院校\n\n`
  } else {
    text += `建议以稳妥为主，重点关注调剂机会。\n\n`
    text += `### 二、院校推荐策略\n`
    text += `- **冲刺目标**：普通211院校\n`
    text += `- **稳妥选择**：双一流或省属重点院校\n`
    text += `- **保底方案**：普通院校，关注调剂\n\n`
  }
  
  text += `### 三、备考建议\n`
  text += `1. **专业课**：${category}类专业课是拉分关键，建议重点突破\n`
  text += `2. **公共课**：政治英语要保证过线，争取高分\n`
  text += `3. **复试准备**：提前准备英语口语和专业面试\n`
  
  if (province) {
    text += `\n### 四、地域分析\n`
    text += `您选择的目标省份是 **${province}**，该地区院校竞争${['北京', '上海', '江苏', '浙江'].includes(province) ? '较为激烈' : '相对适中'}。\n`
  }
  
  text += `\n---\n*以上分析基于历年数据，仅供参考。实际录取情况请以各院校官方公布为准。*`
  
  return text
}

/**
 * 模拟 AI 择校分析
 */
function mockAISchoolAnalysis(params) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        success: true,
        data: {
          matchScore: Math.floor(Math.random() * 30) + 60,
          analysis: '根据您的成绩和目标院校历年录取数据分析，您有一定的录取机会。建议重点提升专业课成绩。',
          risks: ['竞争激烈', '复试比例较高'],
          advantages: ['成绩达到往年分数线', '专业课基础扎实']
        }
      })
    }, 1000)
  })
}

/**
 * 模拟 AI 备考建议
 */
function mockAIStudyAdvice(params) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        success: true,
        data: {
          plan: '建议制定详细的复习计划，每天保证8小时有效学习时间。',
          priorities: ['专业课强化', '英语阅读提升', '政治冲刺'],
          timeline: [
            { month: '1-3月', task: '基础阶段，夯实基础知识' },
            { month: '4-6月', task: '强化阶段，重点突破难点' },
            { month: '7-9月', task: '提高阶段，大量刷题' },
            { month: '10-12月', task: '冲刺阶段，模拟考试' }
          ]
        }
      })
    }, 1000)
  })
}

// 导出配置供外部使用
export { AI_GRADUATE_CONFIG }

// 获取院校列表
export function getSchools(params) {
  return request({
    url: '/graduate/schools',
    method: 'get',
    params
  })
}

// 获取院校详情
export function getSchoolDetail(schoolId) {
  return request({
    url: `/graduate/schools/${schoolId}`,
    method: 'get'
  })
}

// 获取院校的专业列表
export function getSchoolMajors(schoolId, params) {
  return request({
    url: `/graduate/schools/${schoolId}/majors`,
    method: 'get',
    params
  })
}

// 获取专业详情
export function getMajorDetail(majorId) {
  return request({
    url: `/graduate/majors/${majorId}`,
    method: 'get'
  })
}

// 获取专业的历年分数线
export function getMajorScoreLines(majorId) {
  return request({
    url: `/graduate/majors/${majorId}/score-lines`,
    method: 'get'
  })
}

// 获取专业的考试科目
export function getMajorExamSubjects(majorId, params) {
  return request({
    url: `/graduate/majors/${majorId}/exam-subjects`,
    method: 'get',
    params
  })
}

// 搜索分数线
export function searchScoreLines(params) {
  return request({
    url: '/graduate/score-lines/search',
    method: 'get',
    params
  })
}

// 获取省份列表
export function getProvinces() {
  return request({
    url: '/graduate/provinces',
    method: 'get'
  })
}

// 获取学科门类列表
export function getCategories() {
  return request({
    url: '/graduate/categories',
    method: 'get'
  })
}

// 分数估算
export function estimateScore(data) {
  return request({
    url: '/graduate/estimate-score',
    method: 'post',
    data
  })
}


// ============ 院校管理接口 ============

// 添加院校
export function createSchool(data) {
  return request({
    url: '/graduate/schools',
    method: 'post',
    data
  })
}

// 更新院校
export function updateSchool(schoolId, data) {
  return request({
    url: `/graduate/schools/${schoolId}`,
    method: 'put',
    data
  })
}

// 删除院校
export function deleteSchool(schoolId) {
  return request({
    url: `/graduate/schools/${schoolId}`,
    method: 'delete'
  })
}

// ============ 专业管理接口 ============

// 添加专业
export function createMajor(data) {
  return request({
    url: '/graduate/majors',
    method: 'post',
    data
  })
}

// 更新专业
export function updateMajor(majorId, data) {
  return request({
    url: `/graduate/majors/${majorId}`,
    method: 'put',
    data
  })
}

// 删除专业
export function deleteMajor(majorId) {
  return request({
    url: `/graduate/majors/${majorId}`,
    method: 'delete'
  })
}

// ============ 分数线管理接口 ============

// 添加分数线
export function createScoreLine(data) {
  return request({
    url: '/graduate/score-lines',
    method: 'post',
    data
  })
}

// 更新分数线
export function updateScoreLine(scoreLineId, data) {
  return request({
    url: `/graduate/score-lines/${scoreLineId}`,
    method: 'put',
    data
  })
}

// 删除分数线
export function deleteScoreLine(scoreLineId) {
  return request({
    url: `/graduate/score-lines/${scoreLineId}`,
    method: 'delete'
  })
}

// ============ 考试科目管理接口 ============

// 添加考试科目
export function createExamSubject(data) {
  return request({
    url: '/graduate/exam-subjects',
    method: 'post',
    data
  })
}

// 更新考试科目
export function updateExamSubject(subjectId, data) {
  return request({
    url: `/graduate/exam-subjects/${subjectId}`,
    method: 'put',
    data
  })
}

// 删除考试科目
export function deleteExamSubject(subjectId) {
  return request({
    url: `/graduate/exam-subjects/${subjectId}`,
    method: 'delete'
  })
}
