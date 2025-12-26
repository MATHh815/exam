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
  
  // 如果路由不需要认证，直接放行
  if (!requiresAuth) {
    // 如果已登录用户访问登录/注册页，重定向到仪表盘
    if ((to.name === 'login' || to.name === 'register') && userStore.isLoggedIn) {
      next({ name: 'dashboard' })
      return
    }
    next()
    return
  }
  
  // 检查登录状态 - 只检查 token 是否存在
  const token = localStorage.getItem('access_token')
  console.log('路由守卫检查token:', token ? '存在' : '不存在')
  
  if (!token) {
    // 未登录，重定向到登录页
    console.log('未登录，跳转到登录页')
    ElMessage.warning('请先登录')
    next({
      name: 'login',
      query: { redirect: to.fullPath } // 保存目标路由，登录后跳转
    })
    return
  }
  
  // 如果有 token 但 store 中没有用户信息，尝试从本地存储恢复
  if (!userStore.user) {
    console.log('store中无用户信息，尝试从localStorage恢复')
    // 先尝试从本地存储恢复
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser)
        userStore.setUser(userData)
        console.log('从localStorage恢复用户信息成功:', userData.username)
      } catch (e) {
        console.error('解析本地用户信息失败:', e)
      }
    }
    
    // 如果仍然没有用户信息，尝试从服务器获取（但不阻塞路由）
    if (!userStore.user) {
      console.log('localStorage中也无用户信息，将在后台获取')
      // 不等待，让页面先加载，在后台获取用户信息
      userStore.fetchUserInfo().catch(error => {
        console.error('后台获取用户信息失败:', error)
        // 如果获取失败，让请求拦截器处理401错误
      })
    }
  } else {
    console.log('store中已有用户信息:', userStore.user.username)
  }
  
  // 检查管理员权限
  if (requiresAdmin && !userStore.isAdmin) {
    // 非管理员访问管理员页面
    console.log('非管理员访问管理员页面')
    ElMessage.error('您没有权限访问该页面')
    next({ name: 'dashboard' })
    return
  }
  
  // 所有检查通过，放行
  console.log('路由守卫检查通过，放行')
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
