<template>
  <div class="main-layout" :class="{ 'sidebar-collapsed': isCollapsed }">
    <!-- 星空背景 -->
    <StarryBackground />
    
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <!-- Logo区域 -->
      <div class="sidebar-header">
        <div class="logo">
          <el-icon :size="28"><Reading /></el-icon>
          <span v-show="!isCollapsed" class="logo-text">考试系统</span>
        </div>
      </div>

      <!-- 导航菜单 -->
      <el-scrollbar class="sidebar-menu">
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapsed"
          :collapse-transition="false"
          background-color="#1e1e2d"
          text-color="#a2a3b7"
          active-text-color="#ffffff"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <template #title>首页</template>
          </el-menu-item>

          <el-sub-menu index="study">
            <template #title>
              <el-icon><Reading /></el-icon>
              <span>学习中心</span>
            </template>
            <el-menu-item index="/practice">
              <el-icon><EditPen /></el-icon>
              <span>智能练习</span>
            </el-menu-item>
            <el-menu-item index="/exams">
              <el-icon><Document /></el-icon>
              <span>模拟考试</span>
            </el-menu-item>
            <el-menu-item index="/exam-history">
              <el-icon><Clock /></el-icon>
              <span>考试记录</span>
            </el-menu-item>
            <el-menu-item index="/wrong-book">
              <el-icon><Collection /></el-icon>
              <span>错题本</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="tools">
            <template #title>
              <el-icon><Notebook /></el-icon>
              <span>学习工具</span>
            </template>
            <el-menu-item index="/study-plans">
              <el-icon><Calendar /></el-icon>
              <span>学习计划</span>
            </el-menu-item>
            <el-menu-item index="/notes">
              <el-icon><Edit /></el-icon>
              <span>我的笔记</span>
            </el-menu-item>
            <el-menu-item index="/bookmarks">
              <el-icon><Star /></el-icon>
              <span>我的收藏</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="gamification">
            <template #title>
              <el-icon><Trophy /></el-icon>
              <span>游戏化</span>
            </template>
            <el-menu-item index="/achievements">
              <el-icon><Medal /></el-icon>
              <span>成就系统</span>
            </el-menu-item>
            <el-menu-item index="/daily-tasks">
              <el-icon><Checked /></el-icon>
              <span>每日任务</span>
            </el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/statistics">
            <el-icon><TrendCharts /></el-icon>
            <template #title>学习统计</template>
          </el-menu-item>

          <el-menu-item index="/ai-analysis">
            <el-icon><MagicStick /></el-icon>
            <template #title>AI智能分析</template>
          </el-menu-item>

          <el-menu-item index="/graduate-schools">
            <el-icon><School /></el-icon>
            <template #title>考研院校查询</template>
          </el-menu-item>

          <!-- 管理员菜单 -->
          <el-sub-menu v-if="userStore.isAdmin" index="admin">
            <template #title>
              <el-icon><Setting /></el-icon>
              <span>系统管理</span>
            </template>
            <el-menu-item index="/questions">
              <el-icon><List /></el-icon>
              <span>题库管理</span>
            </el-menu-item>
            <el-menu-item index="/exam-papers">
              <el-icon><Tickets /></el-icon>
              <span>试卷管理</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-scrollbar>

      <!-- 折叠按钮 -->
      <div class="sidebar-footer">
        <div class="collapse-btn" @click="toggleSidebar">
          <el-icon :size="18">
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航栏 -->
      <header class="header">
        <div class="header-left">
          <!-- 面包屑导航 -->
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentPageTitle">{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <!-- 搜索框 -->
          <div class="header-search">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索..."
              :prefix-icon="Search"
              clearable
              size="default"
              @keyup.enter="handleSearch"
            />
          </div>

          <!-- 全屏按钮 -->
          <el-tooltip content="全屏" placement="bottom">
            <div class="header-icon" @click="toggleFullscreen">
              <el-icon :size="20"><FullScreen /></el-icon>
            </div>
          </el-tooltip>

          <!-- 消息通知 -->
          <el-tooltip content="消息" placement="bottom">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0" class="header-badge">
              <div class="header-icon">
                <el-icon :size="20"><Bell /></el-icon>
              </div>
            </el-badge>
          </el-tooltip>

          <!-- 用户信息 -->
          <el-dropdown trigger="click" @command="handleUserCommand">
            <div class="user-info">
              <el-avatar :size="36" :src="userStore.userInfo?.avatar">
                {{ (userStore.userInfo?.nickname || userStore.userInfo?.username)?.charAt(0) }}
              </el-avatar>
              <div class="user-detail">
                <span class="user-name">{{ userStore.userInfo?.nickname || userStore.userInfo?.username }}</span>
                <span class="user-role">{{ userStore.isAdmin ? '管理员' : '普通用户' }}</span>
              </div>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <el-dropdown-item command="settings">
                  <el-icon><Setting /></el-icon>
                  账户设置
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 页面内容 -->
      <main class="content">
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Reading, HomeFilled, EditPen, Document, Collection, MagicStick,
  TrendCharts, Setting, List, Tickets, Fold, Expand,
  Search, FullScreen, Bell, ArrowDown, User, SwitchButton, Clock, School,
  Notebook, Calendar, Edit, Star, Trophy, Medal, Checked
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import StarryBackground from '../components/StarryBackground.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 侧边栏折叠状态
const isCollapsed = ref(false)
// 搜索关键词
const searchKeyword = ref('')
// 未读消息数
const unreadCount = ref(0)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 当前页面标题
const currentPageTitle = computed(() => {
  const titles = {
    '/dashboard': '',
    '/practice': '智能练习',
    '/exams': '模拟考试',
    '/exam-history': '考试记录',
    '/wrong-book': '错题本',
    '/study-plans': '学习计划',
    '/notes': '我的笔记',
    '/bookmarks': '我的收藏',
    '/achievements': '成就系统',
    '/daily-tasks': '每日任务',
    '/statistics': '学习统计',
    '/ai-analysis': 'AI智能分析',
    '/profile': '个人中心',
    '/questions': '题库管理',
    '/exam-papers': '试卷管理'
  }
  return titles[route.path] || route.meta?.title || ''
})

