<template>
  <div class="login-page">
    <!-- 动态星空背景 -->
    <div class="cosmos-bg">
      <div class="stars-layer">
        <div class="stars stars-1"></div>
        <div class="stars stars-2"></div>
        <div class="stars stars-3"></div>
      </div>
      <div class="nebula-layer">
        <div class="nebula nebula-1"></div>
        <div class="nebula nebula-2"></div>
        <div class="nebula nebula-3"></div>
      </div>
      <div class="shooting-stars">
        <div class="meteor"></div>
        <div class="meteor"></div>
        <div class="meteor"></div>
      </div>
      <div class="floating-particles">
        <div class="particle" v-for="n in 20" :key="n" :style="getParticleStyle(n)"></div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧品牌区 -->
      <div class="brand-section">
        <div class="brand-content">
          <!-- 动态Logo -->
          <div class="logo-wrapper">
            <div class="logo-ring"></div>
            <div class="logo-ring"></div>
            <div class="logo-ring"></div>
            <div class="logo-core">
              <el-icon :size="48"><Reading /></el-icon>
            </div>
          </div>
          
          <h1 class="brand-title">
            <span class="title-line">考公考研考编</span>
            <span class="title-highlight">智能学习系统</span>
          </h1>
          
          <p class="brand-slogan">开启你的备考之旅，助你轻松上岸</p>

          <!-- 特色功能卡片 -->
          <div class="feature-cards">
            <div class="feature-card" v-for="(feature, index) in features" :key="index">
              <div class="feature-icon-wrap">
                <el-icon :size="24"><component :is="feature.icon" /></el-icon>
              </div>
              <div class="feature-text">
                <h4>{{ feature.title }}</h4>
                <p>{{ feature.desc }}</p>
              </div>
            </div>
          </div>

          <!-- 数据统计 -->
          <div class="stats-row">
            <div class="stat-block" v-for="(stat, index) in stats" :key="index">
              <span class="stat-num">{{ stat.value }}</span>
              <span class="stat-label">{{ stat.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧登录区 -->
      <div class="auth-section">
        <div class="auth-card">
          <!-- 玻璃光效 -->
          <div class="card-glow"></div>
          <div class="card-border"></div>
          
          <div class="card-content">
            <!-- 标题 -->
            <div class="auth-header">
              <h2 class="auth-title">{{ isLogin ? '欢迎回来' : '创建账户' }}</h2>
              <p class="auth-subtitle">{{ isLogin ? '登录您的账户继续学习' : '注册新账户开始学习之旅' }}</p>
            </div>

            <!-- 表单 -->
            <el-form
              ref="formRef"
              :model="formData"
              :rules="rules"
              class="auth-form"
              @submit.prevent="handleSubmit"
            >
              <div class="input-group">
                <div class="input-icon">
                  <el-icon><User /></el-icon>
                </div>
                <el-form-item prop="username">
                  <el-input
                    v-model="formData.username"
                    placeholder="请输入用户名"
                    size="large"
                    clearable
                  />
                </el-form-item>
              </div>

              <div class="input-group" v-if="!isLogin">
                <div class="input-icon">
                  <el-icon><Message /></el-icon>
                </div>
                <el-form-item prop="email">
                  <el-input
                    v-model="formData.email"
                    placeholder="请输入邮箱"
                    size="large"
                    clearable
                  />
                </el-form-item>
              </div>

              <div class="input-group" v-if="!isLogin">
                <div class="input-icon">
                  <el-icon><UserFilled /></el-icon>
                </div>
                <el-form-item prop="nickname">
                  <el-input
                    v-model="formData.nickname"
                    placeholder="请输入昵称（可选）"
                    size="large"
                    clearable
                  />
                </el-form-item>
              </div>

              <div class="input-group">
                <div class="input-icon">
                  <el-icon><Lock /></el-icon>
                </div>
                <el-form-item prop="password">
                  <el-input
                    v-model="formData.password"
                    type="password"
                    placeholder="请输入密码"
                    size="large"
                    show-password
                    @keyup.enter="handleSubmit"
                  />
                </el-form-item>
              </div>

              <div class="input-group" v-if="!isLogin">
                <div class="input-icon">
                  <el-icon><Lock /></el-icon>
                </div>
                <el-form-item prop="confirmPassword">
                  <el-input
                    v-model="formData.confirmPassword"
                    type="password"
                    placeholder="请再次输入密码"
                    size="large"
                    show-password
                    @keyup.enter="handleSubmit"
                  />
                </el-form-item>
              </div>

              <div v-if="isLogin" class="form-options">
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                <span class="forgot-link">忘记密码？</span>
              </div>

              <!-- 提交按钮 -->
              <button 
                type="button" 
                class="submit-btn" 
                :class="{ loading }"
                @click="handleSubmit"
                :disabled="loading"
              >
                <span class="btn-bg"></span>
                <span class="btn-text">
                  <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
                  {{ isLogin ? '登 录' : '注 册' }}
                </span>
              </button>

              <!-- 切换模式 -->
              <div class="switch-mode">
                <span>{{ isLogin ? '还没有账户？' : '已有账户？' }}</span>
                <a href="javascript:;" @click="toggleMode">
                  {{ isLogin ? '立即注册' : '立即登录' }}
                </a>
              </div>
            </el-form>
          </div>
        </div>

        <!-- 版权 -->
        <div class="copyright">
          <p>© 2024 考公考研考编系统 · 专注备考</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, Lock, Message, UserFilled, Reading,
  EditPen, Document, TrendCharts, Notebook, Loading
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const isLogin = ref(true)
const loading = ref(false)
const rememberMe = ref(false)

const features = [
  { icon: EditPen, title: '智能练习', desc: '海量真题智能推荐' },
  { icon: Document, title: '模拟考试', desc: '真实考试环境' },
  { icon: TrendCharts, title: '数据分析', desc: '精准定位薄弱点' },
  { icon: Notebook, title: '错题本', desc: '自动收集巩固' }
]

const stats = [
  { value: '10000+', label: '题库数量' },
  { value: '5000+', label: '注册用户' },
  { value: '98%', label: '好评率' }
]

const formData = reactive({
  username: '',
  password: '',
  email: '',
  nickname: '',
  confirmPassword: ''
})

const rules = computed(() => {
  const baseRules = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, max: 50, message: '密码长度至少 6 个字符', trigger: 'blur' }
    ]
  }

  if (!isLogin.value) {
    return {
      ...baseRules,
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== formData.password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }
  }
  return baseRules
})

