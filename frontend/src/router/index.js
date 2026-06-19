import { createRouter, createWebHistory } from 'vue-router'
import { showLoading, hideLoading } from '../utils/loading'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 公开页面（不需要布局）
    {
      path: '/login',
      name: 'login',
      component: () => import(/* webpackChunkName: "auth" */ '../views/Login.vue'),
      meta: { requiresAuth: false, title: '登录' }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import(/* webpackChunkName: "auth" */ '../views/Register.vue'),
      meta: { requiresAuth: false, title: '注册' }
    },
    
    // 需要登录的页面（使用主布局）
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          redirect: '/dashboard'
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import(/* webpackChunkName: "dashboard" */ '../views/Dashboard.vue'),
          meta: { title: '首页' }
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import(/* webpackChunkName: "user" */ '../views/Profile.vue'),
          meta: { title: '个人中心' }
        },
        {
          path: 'practice',
          name: 'practice',
          component: () => import(/* webpackChunkName: "practice" */ '../views/Practice.vue'),
          meta: { title: '智能练习' }
        },
        {
          path: 'exams',
          name: 'examList',
          component: () => import(/* webpackChunkName: "exam" */ '../views/ExamList.vue'),
          meta: { title: '模拟考试' }
        },
        {
          path: 'wrong-book',
          name: 'wrongBook',
          component: () => import(/* webpackChunkName: "practice" */ '../views/WrongBook.vue'),
          meta: { title: '错题本' }
        },
        {
          path: 'statistics',
          name: 'statistics',
          component: () => import(/* webpackChunkName: "statistics" */ '../views/Statistics.vue'),
          meta: { title: '学习统计' }
        },
        {
          path: 'wrong-analysis',
          name: 'wrongAnalysis',
          component: () => import(/* webpackChunkName: "statistics" */ '../views/WrongAnalysis.vue'),
          meta: { title: '错题分析' }
        },
        {
          path: 'pomodoro',
          name: 'pomodoro',
          component: () => import(/* webpackChunkName: "tools" */ '../views/PomodoroTimer.vue'),
          meta: { title: '番茄钟' }
        },
        {
          path: 'knowledge-graph',
          name: 'knowledgeGraph',
          component: () => import(/* webpackChunkName: "tools" */ '../views/KnowledgeGraph.vue'),
          meta: { title: '知识图谱' }
        },
        {
          path: 'exam-history',
          name: 'examHistory',
          component: () => import(/* webpackChunkName: "exam" */ '../views/ExamHistory.vue'),
          meta: { title: '考试记录' }
        },
        {
          path: 'ai-analysis',
          name: 'aiAnalysis',
          component: () => import(/* webpackChunkName: "ai" */ '../views/AIAnalysis.vue'),
          meta: { title: 'AI智能分析' }
        },
        {
          path: 'graduate-schools',
          name: 'graduateSchools',
          component: () => import(/* webpackChunkName: "graduate" */ '../views/GraduateSchools.vue'),
          meta: { title: '考研院校查询' }
        },
        {
          path: 'questions',
          name: 'questions',
          component: () => import(/* webpackChunkName: "admin" */ '../views/QuestionManagement.vue'),
          meta: { requiresAdmin: true, title: '题库管理' }
        },
        {
          path: 'exam-papers',
          name: 'examPapers',
          component: () => import(/* webpackChunkName: "admin" */ '../views/ExamPaperManagement.vue'),
          meta: { requiresAdmin: true, title: '试卷管理' }
        },
        {
          path: 'study-plans',
          name: 'studyPlans',
          component: () => import(/* webpackChunkName: "study" */ '../views/StudyPlans.vue'),
          meta: { title: '学习计划' }
        },
        {
          path: 'notes',
          name: 'notes',
          component: () => import(/* webpackChunkName: "study" */ '../views/Notes.vue'),
          meta: { title: '我的笔记' }
        },
        {
          path: 'bookmarks',
          name: 'bookmarks',
          component: () => import(/* webpackChunkName: "study" */ '../views/Bookmarks.vue'),
          meta: { title: '我的收藏' }
        },
        {
          path: 'achievements',
          name: 'achievements',
          component: () => import(/* webpackChunkName: "gamification" */ '../views/Achievements.vue'),
          meta: { title: '成就系统' }
        },
        {
          path: 'daily-tasks',
          name: 'dailyTasks',
          component: () => import(/* webpackChunkName: "gamification" */ '../views/DailyTasks.vue'),
          meta: { title: '每日任务' }
        },
        {
          path: 'schedule',
          name: 'studySchedule',
          component: () => import(/* webpackChunkName: "study" */ '../views/StudySchedule.vue'),
          meta: { title: '学习日程' }
        }
      ]
    },
    
    // 考试页面（全屏，不使用主布局）
    {
      path: '/exam/:paperId',
      name: 'exam',
      component: () => import(/* webpackChunkName: "exam" */ '../views/Exam.vue'),
      meta: { requiresAuth: true, title: '考试' }
    },
    {
      path: '/exam/result/:resultId',
      name: 'examResult',
      component: () => import(/* webpackChunkName: "exam" */ '../views/ExamResult.vue'),
      meta: { requiresAuth: true, title: '考试结果' }
    },
    
    // 404页面
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: () => import(/* webpackChunkName: "error" */ '../views/NotFound.vue'),
      meta: { requiresAuth: false, title: '页面未找到' }
    }
  ],
  // 滚动行为
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0, behavior: 'smooth' }
    }
  }
})