// 切换侧边栏
function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebarCollapsed', isCollapsed.value)
}

// 搜索
function handleSearch() {
  if (searchKeyword.value.trim()) {
    ElMessage.info(`搜索: ${searchKeyword.value}`)
    // TODO: 实现搜索功能
  }
}

// 全屏切换
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen()
  } else {
    document.exitFullscreen()
  }
}

// 用户下拉菜单命令
async function handleUserCommand(command) {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '<div style="text-align: center; padding: 20px 0;">' +
          '<div style="width: 80px; height: 80px; margin: 0 auto 20px; background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1)); border-radius: 50%; display: flex; align-items: center; justify-content: center;">' +
          '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#667eea" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>' +
          '</div>' +
          '<p style="font-size: 18px; font-weight: 600; color: #303133; margin: 0 0 8px;">确定要退出登录吗？</p>' +
          '<p style="font-size: 14px; color: #909399; margin: 0;">退出后需要重新登录才能继续学习</p>' +
          '</div>',
          '退出确认',
          {
            confirmButtonText: '确定退出',
            cancelButtonText: '继续学习',
            dangerouslyUseHTMLString: true,
            customClass: 'logout-confirm-dialog',
            confirmButtonClass: 'logout-confirm-btn',
            cancelButtonClass: 'logout-cancel-btn',
            center: true
          }
        )
        await userStore.logout()
        ElMessage.success('已退出登录，期待您的再次光临！')
        router.push('/login')
      } catch {
        // 用户取消
      }
      break
  }
}

// 初始化
onMounted(() => {
  // 恢复侧边栏状态
  const savedState = localStorage.getItem('sidebarCollapsed')
  if (savedState !== null) {
    isCollapsed.value = savedState === 'true'
  }
})
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
  background: transparent;
  position: relative;
}

