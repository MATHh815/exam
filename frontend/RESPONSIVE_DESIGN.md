# 响应式设计和性能优化文档

## 概述

本文档描述了考公考研考编系统前端的响应式设计和性能优化实现。

## 响应式设计

### 断点定义

系统使用以下响应式断点：

```javascript
{
  XS: 480px,   // 超小屏幕（手机竖屏）
  SM: 768px,   // 小屏幕（手机横屏、小平板）
  MD: 1024px,  // 中等屏幕（平板）
  LG: 1280px,  // 大屏幕（桌面）
  XL: 1920px   // 超大屏幕（大桌面）
}
```

### 响应式组件

#### 1. ResponsiveLayout 组件

提供响应式布局容器，支持：
- 自适应头部导航
- 可折叠侧边栏
- 移动端遮罩层
- 响应式内容区域

使用示例：

```vue
<template>
  <ResponsiveLayout
    title="页面标题"
    :show-header="true"
    :show-sidebar="true"
    :show-footer="false"
  >
    <template #sidebar>
      <!-- 侧边栏内容 -->
    </template>
    
    <template #header-actions>
      <!-- 头部操作按钮 -->
    </template>
    
    <!-- 主内容 -->
    <div>页面内容</div>
  </ResponsiveLayout>
</template>
```

#### 2. 响应式工具函数

```javascript
import { useResponsive } from '@/utils/responsive'

const { screenSize, isMobile, isTablet, isDesktop } = useResponsive()

// 根据屏幕尺寸调整行为
if (isMobile()) {
  // 移动端逻辑
}
```

### 响应式样式

#### 全局工具类

```css
/* 隐藏/显示类 */
.hidden-xs    /* 在小屏幕隐藏 */
.visible-xs   /* 仅在小屏幕显示 */

/* 容器类 */
.container    /* 响应式容器，最大宽度 1400px */
```

#### Element Plus 响应式覆盖

系统自动调整 Element Plus 组件在移动端的显示：
- 对话框宽度：90%
- 抽屉宽度：80%
- 消息框宽度：90%

## 加载状态管理

### 1. 全局加载组件

```javascript
import { showLoading, hideLoading } from '@/utils/loading'

// 显示加载
showLoading('加载中...')

// 隐藏加载
hideLoading()

// 包装异步函数
await withLoading(async () => {
  // 异步操作
}, '正在保存...')
```

### 2. 骨架屏组件

```vue
<template>
  <LoadingSkeleton
    type="card"
    :lines="3"
    :animated="true"
  />
</template>
```

支持的类型：
- `card`: 卡片骨架
- `list`: 列表骨架
- `table`: 表格骨架
- `text`: 文本骨架
- `custom`: 自定义骨架

### 3. 图片懒加载

```vue
<template>
  <LazyImage
    :src="imageUrl"
    alt="图片描述"
    :lazy="true"
  />
</template>
```

特性：
- 使用 Intersection Observer API
- 自动占位符
- 加载失败处理
- 平滑过渡动画

## 错误处理

### 1. 全局错误处理

```javascript
import { handleError } from '@/utils/errorHandler'

try {
  // 可能出错的代码
} catch (error) {
  handleError(error, {
    showMessage: true,
    showNotification: false,
    customMessage: '自定义错误消息'
  })
}
```

### 2. 错误边界组件

```vue
<template>
  <ErrorBoundary>
    <!-- 可能出错的组件 -->
  </ErrorBoundary>
</template>
```

### 3. 错误类型

- `NETWORK`: 网络错误
- `AUTH`: 认证错误
- `VALIDATION`: 验证错误
- `SERVER`: 服务器错误
- `UNKNOWN`: 未知错误

## 性能优化

### 1. 代码分割

#### 路由懒加载

```javascript
{
  path: '/dashboard',
  component: () => import(/* webpackChunkName: "dashboard" */ '../views/Dashboard.vue')
}
```

#### 手动代码分割

Vite 配置中实现了以下分割策略：
- `vue-vendor`: Vue 核心库
- `element-plus`: UI 组件库
- `echarts`: 图表库

### 2. 资源优化

#### 图片优化
- 使用懒加载
- 支持占位符
- 错误处理

#### CSS 优化
- CSS 代码分割
- 按需加载

#### JavaScript 优化
- Tree shaking
- 压缩混淆
- 移除 console（生产环境）

### 3. 性能监控

开发环境自动启用性能监控：

```javascript
import { enablePerformanceMonitoring } from '@/utils/performance'

// 自动监控
enablePerformanceMonitoring()
```

监控指标：
- DNS 查询时间
- TCP 连接时间
- 页面加载时间
- 首次渲染时间
- 资源加载统计
- 内存使用情况
- 长任务检测

### 4. 缓存策略

#### 浏览器缓存
- 静态资源使用强缓存
- API 响应使用协商缓存

#### 本地存储
- Token 存储在 localStorage
- 用户偏好存储在 localStorage

## 最佳实践

### 1. 组件开发

```vue
<template>
  <div class="component">
    <!-- 使用响应式工具类 -->
    <div class="hidden-xs">桌面端内容</div>
    <div class="visible-xs">移动端内容</div>
  </div>
</template>

<script setup>
import { useResponsive } from '@/utils/responsive'

const { isMobile } = useResponsive()

// 根据屏幕尺寸调整逻辑
const columns = computed(() => isMobile() ? 1 : 3)
</script>

<style scoped>
/* 移动端优先 */
.component {
  padding: 10px;
}

/* 桌面端 */
@media (min-width: 768px) {
  .component {
    padding: 20px;
  }
}
</style>
```

### 2. API 调用

```javascript
import { withLoading } from '@/utils/loading'
import { handleError } from '@/utils/errorHandler'

async function fetchData() {
  try {
    const data = await withLoading(
      () => api.getData(),
      '加载数据中...'
    )
    return data
  } catch (error) {
    handleError(error)
  }
}
```

### 3. 性能优化

```javascript
// 使用防抖
import { debounce } from '@/utils/responsive'

const handleSearch = debounce((keyword) => {
  // 搜索逻辑
}, 300)

// 使用节流
import { throttle } from '@/utils/responsive'

const handleScroll = throttle(() => {
  // 滚动逻辑
}, 100)
```

## 测试

### 响应式测试

在不同设备上测试：
1. iPhone SE (375px)
2. iPhone 12 Pro (390px)
3. iPad (768px)
4. iPad Pro (1024px)
5. Desktop (1920px)

### 性能测试

使用 Chrome DevTools：
1. Lighthouse 审计
2. Performance 面板
3. Network 面板
4. Coverage 面板

### 加载测试

测试场景：
1. 慢速 3G 网络
2. 快速 3G 网络
3. 4G 网络
4. WiFi 网络

## 浏览器兼容性

支持的浏览器：
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

不支持 IE 11。

## 未来改进

1. **PWA 支持**
   - Service Worker
   - 离线缓存
   - 推送通知

2. **更多优化**
   - 虚拟滚动
   - 图片 WebP 格式
   - HTTP/2 推送

3. **监控增强**
   - 用户行为追踪
   - 错误上报
   - 性能指标上报

## 参考资源

- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)
- [Vite 文档](https://vitejs.dev/)
- [Web Performance](https://web.dev/performance/)
