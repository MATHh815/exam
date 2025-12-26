# 响应式设计和优化实现指南

## 快速开始

### 1. 使用响应式布局

```vue
<template>
  <ResponsiveLayout
    title="我的页面"
    :show-header="true"
    :show-sidebar="true"
    :show-footer="false"
  >
    <!-- 侧边栏内容 -->
    <template #sidebar>
      <el-menu>
        <el-menu-item>菜单项</el-menu-item>
      </el-menu>
    </template>

    <!-- 头部操作按钮 -->
    <template #header-actions>
      <el-button>操作</el-button>
    </template>

    <!-- 主内容 -->
    <div class="container">
      <h1>页面内容</h1>
    </div>
  </ResponsiveLayout>
</template>

<script setup>
import ResponsiveLayout from '@/components/ResponsiveLayout.vue'
</script>
```

### 2. 添加加载状态

#### 方式一：使用 withLoading 包装器

```javascript
import { withLoading } from '@/utils/loading'

async function loadData() {
  await withLoading(async () => {
    const response = await api.getData()
    data.value = response.data
  }, '正在加载数据...')
}
```

#### 方式二：手动控制

```javascript
import { showLoading, hideLoading } from '@/utils/loading'

async function loadData() {
  showLoading('加载中...')
  try {
    const response = await api.getData()
    data.value = response.data
  } finally {
    hideLoading()
  }
}
```

#### 方式三：使用骨架屏

```vue
<template>
  <div>
    <LoadingSkeleton v-if="loading" type="card" :lines="3" />
    <div v-else>
      <!-- 实际内容 -->
    </div>
  </div>
</template>

<script setup>
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import { ref } from 'vue'

const loading = ref(true)
</script>
```

### 3. 错误处理

#### API 调用错误处理

```javascript
import { handleError } from '@/utils/errorHandler'

async function saveData() {
  try {
    await api.save(data)
    ElMessage.success('保存成功')
  } catch (error) {
    handleError(error, {
      showMessage: true,
      customMessage: '保存失败，请重试'
    })
  }
}
```

#### 组件错误边界

```vue
<template>
  <ErrorBoundary>
    <ComplexComponent />
  </ErrorBoundary>
</template>

<script setup>
import ErrorBoundary from '@/components/ErrorBoundary.vue'
import ComplexComponent from './ComplexComponent.vue'
</script>
```

### 4. 响应式检测

```vue
<template>
  <div>
    <!-- 桌面端显示 -->
    <div v-if="isDesktop()" class="desktop-view">
      桌面端内容
    </div>

    <!-- 移动端显示 -->
    <div v-else class="mobile-view">
      移动端内容
    </div>

    <!-- 使用工具类 -->
    <div class="hidden-xs">仅桌面端显示</div>
    <div class="visible-xs">仅移动端显示</div>
  </div>
</template>

<script setup>
import { useResponsive } from '@/utils/responsive'

const { isMobile, isTablet, isDesktop, screenSize } = useResponsive()

// 根据屏幕尺寸调整列数
const columns = computed(() => {
  if (isMobile()) return 1
  if (isTablet()) return 2
  return 3
})
</script>
```

### 5. 图片懒加载

```vue
<template>
  <LazyImage
    :src="imageUrl"
    alt="图片描述"
    :lazy="true"
    placeholder="/placeholder.png"
  />
</template>

<script setup>
import LazyImage from '@/components/LazyImage.vue'

const imageUrl = ref('https://example.com/image.jpg')
</script>
```

### 6. 性能优化

#### 使用防抖

```javascript
import { debounce } from '@/utils/responsive'

const handleSearch = debounce((keyword) => {
  // 搜索逻辑
  console.log('搜索:', keyword)
}, 300)
```

#### 使用节流

```javascript
import { throttle } from '@/utils/responsive'

const handleScroll = throttle(() => {
  // 滚动逻辑
  console.log('滚动位置:', window.scrollY)
}, 100)
```

## 响应式样式编写

### 移动优先策略

```css
/* 基础样式（移动端） */
.card {
  padding: 10px;
  font-size: 14px;
}

/* 平板 */
@media (min-width: 768px) {
  .card {
    padding: 15px;
    font-size: 15px;
  }
}

/* 桌面 */
@media (min-width: 1024px) {
  .card {
    padding: 20px;
    font-size: 16px;
  }
}
```

### 使用全局工具类

```vue
<template>
  <div class="container">
    <div class="hidden-xs">桌面端内容</div>
    <div class="visible-xs">移动端内容</div>
    
    <div class="mt-20 mb-20">
      <h1 class="text-center">标题</h1>
    </div>
  </div>
</template>
```

## Element Plus 响应式

### 栅格系统

```vue
<template>
  <el-row :gutter="20">
    <!-- 移动端占满，平板占一半，桌面占三分之一 -->
    <el-col :xs="24" :sm="12" :md="8">
      <el-card>卡片 1</el-card>
    </el-col>
    <el-col :xs="24" :sm="12" :md="8">
      <el-card>卡片 2</el-card>
    </el-col>
    <el-col :xs="24" :sm="12" :md="8">
      <el-card>卡片 3</el-card>
    </el-col>
  </el-row>
</template>
```

### 响应式表格

