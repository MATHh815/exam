<template>
  <div class="graduate-schools-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-icon">
          <el-icon :size="48"><School /></el-icon>
        </div>
        <div class="header-text">
          <h1>考研院校查询</h1>
          <p>查询全国研究生招生院校、专业、分数线及考试科目</p>
        </div>
      </div>
    </div>

    <!-- 功能标签页 -->
    <el-tabs v-model="activeTab" class="main-tabs">
      <!-- 院校查询 -->
      <el-tab-pane label="院校查询" name="schools">
        <SchoolList />
      </el-tab-pane>

      <!-- 分数线查询 -->
      <el-tab-pane label="分数线查询" name="scorelines">
        <ScoreLineSearch />
      </el-tab-pane>

      <!-- 分数估算 -->
      <el-tab-pane label="分数估算" name="estimate">
        <ScoreEstimate />
      </el-tab-pane>

      <!-- 数据管理 -->
      <el-tab-pane label="数据管理" name="management">
        <SchoolManagement />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { School } from '@element-plus/icons-vue'
import SchoolList from '../components/graduate/SchoolList.vue'
import ScoreLineSearch from '../components/graduate/ScoreLineSearch.vue'
import ScoreEstimate from '../components/graduate/ScoreEstimate.vue'
import SchoolManagement from '../components/graduate/SchoolManagement.vue'

const activeTab = ref('schools')
</script>

<style scoped>
.graduate-schools-container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  background: linear-gradient(135deg, #0c1445 0%, #1a0a2e 50%, #16213e 100%);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(2px 2px at 10% 20%, rgba(255, 255, 255, 0.8) 50%, transparent 50%),
    radial-gradient(2px 2px at 30% 60%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(2px 2px at 50% 30%, rgba(255, 255, 255, 0.7) 50%, transparent 50%),
    radial-gradient(2px 2px at 70% 80%, rgba(255, 255, 255, 0.5) 50%, transparent 50%),
    radial-gradient(2px 2px at 90% 40%, rgba(255, 255, 255, 0.8) 50%, transparent 50%);
  pointer-events: none;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 24px;
  position: relative;
  z-index: 1;
}

.header-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.header-text h1 {
  font-size: 28px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px 0;
}

.header-text p {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.8);
  margin: 0;
}

.main-tabs {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
}

:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-tabs__nav-wrap::after) {
  background-color: rgba(255, 255, 255, 0.1);
}

:deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
}

:deep(.el-tabs__item.is-active) {
  color: #667eea;
}

:deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #667eea, #764ba2);
}
</style>
