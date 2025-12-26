<template>
  <div class="loading-skeleton" :class="{ animated: animated }">
    <!-- 卡片骨架 -->
    <div v-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-header">
        <div class="skeleton-avatar" />
        <div class="skeleton-title" />
      </div>
      <div class="skeleton-content">
        <div class="skeleton-line" v-for="i in lines" :key="i" />
      </div>
    </div>

    <!-- 列表骨架 -->
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div class="skeleton-list-item" v-for="i in count" :key="i">
        <div class="skeleton-avatar" />
        <div class="skeleton-content">
          <div class="skeleton-title" />
          <div class="skeleton-line" />
        </div>
      </div>
    </div>

    <!-- 表格骨架 -->
    <div v-else-if="type === 'table'" class="skeleton-table">
      <div class="skeleton-table-header">
        <div class="skeleton-cell" v-for="i in columns" :key="i" />
      </div>
      <div class="skeleton-table-row" v-for="i in rows" :key="i">
        <div class="skeleton-cell" v-for="j in columns" :key="j" />
      </div>
    </div>

    <!-- 文本骨架 -->
    <div v-else-if="type === 'text'" class="skeleton-text">
      <div class="skeleton-line" v-for="i in lines" :key="i" :style="{ width: getLineWidth(i) }" />
    </div>

    <!-- 自定义骨架 -->
    <div v-else class="skeleton-custom">
      <slot />
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  type: {
    type: String,
    default: 'card',
    validator: (value) => ['card', 'list', 'table', 'text', 'custom'].includes(value)
  },
  animated: {
    type: Boolean,
    default: true
  },
  lines: {
    type: Number,
    default: 3
  },
  count: {
    type: Number,
    default: 3
  },
  rows: {
    type: Number,
    default: 5
  },
  columns: {
    type: Number,
    default: 4
  }
})

/**
 * 获取行宽度（随机化以模拟真实内容）
 */
function getLineWidth(index) {
  const widths = ['100%', '95%', '90%', '85%', '80%']
  return widths[index % widths.length]
}
</script>

<style scoped>
.loading-skeleton {
  width: 100%;
}

/* 基础骨架样式 */
.skeleton-avatar,
.skeleton-title,
.skeleton-line,
.skeleton-cell {
  background: linear-gradient(90deg, #f2f2f2 25%, #e6e6e6 50%, #f2f2f2 75%);
  background-size: 200% 100%;
  border-radius: 4px;
}

.loading-skeleton.animated .skeleton-avatar,
.loading-skeleton.animated .skeleton-title,
.loading-skeleton.animated .skeleton-line,
.loading-skeleton.animated .skeleton-cell {
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 卡片骨架 */
.skeleton-card {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.skeleton-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.skeleton-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  flex-shrink: 0;
}

.skeleton-title {
  height: 20px;
  flex: 1;
}

.skeleton-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.skeleton-line {
  height: 16px;
  width: 100%;
}

/* 列表骨架 */
.skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.skeleton-list-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.skeleton-list-item .skeleton-avatar {
  width: 40px;
  height: 40px;
}

.skeleton-list-item .skeleton-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-list-item .skeleton-title {
  height: 18px;
  width: 60%;
}

.skeleton-list-item .skeleton-line {
  height: 14px;
  width: 80%;
}

/* 表格骨架 */
.skeleton-table {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.skeleton-table-header,
.skeleton-table-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 15px;
  padding: 15px;
}

.skeleton-table-header {
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
}

.skeleton-table-row {
  border-bottom: 1px solid #f5f7fa;
}

.skeleton-cell {
  height: 20px;
}

/* 文本骨架 */
.skeleton-text {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 响应式 */
@media (max-width: 768px) {
  .skeleton-card {
    padding: 15px;
  }

  .skeleton-list-item {
    padding: 12px;
  }

  .skeleton-table-header,
  .skeleton-table-row {
    padding: 12px;
    gap: 10px;
  }
}
</style>