function getParticleStyle(n) {
  const size = Math.random() * 4 + 2
  const left = Math.random() * 100
  const top = Math.random() * 100
  const duration = Math.random() * 20 + 10
  const delay = Math.random() * 10
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${left}%`,
    top: `${top}%`,
    animationDuration: `${duration}s`,
    animationDelay: `${delay}s`
  }
}

function toggleMode() {
  isLogin.value = !isLogin.value
  formRef.value?.resetFields()
  Object.assign(formData, {
    username: '',
    password: '',
    email: '',
    nickname: '',
    confirmPassword: ''
  })
}

async function handleSubmit() {
  try {
    await formRef.value?.validate()
    loading.value = true

    if (isLogin.value) {
      await userStore.login({
        username: formData.username,
        password: formData.password
      })
      ElMessage.success('登录成功！')
      
      // 等待一小段时间确保token已保存到localStorage
      await new Promise(resolve => setTimeout(resolve, 100))
      
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      await userStore.register({
        username: formData.username,
        password: formData.password,
        email: formData.email,
        nickname: formData.nickname || undefined
      })
      ElMessage.success('注册成功！')
      
      // 等待一小段时间确保token已保存到localStorage
      await new Promise(resolve => setTimeout(resolve, 100))
      
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    }
  } catch (error) {
    console.error('操作失败:', error)
    if (error.response?.data?.error?.message) {
      ElMessage.error(error.response.data.error.message)
    }
  } finally {
    loading.value = false
  }
}
</script>


<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* ========== 宇宙背景 ========== */
.cosmos-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    #0a0a1a 0%,
    #0d1033 20%,
    #1a0a2e 40%,
    #0f1a3d 60%,
    #16213e 80%,
    #0a0a1a 100%
  );
  background-size: 400% 400%;
  animation: cosmos-flow 25s ease-in-out infinite;
}

@keyframes cosmos-flow {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* 星星层 */
.stars-layer {
  position: absolute;
  width: 100%;
  height: 100%;
}

.stars {
  position: absolute;
  width: 200%;
  height: 200%;
  top: -50%;
  left: -50%;
}

.stars-1 {
  background-image: 
    radial-gradient(1px 1px at 10% 20%, #fff, transparent),
    radial-gradient(1px 1px at 20% 50%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 30% 30%, #fff, transparent),
    radial-gradient(1px 1px at 40% 70%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1px 1px at 50% 10%, #fff, transparent),
    radial-gradient(1px 1px at 60% 40%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 70% 80%, #fff, transparent),
    radial-gradient(1px 1px at 80% 25%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 90% 60%, #fff, transparent),
    radial-gradient(1px 1px at 15% 85%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1px 1px at 25% 15%, #fff, transparent),
    radial-gradient(1px 1px at 35% 55%, rgba(255,255,255,0.7), transparent),
    radial-gradient(1px 1px at 45% 35%, #fff, transparent),
    radial-gradient(1px 1px at 55% 75%, rgba(255,255,255,0.8), transparent),
    radial-gradient(1px 1px at 65% 5%, #fff, transparent),
    radial-gradient(1px 1px at 75% 45%, rgba(255,255,255,0.6), transparent),
    radial-gradient(1px 1px at 85% 95%, #fff, transparent),
    radial-gradient(1px 1px at 95% 35%, rgba(255,255,255,0.7), transparent);
  animation: stars-move 100s linear infinite, twinkle 4s ease-in-out infinite;
}

.stars-2 {
  background-image: 
    radial-gradient(2px 2px at 15% 25%, rgba(255,255,255,0.9), transparent),
    radial-gradient(2px 2px at 35% 65%, rgba(255,255,255,0.7), transparent),
    radial-gradient(2px 2px at 55% 15%, rgba(255,255,255,0.8), transparent),
    radial-gradient(2px 2px at 75% 85%, rgba(255,255,255,0.6), transparent),
    radial-gradient(2px 2px at 95% 45%, rgba(255,255,255,0.9), transparent),
    radial-gradient(2px 2px at 5% 75%, rgba(255,255,255,0.7), transparent),
    radial-gradient(2px 2px at 25% 5%, rgba(255,255,255,0.8), transparent),
    radial-gradient(2px 2px at 45% 95%, rgba(255,255,255,0.6), transparent),
    radial-gradient(2px 2px at 65% 35%, rgba(255,255,255,0.9), transparent),
    radial-gradient(2px 2px at 85% 55%, rgba(255,255,255,0.7), transparent);
  animation: stars-move 150s linear infinite reverse, twinkle 5s ease-in-out infinite 1s;
}

.stars-3 {
  background-image: 
    radial-gradient(3px 3px at 20% 40%, #fff, transparent),
    radial-gradient(3px 3px at 50% 80%, rgba(255,255,255,0.9), transparent),
    radial-gradient(3px 3px at 80% 20%, #fff, transparent),
    radial-gradient(3px 3px at 10% 90%, rgba(255,255,255,0.9), transparent),
    radial-gradient(3px 3px at 70% 60%, #fff, transparent);
  animation: stars-move 200s linear infinite, twinkle 6s ease-in-out infinite 2s;
}

@keyframes stars-move {
  0% { transform: translateX(0) translateY(0); }
  100% { transform: translateX(-50%) translateY(-50%); }
}

@keyframes twinkle {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* 星云层 */
.nebula-layer {
  position: absolute;
  width: 100%;
  height: 100%;
}

.nebula {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.nebula-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.4) 0%, transparent 70%);
  top: -20%;
  left: -10%;
  animation: nebula-float-1 30s ease-in-out infinite;
}

.nebula-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(118, 75, 162, 0.35) 0%, transparent 70%);
  bottom: -20%;
  right: -10%;
  animation: nebula-float-2 35s ease-in-out infinite;
}

.nebula-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(64, 158, 255, 0.25) 0%, transparent 70%);
  top: 30%;
  right: 20%;
  animation: nebula-float-3 40s ease-in-out infinite;
}

@keyframes nebula-float-1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(100px, 50px) scale(1.2); }
}

@keyframes nebula-float-2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-80px, -60px) scale(1.15); }
}

@keyframes nebula-float-3 {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(60px, -40px) rotate(180deg); }
}

/* 流星 */
.shooting-stars {
  position: absolute;
  width: 100%;
  height: 100%;
}

.meteor {
  position: absolute;
  width: 200px;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.8), transparent);
  border-radius: 50%;
  opacity: 0;
  transform: rotate(-45deg);
  filter: drop-shadow(0 0 6px #fff);
}

.meteor:nth-child(1) {
  top: 10%;
  left: 80%;
  animation: meteor-fall 8s ease-in-out infinite;
}

.meteor:nth-child(2) {
  top: 30%;
  left: 60%;
  animation: meteor-fall 12s ease-in-out infinite 4s;
}

.meteor:nth-child(3) {
  top: 50%;
  left: 90%;
  animation: meteor-fall 10s ease-in-out infinite 7s;
}

@keyframes meteor-fall {
  0% { opacity: 0; transform: translateX(0) translateY(0) rotate(-45deg); }
  5% { opacity: 1; }
  15% { opacity: 0; transform: translateX(-500px) translateY(500px) rotate(-45deg); }
  100% { opacity: 0; }
}

/* 浮动粒子 */
.floating-particles {
  position: absolute;
  width: 100%;
  height: 100%;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 50%;
  animation: particle-float 20s ease-in-out infinite;
}

@keyframes particle-float {
  0%, 100% { 
    transform: translateY(0) translateX(0); 
    opacity: 0.3;
  }
  25% { 
    transform: translateY(-30px) translateX(20px); 
    opacity: 0.8;
  }
  50% { 
    transform: translateY(-10px) translateX(-15px); 
    opacity: 0.5;
  }
  75% { 
    transform: translateY(-40px) translateX(10px); 
    opacity: 0.7;
  }
}

/* ========== 主内容 ========== */
.main-content {
  position: relative;
  z-index: 10;
  display: flex;
  min-height: 100vh;
}

/* 左侧品牌区 */
.brand-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
}

.brand-content {
  max-width: 520px;
  color: #fff;
}

/* Logo动画 */
.logo-wrapper {
  position: relative;
  width: 120px;
  height: 120px;
  margin-bottom: 40px;
}

.logo-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  border: 2px solid rgba(102, 126, 234, 0.3);
  border-radius: 50%;
  transform: translate(-50%, -50%);
}

.logo-ring:nth-child(1) {
  width: 100%;
  height: 100%;
  animation: ring-rotate 8s linear infinite;
  border-top-color: rgba(102, 126, 234, 0.8);
}

.logo-ring:nth-child(2) {
  width: 80%;
  height: 80%;
  animation: ring-rotate 6s linear infinite reverse;
  border-right-color: rgba(118, 75, 162, 0.8);
}

.logo-ring:nth-child(3) {
  width: 60%;
  height: 60%;
  animation: ring-rotate 4s linear infinite;
  border-bottom-color: rgba(64, 158, 255, 0.8);
}

@keyframes ring-rotate {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}

.logo-core {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 70px;
  height: 70px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: core-pulse 3s ease-in-out infinite;
}

@keyframes core-pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.3); }
  50% { box-shadow: 0 0 40px rgba(102, 126, 234, 0.6); }
}

.brand-title {
  margin: 0 0 16px 0;
  line-height: 1.3;
}

.title-line {
  display: block;
  font-size: 36px;
  font-weight: 300;
  opacity: 0.9;
}

.title-highlight {
  display: block;
  font-size: 48px;
  font-weight: 700;
  background: linear-gradient(90deg, #667eea, #764ba2, #409eff);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-flow 3s linear infinite;
}

@keyframes gradient-flow {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}

.brand-slogan {
  font-size: 18px;
  opacity: 0.7;
  margin: 0 0 48px 0;
}

/* 特色功能卡片 */
.feature-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 48px;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(102, 126, 234, 0.5);
  transform: translateY(-2px);
}

.feature-icon-wrap {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.feature-text h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
}

.feature-text p {
  margin: 0;
  font-size: 12px;
  opacity: 0.7;
}

/* 统计数据 */
.stats-row {
  display: flex;
  gap: 40px;
  padding-top: 32px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-block {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-num {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(90deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 14px;
  opacity: 0.6;
}

/* ========== 右侧登录区 ========== */
.auth-section {
  width: 480px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px;
}

.auth-card {
  position: relative;
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 24px;
  backdrop-filter: blur(20px);
  overflow: hidden;
}

.card-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: conic-gradient(
    from 0deg,
    transparent,
    rgba(102, 126, 234, 0.1),
    transparent,
    rgba(118, 75, 162, 0.1),
    transparent
  );
  animation: glow-rotate 10s linear infinite;
}

@keyframes glow-rotate {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.card-border {
  position: absolute;
  inset: 0;
  border-radius: 24px;
  padding: 1px;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.2),
    rgba(255, 255, 255, 0.05),
    rgba(102, 126, 234, 0.3),
    rgba(255, 255, 255, 0.05)
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
}

.card-content {
  position: relative;
  z-index: 1;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  margin: 0 0 8px 0;
}

.auth-subtitle {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* 表单样式 */
.auth-form {
  width: 100%;
}

.input-group {
  position: relative;
  margin-bottom: 20px;
}

.input-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.5);
  z-index: 10;
  font-size: 18px;
}

.input-group :deep(.el-form-item) {
  margin-bottom: 0;
}

.input-group :deep(.el-input__wrapper) {
  padding: 4px 15px 4px 44px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  box-shadow: none;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.input-group :deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.5);
}

.input-group :deep(.el-input__wrapper.is-focus) {
  border-color: rgba(102, 126, 234, 0.8);
  box-shadow: 0 0 20px rgba(102, 126, 234, 0.2);
}

.input-group :deep(.el-input__inner) {
  height: 48px;
  font-size: 15px;
  color: #fff;
}

.input-group :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4);
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.form-options :deep(.el-checkbox__label) {
  color: rgba(255, 255, 255, 0.7);
}

.forgot-link {
  color: rgba(102, 126, 234, 0.9);
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s;
}

.forgot-link:hover {
  color: #667eea;
}

/* 提交按钮 */
.submit-btn {
  position: relative;
  width: 100%;
  height: 52px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  overflow: hidden;
  margin-bottom: 24px;
}

.submit-btn .btn-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transition: all 0.3s;
}

.submit-btn:hover .btn-bg {
  transform: scale(1.02);
  filter: brightness(1.1);
}

.submit-btn .btn-text {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  letter-spacing: 4px;
}

.submit-btn.loading {
  pointer-events: none;
}

.submit-btn:disabled {
  opacity: 0.7;
}

/* 切换模式 */
.switch-mode {
  text-align: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.switch-mode a {
  color: #667eea;
  font-weight: 600;
  text-decoration: none;
  margin-left: 4px;
  transition: color 0.3s;
}

.switch-mode a:hover {
  color: #764ba2;
}

/* 版权 */
.copyright {
  margin-top: 40px;
  text-align: center;
}

.copyright p {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.4);
  margin: 0;
}

/* 加载动画 */
.is-loading {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ========== 响应式 ========== */
@media (max-width: 1024px) {
  .brand-section {
    display: none;
  }

  .auth-section {
    width: 100%;
    padding: 40px 20px;
  }
}

@media (max-width: 480px) {
  .auth-card {
    padding: 32px 24px;
  }

  .auth-title {
    font-size: 24px;
  }
}
</style>
