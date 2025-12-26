<template>
  <div class="score-estimate">
    <!-- 输入表单 -->
    <div class="estimate-form">
      <div class="form-header">
        <el-icon class="header-icon"><TrendCharts /></el-icon>
        <div class="header-text">
          <h3>分数估算与AI智能推荐</h3>
          <p>输入你的预估成绩，AI为你智能分析并推荐可报考的院校</p>
        </div>
      </div>
      
      <el-form :model="scoreForm" label-position="top">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="总分" required>
              <el-input-number v-model="scoreForm.total_score" :min="0" :max="500" style="width: 100%" placeholder="0-500" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="政治">
              <el-input-number v-model="scoreForm.politics_score" :min="0" :max="100" style="width: 100%" placeholder="0-100" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="英语">
              <el-input-number v-model="scoreForm.english_score" :min="0" :max="100" style="width: 100%" placeholder="0-100" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="数学">
              <el-input-number v-model="scoreForm.math_score" :min="0" :max="150" style="width: 100%" placeholder="0-150" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="专业课">
              <el-input-number v-model="scoreForm.professional_score" :min="0" :max="150" style="width: 100%" placeholder="0-150" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="学科门类">
              <el-select v-model="scoreForm.category" placeholder="选择学科" clearable style="width: 100%">
                <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="目标省份">
              <el-select v-model="scoreForm.province" placeholder="选择省份" clearable style="width: 100%">
                <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="操作">
              <div class="action-buttons">
                <el-button type="primary" @click="handleEstimate" :loading="loading">
                  <el-icon><Search /></el-icon>
                  查询院校
                </el-button>
                <el-button type="success" @click="handleAIRecommend" :loading="aiLoading">
                  <el-icon><MagicStick /></el-icon>
                  AI推荐
                </el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </div>

    <!-- AI 智能推荐结果 -->
    <div v-if="aiResult" class="ai-recommendation">
      <div class="ai-header">
        <div class="ai-title">
          <el-icon class="ai-icon"><MagicStick /></el-icon>
          <span>AI 智能择校分析</span>
          <el-tag type="success" size="small">
            置信度 {{ aiResult.confidence }}%
          </el-tag>
        </div>
        <el-button text type="primary" @click="aiResult = null">
          <el-icon><Close /></el-icon>
          关闭
        </el-button>
      </div>
      
      <div class="ai-summary">
        <el-icon><InfoFilled /></el-icon>
        <span>{{ aiResult.summary }}</span>
      </div>
      
      <div class="ai-content" v-html="renderedRecommendation"></div>
      
      <div class="ai-suggestions" v-if="aiResult.suggestions?.length">
        <h4><el-icon><Sunny /></el-icon> AI 建议</h4>
        <ul>
          <li v-for="(suggestion, idx) in aiResult.suggestions" :key="idx">
            {{ suggestion }}
          </li>
        </ul>
      </div>
    </div>

    <!-- 估算结果 -->
    <div v-if="result" class="estimate-results">
      <div class="result-header">
        <h3>院校匹配结果</h3>
        <p>你的总分：<span class="user-score">{{ result.user_score }}</span> 分</p>
      </div>

      <!-- 冲刺院校 -->
      <div class="result-section reach">
        <div class="section-header">
          <el-icon><Aim /></el-icon>
          <span>冲刺院校</span>
          <el-tag type="danger" size="small">分数线接近，需努力</el-tag>
        </div>
        <div class="school-list" v-if="result.reach.length">
          <div v-for="item in result.reach" :key="item.id" class="school-item">
            <div class="school-name">{{ item.school_name }}</div>
            <div class="major-name">{{ item.major_name }}</div>
            <div class="score-info">
              <span class="year">{{ item.year }}年</span>
              <span class="score">{{ item.total_score }}分</span>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无推荐" :image-size="60" />
      </div>

      <!-- 稳妥院校 -->
      <div class="result-section match">
        <div class="section-header">
          <el-icon><CircleCheck /></el-icon>
          <span>稳妥院校</span>
          <el-tag type="success" size="small">录取概率较高</el-tag>
        </div>
        <div class="school-list" v-if="result.match.length">
          <div v-for="item in result.match" :key="item.id" class="school-item">
            <div class="school-name">{{ item.school_name }}</div>
            <div class="major-name">{{ item.major_name }}</div>
            <div class="score-info">
              <span class="year">{{ item.year }}年</span>
              <span class="score">{{ item.total_score }}分</span>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无推荐" :image-size="60" />
      </div>

      <!-- 保底院校 -->
      <div class="result-section safe">
        <div class="section-header">
          <el-icon><Lock /></el-icon>
          <span>保底院校</span>
          <el-tag type="info" size="small">录取把握大</el-tag>
        </div>
        <div class="school-list" v-if="result.safe.length">
          <div v-for="item in result.safe" :key="item.id" class="school-item">
            <div class="school-name">{{ item.school_name }}</div>
            <div class="major-name">{{ item.major_name }}</div>
            <div class="score-info">
              <span class="year">{{ item.year }}年</span>
              <span class="score">{{ item.total_score }}分</span>
            </div>
          </div>
        </div>
        <el-empty v-else description="暂无推荐" :image-size="60" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  TrendCharts, Aim, CircleCheck, Lock, Search, MagicStick, 
  Close, InfoFilled, Sunny 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { 
  estimateScore, getProvinces, getCategories, getAIRecommendation 
} from '../../api/graduate'