/* 侧边栏 */
.sidebar {
  width: 240px;
  background: #1e1e2d;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 100;
  transition: width 0.3s ease;
}

.sidebar-collapsed .sidebar {
  width: 64px;
}

.sidebar-header {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-menu {
  flex: 1;
  overflow: hidden;
}

.sidebar-menu :deep(.el-menu) {
  border-right: none;
}

.sidebar-menu :deep(.el-menu-item),
.sidebar-menu :deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
}

.sidebar-menu :deep(.el-menu-item:hover),
.sidebar-menu :deep(.el-sub-menu__title:hover) {
  background-color: rgba(255, 255, 255, 0.05) !important;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 0 25px 25px 0;
  margin-right: 12px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  cursor: pointer;
  color: #a2a3b7;
  border-radius: 8px;
  transition: all 0.3s;
}

.collapse-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

/* 主内容区 */
.main-container {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left 0.3s ease;
}

.sidebar-collapsed .main-container {
  margin-left: 64px;
}

/* 顶部导航栏 */
.header {
  height: 64px;
  background: rgba(30, 30, 45, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 99;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-left :deep(.el-breadcrumb__inner) {
  color: rgba(255, 255, 255, 0.7) !important;
}

.header-left :deep(.el-breadcrumb__inner a) {
  color: rgba(255, 255, 255, 0.7) !important;
}

.header-left :deep(.el-breadcrumb__inner a:hover) {
  color: #667eea !important;
}

.header-left :deep(.el-breadcrumb__separator) {
  color: rgba(255, 255, 255, 0.4) !important;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-search {
  width: 200px;
}

.header-search :deep(.el-input__wrapper) {
  border-radius: 20px;
  background-color: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.header-search :deep(.el-input__inner) {
  color: #fff;
}

.header-search :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.5);
}

.header-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.7);
  transition: all 0.3s;
}

.header-icon:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #667eea;
}

.header-badge :deep(.el-badge__content) {
  top: 8px;
  right: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 8px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.user-detail {
  display: flex;
  flex-direction: column;
  line-height: 1.3;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.user-role {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* 页面内容 */
.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 页面过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-20px);
}

/* 响应式设计 */
@media (max-width: 992px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar-collapsed .sidebar {
    transform: translateX(-100%);
  }

  .main-container {
    margin-left: 0;
  }

  .sidebar-collapsed .main-container {
    margin-left: 0;
  }

  .header-search {
    display: none;
  }

  .user-detail {
    display: none;
  }
}

@media (max-width: 768px) {
  .header {
    padding: 0 16px;
  }

  .content {
    padding: 16px;
  }
}

/* 退出登录弹窗样式 */
:global(.logout-confirm-dialog) {
  border-radius: 20px !important;
  overflow: hidden;
}

:global(.logout-confirm-dialog .el-message-box__header) {
  padding: 20px 20px 0;
}

:global(.logout-confirm-dialog .el-message-box__title) {
  font-size: 16px;
  color: #909399;
}

:global(.logout-confirm-dialog .el-message-box__content) {
  padding: 0 20px;
}

:global(.logout-confirm-dialog .el-message-box__btns) {
  padding: 20px;
  display: flex;
  gap: 12px;
}

:global(.logout-confirm-dialog .el-message-box__btns button) {
  flex: 1;
  margin: 0 !important;
  border-radius: 10px !important;
  height: 44px;
  font-size: 15px;
}

:global(.logout-cancel-btn) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border: none !important;
  color: #fff !important;
}

:global(.logout-cancel-btn:hover) {
  opacity: 0.9;
}

:global(.logout-confirm-btn) {
  background: #f5f7fa !important;
  border: 1px solid #dcdfe6 !important;
  color: #606266 !important;
}

:global(.logout-confirm-btn:hover) {
  background: #ecf5ff !important;
  border-color: #c6e2ff !important;
  color: #409eff !important;
}
</style>
