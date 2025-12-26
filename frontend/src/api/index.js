/**
 * API 接口统一导出
 * 
 * 各个模块的 API 将在后续任务中实现：
 * - auth.js (任务 20.1): 认证相关接口（登录、注册、用户信息）✓
 * - questions.js (任务 21.1): 题库相关接口
 * - practice.js (任务 22.1): 练习相关接口
 * - exams.js (任务 23.1): 考试相关接口
 * - statistics.js (任务 25.1): 统计相关接口
 */

// 导出认证相关 API
export * from './auth'

// 导出题库相关 API
export * from './questions'

// 导出考试相关 API
export * from './exams'

// 导出练习相关 API
export * from './practice'

// 导出统计相关 API
export * from './statistics'
