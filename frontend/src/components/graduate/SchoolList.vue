<template>
  <div class="school-list">
    <!-- 搜索筛选 -->
    <div class="filter-section">
      <el-input
        v-model="filters.keyword"
        placeholder="搜索院校名称"
        clearable
        class="search-input"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
      
      <el-select v-model="filters.province" placeholder="选择省份" clearable @change="handleSearch">
        <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
      </el-select>
      
      <el-select v-model="filters.level" placeholder="院校层次" clearable @change="handleSearch">
        <el-option label="985院校" value="985" />
        <el-option label="211院校" value="211" />
        <el-option label="双一流" value="双一流" />
      </el-select>
      
      <el-button type="primary" @click="handleSearch">
        <el-icon><Search /></el-icon>
        搜索
      </el-button>
    </div>

    <!-- 院校列表 -->
    <div class="schools-grid" v-loading="loading">
      <div 
        v-for="school in schools" 
        :key="school.id" 
        class="school-card"
        @click="showSchoolDetail(school)"
      >
        <div class="school-header">
          <div class="school-logo">
            <el-icon :size="32"><School /></el-icon>
          </div>
          <div class="school-info">
            <h3>{{ school.name }}</h3>
            <div class="school-tags">
              <el-tag v-if="school.is_985" type="danger" size="small">985</el-tag>
              <el-tag v-if="school.is_211" type="warning" size="small">211</el-tag>
              <el-tag v-if="school.is_double_first" size="small">双一流</el-tag>
            </div>
          </div>
        </div>
        <div class="school-meta">
          <span><el-icon><Location /></el-icon> {{ school.province }} · {{ school.city }}</span>
          <span><el-icon><OfficeBuilding /></el-icon> {{ school.type }}</span>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        @size-change="loadSchools"
        @current-change="loadSchools"
      />
    </div>

    <!-- 院校详情弹窗 -->
    <el-dialog v-model="detailVisible" :title="selectedSchool?.name" width="800px" class="school-dialog">
      <div v-if="selectedSchool" class="school-detail">
        <div class="detail-header">
          <div class="detail-tags">
            <el-tag v-if="selectedSchool.is_985" type="danger">985工程</el-tag>
            <el-tag v-if="selectedSchool.is_211" type="warning">211工程</el-tag>
            <el-tag v-if="selectedSchool.is_double_first">双一流</el-tag>
            <el-tag type="info">{{ selectedSchool.type }}</el-tag>
          </div>
          <p class="detail-location">
            <el-icon><Location /></el-icon>
            {{ selectedSchool.province }} · {{ selectedSchool.city }}
          </p>
        </div>
        
        <el-divider />
        
        <div class="detail-info">
          <p v-if="selectedSchool.description">{{ selectedSchool.description }}</p>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">学校代码</span>
              <span class="value">{{ selectedSchool.code }}</span>
            </div>
            <div class="info-item">
              <span class="label">研招网站</span>
              <a :href="selectedSchool.website" target="_blank" class="value link">
                {{ selectedSchool.website }}
              </a>
            </div>
            <div class="info-item">
              <span class="label">招生电话</span>
              <span class="value">{{ selectedSchool.phone || '暂无' }}</span>
            </div>
          </div>
        </div>
        
        <el-divider content-position="left">招生专业</el-divider>
        
        <!-- 专业列表 -->
        <div class="majors-section">
          <el-table :data="majors" v-loading="loadingMajors" stripe>
            <el-table-column prop="name" label="专业名称" min-width="150" />
            <el-table-column prop="code" label="专业代码" width="100" />
            <el-table-column prop="category" label="学科门类" width="100" />
            <el-table-column prop="degree_type" label="学位类型" width="100" />
            <el-table-column prop="department" label="所属学院" min-width="150" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="showMajorDetail(row)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 专业详情弹窗 -->
    <el-dialog v-model="majorDetailVisible" :title="selectedMajor?.name" width="900px" class="major-dialog">
      <div v-if="selectedMajor" class="major-detail">
        <div class="major-header">
          <el-tag>{{ selectedMajor.code }}</el-tag>
          <el-tag type="info">{{ selectedMajor.category }}</el-tag>
          <el-tag :type="selectedMajor.degree_type === '学术型' ? 'success' : 'warning'">
            {{ selectedMajor.degree_type }}
          </el-tag>
          <span class="duration">学制：{{ selectedMajor.duration }}年</span>
        </div>
        
        <el-tabs v-model="majorTab">
          <el-tab-pane label="历年分数线" name="scorelines">
            <el-table :data="scoreLines" v-loading="loadingScoreLines" stripe>
              <el-table-column prop="year" label="年份" width="80" />
              <el-table-column prop="total_score" label="总分线" width="80" />
              <el-table-column prop="politics_score" label="政治" width="70" />
              <el-table-column prop="english_score" label="英语" width="70" />
              <el-table-column prop="math_score" label="数学" width="70" />
              <el-table-column prop="professional_score" label="专业课" width="80" />
              <el-table-column prop="enrollment_num" label="录取人数" width="90" />
              <el-table-column prop="remark" label="备注" min-width="150" />
            </el-table>
          </el-tab-pane>
          
          <el-tab-pane label="考试科目" name="subjects">
            <el-table :data="examSubjects" v-loading="loadingSubjects" stripe>
              <el-table-column prop="subject_code" label="科目代码" width="100" />
              <el-table-column prop="subject_name" label="科目名称" min-width="150" />
              <el-table-column prop="subject_type" label="科目类型" width="100" />
              <el-table-column prop="full_score" label="满分" width="80" />
              <el-table-column label="参考书目" min-width="250">
                <template #default="{ row }">
                  <div v-if="row.reference_books">
                    <el-tag 
                      v-for="(book, idx) in parseBooks(row.reference_books)" 
                      :key="idx"
                      size="small"
                      class="book-tag"
                    >
                      {{ book }}
                    </el-tag>
                  </div>
                  <span v-else class="text-muted">暂无</span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search, School, Location, OfficeBuilding } from '@element-plus/icons-vue'
