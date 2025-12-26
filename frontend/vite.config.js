import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [
    vue({
      // 启用响应式转换
      reactivityTransform: true
    })
  ],
  test: {
    globals: true,
    environment: 'node'
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    // 代码分割策略
    rollupOptions: {
      output: {
        manualChunks: {
          // 将 Vue 相关库打包到一起
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          // 将 Element Plus 单独打包
          'element-plus': ['element-plus', '@element-plus/icons-vue'],
          // 将 ECharts 单独打包
          'echarts': ['echarts', 'vue-echarts']
        }
      }
    },
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // 生成 sourcemap
    sourcemap: false,
    // 压缩选项
    minify: 'terser',
    terserOptions: {
      compress: {
        // 生产环境移除 console
        drop_console: true,
        drop_debugger: true
      }
    },
    // chunk 大小警告限制
    chunkSizeWarningLimit: 1000
  },
  // 优化依赖预构建
  optimizeDeps: {
    include: [
      'vue',
      'vue-router',
      'pinia',
      'axios',
      'element-plus',
      '@element-plus/icons-vue',
      'echarts',
      'vue-echarts'
    ]
  }
})