// 全局前置守卫 - 路由守卫和权限控制
router.beforeEach(async (to, from, next) => {
  // 显示加载状态
  showLoading('页面加载中...')
  
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - 考公考研考编系统`
  } else {
    document.title = '考公考研考编系统'
  }
  
  // 获取用户 store
  const userStore = useUserStore()
  
  // 检查路由是否需要认证（检查当前路由和父路由）
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth !== false)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin === true)
  
  // 如果路由不需要认证，处理已登录用户的重定向逻辑
  if (!requiresAuth) {
    // 防止重定向循环：检查token存在性来确定登录状态
    const token = localStorage.getItem('access_token')
    const isAuthenticated = !!(token && token.trim())
    
    // 如果已登录用户访问登录/注册页，重定向到仪表盘（防止循环）
    if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
      console.log('已登录用户访问登录页，重定向到仪表盘')
      next({ name: 'dashboard' })
      return
    }
    next()
    return
  }
  
  // 需要认证的路由：优先检查token存在性（Requirements 1.3, 2.1）
  const token = localStorage.getItem('access_token')
  const isTokenValid = !!(token && token.trim())
  
  console.log('路由守卫检查 - token存在:', isTokenValid, 'store登录状态:', userStore.isLoggedIn)
  
  // 如果没有有效token，立即重定向到登录页（防止循环）
  if (!isTokenValid) {
    console.log('无有效token，重定向到登录页')
    ElMessage.warning('请先登录')
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
    return
  }
  
  // 有有效token，确保store状态同步（原子性操作）
  if (token !== userStore.accessToken) {
    console.log('token不同步，原子性更新store状态')
    try {
      userStore.accessToken = token
      // 同时检查refresh token
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        userStore.refreshToken = refreshToken
      }
    } catch (error) {
      console.error('更新store token失败:', error)
      // 如果更新失败，清除认证状态并重定向
      userStore.clearTokens()
      userStore.clearUser()
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  // 实现适当的状态恢复逻辑（Requirements 1.4, 2.2）
  if (!userStore.user) {
    console.log('store中无用户信息，尝试从localStorage恢复')
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser)
        userStore.setUser(userData)
        console.log('从localStorage恢复用户信息成功:', userData.username)
      } catch (parseError) {
        console.error('解析本地用户信息失败:', parseError)
        // 清除损坏的用户数据，但保留token（允许后台获取）
        localStorage.removeItem('user')
        userStore.user = null
        console.log('已清除损坏的用户数据，将在后台获取用户信息')
        
        // 异步获取用户信息，不阻塞路由导航
        userStore.fetchUserInfo().catch(fetchError => {
          console.error('后台获取用户信息失败:', fetchError)
          // 获取失败由API拦截器处理，不在此处理
        })
      }
    } else {
      // 没有本地用户信息但有token，异步获取用户信息
      console.log('localStorage中无用户信息，异步获取用户信息')
      userStore.fetchUserInfo().catch(fetchError => {
        console.error('异步获取用户信息失败:', fetchError)
        // 获取失败由API拦截器处理
      })
    }
  } else {
    console.log('store中已有用户信息:', userStore.user.username)
  }
  
  // 检查管理员权限（基于token优先级的认证状态）
  if (requiresAdmin) {
    // 由于已确认有有效token，可以检查管理员权限
    if (!userStore.user) {
      // 没有用户信息但有token，允许通过（用户信息将异步加载）
      console.log('需要管理员权限但用户信息未加载，基于token允许通过')
    } else if (!userStore.isAdmin) {
      // 有用户信息但不是管理员
      console.log('非管理员访问管理员页面')
      ElMessage.error('您没有权限访问该页面')
      next({ name: 'dashboard' })
      return
    }
  }
  
  // 所有检查通过，放行（基于token优先级的认证）
  console.log('路由守卫检查通过，基于token存在性允许访问')
  next()
})

// 全局后置守卫 - 隐藏加载状态
router.afterEach(() => {
  // 隐藏加载状态
  hideLoading()
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  hideLoading()
})

export default router