```vue
<template>
  <el-table
    :data="tableData"
    style="width: 100%"
    :size="isMobile() ? 'small' : 'default'"
  >
    <el-table-column prop="name" label="名称" />
    <el-table-column prop="value" label="值" v-if="!isMobile()" />
  </el-table>
</template>

<script setup>
import { useResponsive } from '@/utils/responsive'

const { isMobile } = useResponsive()
</script>
```

## 性能监控

### 开发环境自动监控

性能监控在开发环境自动启用，会在控制台输出：
- 页面性能指标
- 资源加载统计
- 内存使用情况
- 长任务警告

### 手动测量性能

```javascript
import { measureTime, measureAsyncTime } from '@/utils/performance'

// 测量同步函数
measureTime(() => {
  // 耗时操作
}, '操作名称')

// 测量异步函数
await measureAsyncTime(async () => {
  await api.call()
}, 'API 调用')
```

## 常见场景

### 场景 1：列表页面

```vue
<template>
  <div class="list-page">
    <!-- 加载状态 -->
    <LoadingSkeleton v-if="loading" type="list" :count="5" />

    <!-- 空状态 -->
    <el-empty v-else-if="!list.length" description="暂无数据" />

    <!-- 列表内容 -->
    <el-row v-else :gutter="20">
      <el-col
        v-for="item in list"
        :key="item.id"
        :xs="24"
        :sm="12"
        :md="8"
        :lg="6"
      >
        <el-card>{{ item.name }}</el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import { withLoading } from '@/utils/loading'
import { handleError } from '@/utils/errorHandler'

const loading = ref(true)
const list = ref([])

onMounted(async () => {
  try {
    const response = await api.getList()
    list.value = response.data
  } catch (error) {
    handleError(error)
  } finally {
    loading.value = false
  }
})
</script>
```

### 场景 2：表单页面

```vue
<template>
  <div class="form-page">
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      :label-position="isMobile() ? 'top' : 'right'"
    >
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          提交
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useResponsive } from '@/utils/responsive'
import { handleError } from '@/utils/errorHandler'
import { ElMessage } from 'element-plus'

const { isMobile } = useResponsive()
const formRef = ref()
const submitting = ref(false)
const form = ref({ name: '' })

const rules = {
  name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
}

async function handleSubmit() {
  try {
    await formRef.value.validate()
    submitting.value = true

    await api.submit(form.value)
    ElMessage.success('提交成功')
  } catch (error) {
    if (error.errors) {
      // 表单验证错误
      return
    }
    handleError(error)
  } finally {
    submitting.value = false
  }
}
</script>
```

### 场景 3：详情页面

```vue
<template>
  <ResponsiveLayout title="详情页" :show-sidebar="false">
    <div class="detail-page">
      <!-- 骨架屏 -->
      <LoadingSkeleton v-if="loading" type="card" :lines="5" />

      <!-- 详情内容 -->
      <el-card v-else>
        <template #header>
          <div class="card-header">
            <span>{{ detail.title }}</span>
            <el-button type="primary" @click="handleEdit">编辑</el-button>
          </div>
        </template>

        <el-descriptions :column="isMobile() ? 1 : 2">
          <el-descriptions-item label="名称">
            {{ detail.name }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            {{ detail.status }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </ResponsiveLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import ResponsiveLayout from '@/components/ResponsiveLayout.vue'
import LoadingSkeleton from '@/components/LoadingSkeleton.vue'
import { useResponsive } from '@/utils/responsive'
import { handleError } from '@/utils/errorHandler'

const route = useRoute()
const { isMobile } = useResponsive()
const loading = ref(true)
const detail = ref({})

onMounted(async () => {
  try {
    const response = await api.getDetail(route.params.id)
    detail.value = response.data
  } catch (error) {
    handleError(error)
  } finally {
    loading.value = false
  }
})
</script>
```

## 调试技巧

### 1. 查看性能指标

打开浏览器控制台，性能指标会自动输出（开发环境）。

### 2. 测试不同屏幕尺寸

使用 Chrome DevTools 的设备模拟器：
1. 按 F12 打开开发者工具
2. 点击设备工具栏图标（Ctrl+Shift+M）
3. 选择不同设备或自定义尺寸

### 3. 测试慢速网络

在 Chrome DevTools 的 Network 面板：
1. 选择 "Slow 3G" 或 "Fast 3G"
2. 观察加载状态和骨架屏效果

### 4. 测试错误处理

在控制台手动触发错误：
```javascript
// 测试网络错误
throw new Error('Network Error')

// 测试 API 错误
throw { response: { status: 500, data: { error: { message: '服务器错误' } } } }
```

## 最佳实践

1. **始终使用响应式组件和工具**
2. **为异步操作添加加载状态**
3. **统一使用错误处理工具**
4. **优先使用懒加载**
5. **定期检查性能指标**
6. **在多种设备上测试**
7. **使用语义化的 HTML**
8. **保持代码简洁和可维护**

## 常见问题

### Q: 如何禁用性能监控？
A: 性能监控仅在开发环境启用，生产环境自动禁用。

### Q: 如何自定义断点？
A: 修改 `utils/responsive.js` 中的 `Breakpoints` 对象。

### Q: 如何处理特殊的错误？
A: 使用 `handleError` 的 `customMessage` 选项自定义错误消息。

### Q: 如何优化大列表性能？
A: 考虑使用虚拟滚动库，如 `vue-virtual-scroller`。

## 参考资源

- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Vite 文档](https://vitejs.dev/)
- [MDN Web 性能](https://developer.mozilla.org/zh-CN/docs/Web/Performance)
