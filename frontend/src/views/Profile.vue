<template>
  <div class="profile-container">
    <!-- 顶部个人信息横幅 - 深色科技风格 -->
    <div class="profile-banner">
      <div class="banner-bg">
        <div class="banner-pattern"></div>
      </div>
      <div class="banner-content">
        <div class="user-section">
          <div class="avatar-wrapper">
            <el-avatar :size="100" :src="userStore.userInfo?.avatar" class="user-avatar">
              {{ (userStore.userInfo?.nickname || userStore.userInfo?.username)?.charAt(0) }}
            </el-avatar>
            <div class="avatar-edit" @click="showAvatarDialog = true">
              <el-icon><Camera /></el-icon>
            </div>
            <div class="avatar-ring"></div>
          </div>
          <div class="user-info">
            <h1 class="user-name">{{ userStore.userInfo?.nickname || userStore.userInfo?.username }}</h1>
            <div class="user-meta">
              <el-tag :type="userStore.isAdmin ? 'danger' : ''" effect="dark" size="small" class="role-tag">
                <el-icon><UserFilled /></el-icon>
                {{ userStore.isAdmin ? '管理员' : '普通用户' }}
              </el-tag>
              <span class="join-date">
                <el-icon><Calendar /></el-icon>
                {{ formatDate(userStore.userInfo?.created_at) }} 加入
              </span>
            </div>
          </div>
        </div>
        <div class="stats-row">
          <div class="stat-box">
            <div class="stat-number">{{ stats.practice_count || 0 }}</div>
            <div class="stat-text">练习题数</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-box">
            <div class="stat-number">{{ stats.exam_count || 0 }}</div>
            <div class="stat-text">考试次数</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-box">
            <div class="stat-number">{{ stats.accuracy ? stats.accuracy.toFixed(0) + '%' : '0%' }}</div>
            <div class="stat-text">正确率</div>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-box">
            <div class="stat-number">{{ formatStudyTime(stats.study_duration) }}</div>
            <div class="stat-text">学习时长</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主体内容 -->
    <div class="profile-body">
      <!-- 左侧菜单 -->
      <div class="profile-menu">
        <div 
          v-for="item in menuItems" 
          :key="item.key"
          class="menu-item"
          :class="{ active: activeMenu === item.key }"
          @click="activeMenu = item.key"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.label }}</span>
          <el-icon class="arrow-icon"><ArrowRight /></el-icon>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="profile-content">
        <!-- 基本信息 -->
        <el-card v-show="activeMenu === 'basic'" class="content-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><User /></el-icon>
                基本信息
              </span>
              <el-button v-if="!isEditing" type="primary" @click="startEdit">
                <el-icon><Edit /></el-icon>
                编辑资料
              </el-button>
            </div>
          </template>

          <!-- 查看模式 -->
          <div v-if="!isEditing" class="info-grid">
            <div class="info-card">
              <div class="info-icon"><el-icon><User /></el-icon></div>
              <div class="info-detail">
                <span class="info-label">用户名</span>
                <span class="info-value">{{ userStore.userInfo?.username }}</span>
              </div>
            </div>
            <div class="info-card">
              <div class="info-icon"><el-icon><Avatar /></el-icon></div>
              <div class="info-detail">
                <span class="info-label">昵称</span>
                <span class="info-value">{{ userStore.userInfo?.nickname || '未设置' }}</span>
              </div>
            </div>
            <div class="info-card">
              <div class="info-icon"><el-icon><Message /></el-icon></div>
              <div class="info-detail">
                <span class="info-label">邮箱</span>
                <span class="info-value">{{ userStore.userInfo?.email || '未设置' }}</span>
              </div>
            </div>
            <div class="info-card">
              <div class="info-icon"><el-icon><Calendar /></el-icon></div>
              <div class="info-detail">
                <span class="info-label">注册时间</span>
                <span class="info-value">{{ formatDateTime(userStore.userInfo?.created_at) }}</span>
              </div>
            </div>
          </div>

          <!-- 编辑模式 -->
          <el-form v-else ref="formRef" :model="formData" :rules="rules" label-width="80px" class="edit-form">
            <el-form-item label="用户名">
              <el-input :value="userStore.userInfo?.username" disabled />
            </el-form-item>
            <el-form-item label="昵称" prop="nickname">
              <el-input v-model="formData.nickname" placeholder="请输入昵称" clearable />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="请输入邮箱" clearable />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="loading" @click="handleUpdate">保存修改</el-button>
              <el-button @click="cancelEdit">取消</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 安全设置 -->
        <el-card v-show="activeMenu === 'security'" class="content-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Lock /></el-icon>
                安全设置
              </span>
            </div>
          </template>
          
          <div class="security-list">
            <div class="security-item">
              <div class="security-icon">
                <el-icon><Key /></el-icon>
              </div>
              <div class="security-info">
                <div class="security-title">登录密码</div>
                <div class="security-desc">定期更换密码可以保护账户安全</div>
              </div>
              <el-button type="primary" @click="showPasswordDialog = true">修改密码</el-button>
            </div>
            <div class="security-item">
              <div class="security-icon email">
                <el-icon><Message /></el-icon>
              </div>
              <div class="security-info">
                <div class="security-title">绑定邮箱</div>
                <div class="security-desc">{{ userStore.userInfo?.email || '未绑定邮箱' }}</div>
              </div>
              <el-tag v-if="userStore.userInfo?.email" type="success" effect="plain">已绑定</el-tag>
              <el-button v-else type="primary" plain @click="activeMenu = 'basic'; startEdit()">去绑定</el-button>
            </div>
            <div class="security-item">
              <div class="security-icon status">
                <el-icon><CircleCheck /></el-icon>
              </div>
              <div class="security-info">
                <div class="security-title">账户状态</div>
                <div class="security-desc">当前账户状态正常</div>
              </div>
              <el-tag type="success" effect="plain">正常</el-tag>
            </div>
          </div>
        </el-card>

        <!-- 学习记录 -->
        <el-card v-show="activeMenu === 'records'" class="content-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><DataAnalysis /></el-icon>
                学习记录
              </span>
              <el-button type="primary" @click="$router.push('/statistics')">
                查看详细统计
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </template>
          
          <div class="records-grid">
            <div class="record-item blue">
              <div class="record-icon"><el-icon><EditPen /></el-icon></div>
              <div class="record-value">{{ stats.practice_count || 0 }}</div>
              <div class="record-label">练习题数</div>
            </div>
            <div class="record-item green">
              <div class="record-icon"><el-icon><CircleCheck /></el-icon></div>
              <div class="record-value">{{ stats.correct_count || 0 }}</div>
              <div class="record-label">正确题数</div>
            </div>
            <div class="record-item orange">
              <div class="record-icon"><el-icon><Document /></el-icon></div>
              <div class="record-value">{{ stats.exam_count || 0 }}</div>
              <div class="record-label">考试次数</div>
            </div>
            <div class="record-item purple">
              <div class="record-icon"><el-icon><Collection /></el-icon></div>
              <div class="record-value">{{ stats.wrong_count || 0 }}</div>
              <div class="record-label">错题数量</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="showPasswordDialog" title="修改密码" width="420px" :close-on-click-modal="false">
      <el-form ref="passwordFormRef" :model="passwordData" :rules="passwordRules" label-width="80px">
        <el-form-item label="旧密码" prop="old_password">
          <el-input v-model="passwordData.old_password" type="password" placeholder="请输入旧密码" show-password />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="passwordData.new_password" type="password" placeholder="请输入新密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input v-model="passwordData.confirm_password" type="password" placeholder="请再次输入新密码" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showPasswordDialog = false">取消</el-button>
        <el-button type="primary" :loading="passwordLoading" @click="handleChangePassword">确定</el-button>
      </template>
    </el-dialog>

    <!-- 修改头像对话框 -->
    <el-dialog v-model="showAvatarDialog" title="修改头像" width="400px">
      <el-form label-width="80px">
        <el-form-item label="头像URL">
          <el-input v-model="avatarUrl" placeholder="请输入头像图片URL" clearable />
        </el-form-item>
        <el-form-item label="预览">
          <el-avatar :size="80" :src="avatarUrl">
            {{ (userStore.userInfo?.nickname || userStore.userInfo?.username)?.charAt(0) }}
          </el-avatar>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAvatarDialog = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateAvatar">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, markRaw } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Camera, Calendar, Edit, ArrowRight, EditPen, CircleCheck,
  Document, Collection, User, Lock, Clock, UserFilled, Avatar,
  Message, Key, DataAnalysis
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import { updateProfile, changePassword } from '../api/auth'
import { getOverview } from '../api/statistics'

