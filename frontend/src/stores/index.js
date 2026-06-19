/**
 * Pinia Stores 入口文件
 * 
 * 各个 store 将在后续任务中实现：
 * - user store (任务 20.2): 用户认证和状态管理 ✓
 * - exam store (任务 23.2): 考试会话和答案管理
 * - 其他业务 stores 根据需要添加
 */

// 导出用户 store
export { useUserStore } from './user'

// 导出考试 store
export { useExamStore } from './exam'

// 其他 stores 将在后续任务中添加