import { 
  getSchools, getSchoolDetail, getSchoolMajors, 
  getMajorScoreLines, getMajorExamSubjects, getProvinces 
} from '../../api/graduate'

const loading = ref(false)
const schools = ref([])
const provinces = ref([])
const filters = ref({
  keyword: '',
  province: '',
  level: ''
})
const pagination = ref({
  page: 1,
  pageSize: 12,
  total: 0
})

// 院校详情
const detailVisible = ref(false)
const selectedSchool = ref(null)
const majors = ref([])
const loadingMajors = ref(false)

// 专业详情
const majorDetailVisible = ref(false)
const selectedMajor = ref(null)
const majorTab = ref('scorelines')
const scoreLines = ref([])
const examSubjects = ref([])
const loadingScoreLines = ref(false)
const loadingSubjects = ref(false)

async function loadSchools() {
  loading.value = true
  try {
    const res = await getSchools({
      page: pagination.value.page,
      page_size: pagination.value.pageSize,
      keyword: filters.value.keyword,
      province: filters.value.province,
      level: filters.value.level
    })
    if (res.success) {
      schools.value = res.data.records
      pagination.value.total = res.data.total
    }
  } catch (error) {
    console.error('加载院校列表失败:', error)
  } finally {
    loading.value = false
  }
}

async function loadProvinces() {
  try {
    const res = await getProvinces()
    if (res.success) {
      provinces.value = res.data
    }
  } catch (error) {
    console.error('加载省份列表失败:', error)
  }
}

function handleSearch() {
  pagination.value.page = 1
  loadSchools()
}

async function showSchoolDetail(school) {
  selectedSchool.value = school
  detailVisible.value = true
  loadingMajors.value = true
  
  try {
    const res = await getSchoolMajors(school.id, { page_size: 100 })
    if (res.success) {
      majors.value = res.data.records
    }
  } catch (error) {
    console.error('加载专业列表失败:', error)
  } finally {
    loadingMajors.value = false
  }
}

async function showMajorDetail(major) {
  selectedMajor.value = major
  majorDetailVisible.value = true
  majorTab.value = 'scorelines'
  
  loadScoreLines(major.id)
  loadExamSubjects(major.id)
}

async function loadScoreLines(majorId) {
  loadingScoreLines.value = true
  try {
    const res = await getMajorScoreLines(majorId)
    if (res.success) {
      scoreLines.value = res.data
    }
  } catch (error) {
    console.error('加载分数线失败:', error)
  } finally {
    loadingScoreLines.value = false
  }
}

async function loadExamSubjects(majorId) {
  loadingSubjects.value = true
  try {
    const res = await getMajorExamSubjects(majorId)
    if (res.success) {
      examSubjects.value = res.data
    }
  } catch (error) {
    console.error('加载考试科目失败:', error)
  } finally {
    loadingSubjects.value = false
  }
}

function parseBooks(booksJson) {
  try {
    return JSON.parse(booksJson)
  } catch {
    return []
  }
}

onMounted(() => {
  loadSchools()
  loadProvinces()
})
</script>

<style scoped>
.school-list {
  padding: 10px 0;
}

.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.search-input {
  width: 280px;
}

.schools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  min-height: 300px;
}

.school-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
}

.school-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.school-header {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.school-logo {
  width: 56px;
  height: 56px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.school-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.school-tags {
  display: flex;
  gap: 6px;
}

.school-meta {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #909399;
}

.school-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

/* 弹窗样式 */
.detail-header {
  margin-bottom: 16px;
}

.detail-tags {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-location {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
  font-size: 14px;
}

.detail-info p {
  color: #606266;
  line-height: 1.8;
  margin-bottom: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item .label {
  font-size: 13px;
  color: #909399;
}

.info-item .value {
  font-size: 14px;
  color: #303133;
}

.info-item .link {
  color: #409eff;
  text-decoration: none;
}

.info-item .link:hover {
  text-decoration: underline;
}

.major-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.duration {
  color: #606266;
  font-size: 14px;
}

.book-tag {
  margin: 2px 4px 2px 0;
}

.text-muted {
  color: #909399;
}
</style>