const userStore = useUserStore()

const menuItems = [
  { key: 'basic', label: '基本信息', icon: markRaw(User) },
  { key: 'security', label: '安全设置', icon: markRaw(Lock) },
  { key: 'records', label: '学习记录', icon: markRaw(DataAnalysis) }
]

const activeMenu = ref('basic')
const isEditing = ref(false)
const loading = ref(false)
const showPasswordDialog = ref(false)
const showAvatarDialog = ref(false)
const passwordLoading = ref(false)
const avatarUrl = ref('')
const stats = ref({})

const formRef = ref(null)
const passwordFormRef = ref(null)
const formData = reactive({ nickname: '', email: '' })
const passwordData = reactive({ old_password: '', new_password: '', confirm_password: '' })

const rules = {
  nickname: [{ max: 50, message: '昵称长度不能超过 50 个字符', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

const passwordRules = {
  old_password: [{ required: true, message: '请输入旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: (rule, value, callback) => {
      if (value !== passwordData.new_password) callback(new Error('两次输入的密码不一致'))
      else callback()
    }, trigger: 'blur' }
  ]
}

function formatDate(dateString) {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
}

function formatDateTime(dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

function formatStudyTime(minutes) {
  if (!minutes) return '0h'
  if (minutes < 60) return `${minutes}m`
  return `${Math.floor(minutes / 60)}h`
}

function startEdit() {
  isEditing.value = true
  formData.nickname = userStore.userInfo?.nickname || ''
  formData.email = userStore.userInfo?.email || ''
}

function cancelEdit() {
  isEditing.value = false
  formRef.value?.resetFields()
}

async function handleUpdate() {
  try {
    await formRef.value?.validate()
    loading.value = true
    const updateData = {}
    if (formData.nickname) updateData.nickname = formData.nickname
    if (formData.email) updateData.email = formData.email
    const response = await updateProfile(updateData)
    if (response.success && response.data) {
      userStore.setUser(response.data.user)
      ElMessage.success('更新成功')
      isEditing.value = false
    }
  } catch (error) {
    console.error('更新失败:', error)
    if (error.response?.data?.error?.message) ElMessage.error(error.response.data.error.message)
  } finally {
    loading.value = false
  }
}

async function handleChangePassword() {
  try {
    await passwordFormRef.value?.validate()
    passwordLoading.value = true
    await changePassword({ old_password: passwordData.old_password, new_password: passwordData.new_password })
    ElMessage.success('密码修改成功，请重新登录')
    showPasswordDialog.value = false
    setTimeout(() => { userStore.logout(); window.location.href = '/login' }, 1500)
  } catch (error) {
    console.error('修改密码失败:', error)
    if (error.response?.data?.error?.message) ElMessage.error(error.response.data.error.message)
  } finally {
    passwordLoading.value = false
  }
}

async function handleUpdateAvatar() {
  try {
    const response = await updateProfile({ avatar: avatarUrl.value })
    if (response.success && response.data) {
      userStore.setUser(response.data.user)
      ElMessage.success('头像更新成功')
      showAvatarDialog.value = false
    }
  } catch (error) {
    console.error('更新头像失败:', error)
    ElMessage.error('更新头像失败')
  }
}

async function loadStats() {
  try {
    const response = await getOverview({ days: 30 })
    if (response.data) stats.value = response.data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(async () => {
  if (!userStore.userInfo) {
    try { await userStore.fetchUserInfo() } catch (error) { console.error('获取用户信息失败:', error) }
  }
  avatarUrl.value = userStore.userInfo?.avatar || ''
  loadStats()
})
</script>

<style scoped>
.profile-container {
  min-height: calc(100vh - 104px);
}

/* 顶部横幅 - 深色科技风格 */
.profile-banner {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 24px;
}

.banner-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}

.banner-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    radial-gradient(circle at 20% 80%, rgba(64, 158, 255, 0.15) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(103, 194, 58, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(230, 162, 60, 0.08) 0%, transparent 40%),
    radial-gradient(2px 2px at 10% 20%, rgba(255, 255, 255, 0.8) 50%, transparent 50%),
    radial-gradient(2px 2px at 30% 60%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(2px 2px at 50% 30%, rgba(255, 255, 255, 0.7) 50%, transparent 50%),
    radial-gradient(2px 2px at 70% 80%, rgba(255, 255, 255, 0.5) 50%, transparent 50%),
    radial-gradient(2px 2px at 90% 40%, rgba(255, 255, 255, 0.8) 50%, transparent 50%),
    radial-gradient(1px 1px at 15% 45%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(1px 1px at 35% 85%, rgba(255, 255, 255, 0.5) 50%, transparent 50%),
    radial-gradient(1px 1px at 55% 15%, rgba(255, 255, 255, 0.7) 50%, transparent 50%),
    radial-gradient(1px 1px at 75% 55%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(1px 1px at 85% 25%, rgba(255, 255, 255, 0.8) 50%, transparent 50%);
  animation: banner-twinkle 5s ease-in-out infinite;
}

@keyframes banner-twinkle {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.banner-content {
  position: relative;
  padding: 40px;
  z-index: 1;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
}

.avatar-wrapper {
  position: relative;
}

.user-avatar {
  background: linear-gradient(135deg, #409eff 0%, #67c23a 100%);
  font-size: 36px;
  font-weight: 600;
  border: 4px solid rgba(255, 255, 255, 0.2);
}

.avatar-ring {
  position: absolute;
  inset: -8px;
  border: 2px solid rgba(64, 158, 255, 0.3);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.5; }
}

.avatar-edit {
  position: absolute;
  bottom: 4px;
  right: 4px;
  width: 32px;
  height: 32px;
  background: #409eff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  cursor: pointer;
  border: 3px solid #1a1a2e;
  transition: all 0.3s;
  font-size: 14px;
}

.avatar-edit:hover {
  transform: scale(1.1);
  background: #66b1ff;
}

.user-info {
  color: #fff;
}

.user-name {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 12px 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.user-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.role-tag {
  display: flex;
  align-items: center;
  gap: 4px;
  background: rgba(64, 158, 255, 0.2) !important;
  border-color: rgba(64, 158, 255, 0.4) !important;
}

.join-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.stats-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px 40px;
  backdrop-filter: blur(10px);
}

.stat-box {
  text-align: center;
  padding: 0 40px;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}

.stat-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.1);
}

/* 主体内容 */
.profile-body {
  display: flex;
  gap: 24px;
}

/* 左侧菜单 */
.profile-menu {
  width: 240px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 16px;
  flex-shrink: 0;
  height: fit-content;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: 10px;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.3s;
  margin-bottom: 8px;
}

.menu-item:last-child {
  margin-bottom: 0;
}

.menu-item .arrow-icon {
  margin-left: auto;
  opacity: 0;
  transition: all 0.3s;
}

.menu-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.menu-item:hover .arrow-icon {
  opacity: 0.5;
}

.menu-item.active {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.menu-item.active .arrow-icon {
  opacity: 1;
}

/* 右侧内容 */
.profile-content {
  flex: 1;
  min-width: 0;
}

.content-card {
  background: rgba(255, 255, 255, 0.1) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.content-card :deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 20px 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

/* 基本信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s;
}

.info-card:hover {
  border-color: rgba(64, 158, 255, 0.5);
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.info-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
}

.info-detail {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.info-value {
  font-size: 15px;
  font-weight: 500;
  color: white;
}

.edit-form {
  max-width: 500px;
}

/* 安全设置 */
.security-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.security-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s;
}

.security-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.security-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 20px;
}

.security-icon.email {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.security-icon.status {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
}

.security-info {
  flex: 1;
}

.security-title {
  font-size: 15px;
  font-weight: 500;
  color: white;
  margin-bottom: 4px;
}

.security-desc {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* 学习记录 */
.records-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.record-item {
  text-align: center;
  padding: 24px 16px;
  border-radius: 12px;
  transition: all 0.3s;
}

.record-item.blue {
  background: rgba(64, 158, 255, 0.15);
  border: 1px solid rgba(64, 158, 255, 0.3);
}

.record-item.green {
  background: rgba(103, 194, 58, 0.15);
  border: 1px solid rgba(103, 194, 58, 0.3);
}

.record-item.orange {
  background: rgba(230, 162, 60, 0.15);
  border: 1px solid rgba(230, 162, 60, 0.3);
}

.record-item.purple {
  background: rgba(102, 126, 234, 0.15);
  border: 1px solid rgba(102, 126, 234, 0.3);
}

.record-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.record-icon {
  font-size: 28px;
  margin-bottom: 12px;
}

.record-item.blue .record-icon { color: #409eff; }
.record-item.green .record-icon { color: #67c23a; }
.record-item.orange .record-icon { color: #e6a23c; }
.record-item.purple .record-icon { color: #667eea; }

.record-value {
  font-size: 28px;
  font-weight: 700;
  color: white;
  margin-bottom: 4px;
}

.record-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-row {
    padding: 16px 20px;
  }
  
  .stat-box {
    padding: 0 24px;
  }
  
  .stat-number {
    font-size: 26px;
  }
  
  .records-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 992px) {
  .banner-content {
    padding: 32px 24px;
  }
  
  .user-section {
    flex-direction: column;
    text-align: center;
  }
  
  .user-meta {
    justify-content: center;
  }
  
  .stats-row {
    flex-wrap: wrap;
    gap: 16px;
  }
  
  .stat-divider {
    display: none;
  }
  
  .stat-box {
    flex: 1;
    min-width: 80px;
    padding: 0 16px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .profile-body {
    flex-direction: column;
  }

  .profile-menu {
    width: 100%;
    display: flex;
    overflow-x: auto;
    padding: 12px;
    gap: 8px;
  }

  .menu-item {
    white-space: nowrap;
    padding: 12px 20px;
    margin-bottom: 0;
  }
  
  .menu-item .arrow-icon {
    display: none;
  }

  .records-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-number {
    font-size: 22px;
  }
}
</style>
