<template>
  <div class="responsive-layout">
    <!-- 顶部导航栏 -->
    <header class="layout-header" v-if="showHeader">
      <div class="header-content">
        <div class="header-left">
          <el-icon class="menu-icon" :size="24" @click="toggleSidebar" v-if="showSidebar">
            <Menu />
          </el-icon>
          <h1 class="app-title">{{ title }}</h1>
        </div>
        <div class="header-right">
          <slot name="header-actions" />
        </div>
      </div>
    </header>

    <!-- 主体内容 -->
    <div class="layout-body" :class="{ 'with-sidebar': showSidebar }">
      <!-- 侧边栏 -->
      <aside class="layout-sidebar" v-if="showSidebar" :class="{ 'is-collapsed': sidebarCollapsed }">
        <slot name="sidebar" />
      </aside>

      <!-- 内容区域 -->
      <main class="layout-main">
        <div class="main-content" :class="contentClass">
          <slot />
        </div>
      </main>
    </div>

    <!-- 底部 -->
    <footer class="layout-footer" v-if="showFooter">
      <slot name="footer">
        <p>&copy; 2024 考公考研考编系统. All rights reserved.</p>
      </slot>
    </footer>

    <!-- 移动端侧边栏遮罩 -->
    <div
      class="sidebar-overlay"
      v-if="showSidebar && !sidebarCollapsed && isMobile"
      @click="toggleSidebar"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Menu } from '@element-plus/icons-vue'

const props = defineProps({
  title: {
    type: String,
    default: '考公考研考编系统'
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showSidebar: {
    type: Boolean,
    default: false
  },
  showFooter: {
    type: Boolean,
    default: false
  },
  contentClass: {
    type: String,
    default: ''
  }
})

const sidebarCollapsed = ref(false)
const isMobile = ref(false)

/**
 * 检查是否为移动设备
 */
function checkMobile() {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    sidebarCollapsed.value = true
  }
}

/**
 * 切换侧边栏
 */
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

/**
 * 监听窗口大小变化
 */
function handleResize() {
  checkMobile()
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

defineExpose({
  toggleSidebar,
  sidebarCollapsed
})
</script>

<style scoped>
.responsive-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 头部 */
.layout-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.menu-icon {
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
}

.menu-icon:hover {
  color: #409eff;
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

/* 主体 */
.layout-body {
  flex: 1;
  display: flex;
  position: relative;
}

.layout-body.with-sidebar {
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
}

/* 侧边栏 */
.layout-sidebar {
  width: 250px;
  background-color: #fff;
  border-right: 1px solid #e4e7ed;
  transition: width 0.3s, transform 0.3s;
  overflow-y: auto;
  overflow-x: hidden;
}

.layout-sidebar.is-collapsed {
  width: 0;
  transform: translateX(-100%);
}

/* 主内容 */
.layout-main {
  flex: 1;
  overflow-y: auto;
  background-color: #f5f7fa;
}

.main-content {
  padding: 20px;
  min-height: calc(100vh - 60px);
}

/* 底部 */
.layout-footer {
  background-color: #fff;
  border-top: 1px solid #e4e7ed;
  padding: 20px;
  text-align: center;
  color: #909399;
  font-size: 14px;
}

/* 移动端遮罩 */
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 99;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 15px;
    height: 50px;
  }

  .app-title {
    font-size: 16px;
  }

  .layout-sidebar {
    position: fixed;
    top: 50px;
    left: 0;
    bottom: 0;
    z-index: 100;
    width: 250px;
  }

  .layout-sidebar.is-collapsed {
    transform: translateX(-100%);
  }

  .main-content {
    padding: 15px;
    min-height: calc(100vh - 50px);
  }

  .layout-footer {
    padding: 15px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .header-content {
    padding: 0 10px;
  }

  .app-title {
    font-size: 14px;
  }

  .layout-sidebar {
    width: 200px;
  }

  .main-content {
    padding: 10px;
  }
}
</style>