const loading = ref(false)
const aiLoading = ref(false)
const provinces = ref([])
const categories = ref([])
const result = ref(null)
const aiResult = ref(null)

const scoreForm = ref({
  total_score: null,
  politics_score: null,
  english_score: null,
  math_score: null,
  professional_score: null,
  category: '',
  province: ''
})

// 渲染 Markdown 内容
const renderedRecommendation = computed(() => {
  if (aiResult.value?.recommendation) {
    return marked(aiResult.value.recommendation)
  }
  return ''
})

async function handleEstimate() {
  if (!scoreForm.value.total_score) {
    ElMessage.warning('请输入总分')
    return
  }
  
  loading.value = true
  try {
    const res = await estimateScore(scoreForm.value)
    if (res.success) {
      result.value = res.data
    }
  } catch (error) {
    console.error('分数估算失败:', error)
    ElMessage.error('估算失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

async function handleAIRecommend() {
  if (!scoreForm.value.total_score) {
    ElMessage.warning('请输入总分')
    return
  }
  
  aiLoading.value = true
  try {
    const res = await getAIRecommendation(scoreForm.value)
    if (res.success) {
      aiResult.value = res.data
      ElMessage.success('AI 分析完成')
    }
  } catch (error) {
    console.error('AI推荐失败:', error)
    ElMessage.error('AI推荐失败，请稍后重试')
  } finally {
    aiLoading.value = false
  }
}

async function loadOptions() {
  try {
    const [provRes, catRes] = await Promise.all([getProvinces(), getCategories()])
    if (provRes.success) provinces.value = provRes.data
    if (catRes.success) categories.value = catRes.data
  } catch (error) {
    console.error('加载选项失败:', error)
  }
}

onMounted(() => {
  loadOptions()
})
</script>


<style scoped>
.score-estimate {
  padding: 10px 0;
}

.estimate-form {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.form-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.header-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 24px;
}

.header-text h3 {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 4px 0;
}

.header-text p {
  font-size: 14px;
  color: #909399;
  margin: 0;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

/* AI 推荐结果样式 */
.ai-recommendation {
  background: linear-gradient(135deg, #f5f7fa 0%, #e8f4f8 100%);
  border: 1px solid #d4e5f7;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.ai-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.ai-icon {
  color: #667eea;
  font-size: 24px;
}

.ai-summary {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 12px 16px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 16px;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.ai-summary .el-icon {
  color: #409eff;
  margin-top: 2px;
}

.ai-content {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
}

.ai-content :deep(h2) {
  font-size: 18px;
  color: #303133;
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #667eea;
}

.ai-content :deep(h3) {
  font-size: 15px;
  color: #303133;
  margin: 16px 0 8px 0;
}

.ai-content :deep(p) {
  color: #606266;
  line-height: 1.8;
  margin: 8px 0;
}

.ai-content :deep(ul) {
  padding-left: 20px;
  margin: 8px 0;
}

.ai-content :deep(li) {
  color: #606266;
  line-height: 1.8;
  margin: 4px 0;
}

.ai-content :deep(strong) {
  color: #303133;
}

.ai-content :deep(hr) {
  border: none;
  border-top: 1px dashed #dcdfe6;
  margin: 16px 0;
}

.ai-content :deep(em) {
  color: #909399;
  font-style: normal;
  font-size: 13px;
}

.ai-suggestions {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
}

.ai-suggestions h4 {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  color: #303133;
  margin: 0 0 12px 0;
}

.ai-suggestions h4 .el-icon {
  color: #e6a23c;
}

.ai-suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.ai-suggestions li {
  position: relative;
  padding-left: 20px;
  color: #606266;
  line-height: 1.8;
  margin: 6px 0;
}

.ai-suggestions li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #67c23a;
  font-weight: bold;
}

/* 估算结果样式 */
.estimate-results {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
}

.result-header {
  margin-bottom: 24px;
  text-align: center;
}

.result-header h3 {
  font-size: 20px;
  color: #303133;
  margin: 0 0 8px 0;
}

.user-score {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
}

.result-section {
  margin-bottom: 24px;
  padding: 16px;
  border-radius: 12px;
}

.result-section.reach {
  background: #fef0f0;
  border: 1px solid #fde2e2;
}

.result-section.match {
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
}

.result-section.safe {
  background: #f4f4f5;
  border: 1px solid #e4e7ed;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
}

.reach .section-header { color: #f56c6c; }
.match .section-header { color: #67c23a; }
.safe .section-header { color: #909399; }

.school-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.school-item {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.school-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.school-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.major-name {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
}

.score-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.score-info .year {
  color: #909399;
}

.score-info .score {
  color: #f56c6c;
  font-weight: 600;
}
</style>
