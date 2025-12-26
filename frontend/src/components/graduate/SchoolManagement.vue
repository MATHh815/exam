<template>
  <div class="school-management">
    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="showAddSchoolDialog">
        <el-icon><Plus /></el-icon>
        添加院校
      </el-button>
      <el-button type="success" @click="showAddMajorDialog">
        <el-icon><Plus /></el-icon>
        添加专业
      </el-button>
      <el-button type="warning" @click="showAddScoreLineDialog">
        <el-icon><Plus /></el-icon>
        添加分数线
      </el-button>
    </div>

    <!-- 院校列表 -->
    <div class="data-section">
      <div class="section-header">
        <h3><el-icon><School /></el-icon> 院校列表</h3>
        <el-input v-model="schoolKeyword" placeholder="搜索院校" clearable style="width: 200px" @input="loadSchools" />
      </div>
      <el-table :data="schools" v-loading="loadingSchools" stripe border>
        <el-table-column prop="name" label="院校名称" min-width="150" />
        <el-table-column prop="code" label="代码" width="80" />
        <el-table-column prop="province" label="省份" width="80" />
        <el-table-column prop="type" label="类型" width="100" />
        <el-table-column label="层次" width="150">
          <template #default="{ row }">
            <el-tag v-if="row.is_985" type="danger" size="small">985</el-tag>
            <el-tag v-if="row.is_211" type="warning" size="small">211</el-tag>
            <el-tag v-if="row.is_double_first" size="small">双一流</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editSchool(row)">编辑</el-button>
            <el-button type="success" link size="small" @click="viewMajors(row)">专业</el-button>
            <el-popconfirm title="确定删除该院校？" @confirm="handleDeleteSchool(row.id)">
              <template #reference>
                <el-button type="danger" link size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination
        v-model:current-page="schoolPage"
        :total="schoolTotal"
        :page-size="10"
        layout="total, prev, pager, next"
        @current-change="loadSchools"
        style="margin-top: 16px; justify-content: center;"
      />
    </div>

    <!-- 添加/编辑院校弹窗 -->
    <el-dialog v-model="schoolDialogVisible" :title="editingSchool ? '编辑院校' : '添加院校'" width="600px">
      <el-form :model="schoolForm" label-width="100px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="院校名称" required>
              <el-input v-model="schoolForm.name" placeholder="请输入院校名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="院校代码" required>
              <el-input v-model="schoolForm.code" placeholder="如：10001" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="省份">
              <el-input v-model="schoolForm.province" placeholder="如：北京" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="城市">
              <el-input v-model="schoolForm.city" placeholder="如：北京" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="类型">
              <el-select v-model="schoolForm.type" placeholder="选择类型" style="width: 100%">
                <el-option label="综合类" value="综合类" />
                <el-option label="理工类" value="理工类" />
                <el-option label="师范类" value="师范类" />
                <el-option label="财经类" value="财经类" />
                <el-option label="医药类" value="医药类" />
                <el-option label="农林类" value="农林类" />
                <el-option label="政法类" value="政法类" />
                <el-option label="艺术类" value="艺术类" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="层次">
              <el-checkbox v-model="schoolForm.is_985">985</el-checkbox>
              <el-checkbox v-model="schoolForm.is_211">211</el-checkbox>
              <el-checkbox v-model="schoolForm.is_double_first">双一流</el-checkbox>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="研招网站">
          <el-input v-model="schoolForm.website" placeholder="https://" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="schoolForm.phone" placeholder="招生办电话" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="schoolForm.description" type="textarea" :rows="3" placeholder="院校简介" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="schoolDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveSchool" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加专业弹窗 -->
    <el-dialog v-model="majorDialogVisible" :title="editingMajor ? '编辑专业' : '添加专业'" width="600px">
      <el-form :model="majorForm" label-width="100px">
        <el-form-item label="所属院校" required>
          <el-select v-model="majorForm.school_id" placeholder="选择院校" filterable style="width: 100%">
            <el-option v-for="s in allSchools" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="专业名称" required>
              <el-input v-model="majorForm.name" placeholder="如：计算机科学与技术" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="专业代码" required>
              <el-input v-model="majorForm.code" placeholder="如：081200" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学科门类">
              <el-select v-model="majorForm.category" placeholder="选择门类" style="width: 100%">
                <el-option label="哲学" value="哲学" />
                <el-option label="经济学" value="经济学" />
                <el-option label="法学" value="法学" />
                <el-option label="教育学" value="教育学" />
                <el-option label="文学" value="文学" />
                <el-option label="历史学" value="历史学" />
                <el-option label="理学" value="理学" />
                <el-option label="工学" value="工学" />
                <el-option label="农学" value="农学" />
                <el-option label="医学" value="医学" />
                <el-option label="管理学" value="管理学" />
                <el-option label="艺术学" value="艺术学" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学位类型">
              <el-select v-model="majorForm.degree_type" placeholder="选择类型" style="width: 100%">
                <el-option label="学术型" value="学术型" />
                <el-option label="专业型" value="专业型" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="学制(年)">
              <el-input-number v-model="majorForm.duration" :min="2" :max="5" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属学院">
              <el-input v-model="majorForm.department" placeholder="如：计算机学院" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="majorDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveMajor" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 添加分数线弹窗 -->
    <el-dialog v-model="scoreLineDialogVisible" title="添加分数线" width="600px">
      <el-form :model="scoreLineForm" label-width="100px">
        <el-form-item label="选择院校" required>
          <el-select v-model="selectedSchoolId" placeholder="先选择院校" filterable style="width: 100%" @change="loadSchoolMajorsForSelect">
            <el-option v-for="s in allSchools" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="选择专业" required>
          <el-select v-model="scoreLineForm.major_id" placeholder="选择专业" filterable style="width: 100%">
            <el-option v-for="m in schoolMajorsForSelect" :key="m.id" :label="m.name" :value="m.id" />
          </el-select>
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="年份" required>
              <el-select v-model="scoreLineForm.year" placeholder="选择年份" style="width: 100%">
                <el-option v-for="y in [2024, 2023, 2022, 2021, 2020]" :key="y" :label="y + '年'" :value="y" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="总分线" required>
              <el-input-number v-model="scoreLineForm.total_score" :min="0" :max="500" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="政治">
              <el-input-number v-model="scoreLineForm.politics_score" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="英语">
              <el-input-number v-model="scoreLineForm.english_score" :min="0" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="数学">
              <el-input-number v-model="scoreLineForm.math_score" :min="0" :max="150" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="专业课">
              <el-input-number v-model="scoreLineForm.professional_score" :min="0" :max="150" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="录取人数">
              <el-input-number v-model="scoreLineForm.enrollment_num" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报考人数">
              <el-input-number v-model="scoreLineForm.applicant_num" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="scoreLineForm.remark" placeholder="备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scoreLineDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveScoreLine" :loading="saving">保存</el-button>
      </template>
    </el-dialog>

    <!-- 查看专业弹窗 -->
    <el-dialog v-model="majorsDialogVisible" :title="currentSchool?.name + ' - 专业列表'" width="800px">
      <el-button type="primary" size="small" @click="showAddMajorForSchool" style="margin-bottom: 16px">
        <el-icon><Plus /></el-icon> 添加专业
      </el-button>
      <el-table :data="currentSchoolMajors" v-loading="loadingMajors" stripe border>
        <el-table-column prop="name" label="专业名称" min-width="150" />
        <el-table-column prop="code" label="代码" width="100" />
        <el-table-column prop="category" label="门类" width="80" />
        <el-table-column prop="degree_type" label="类型" width="80" />
        <el-table-column prop="duration" label="学制" width="60">
          <template #default="{ row }">{{ row.duration }}年</template>
        </el-table-column>
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="editMajor(row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="handleDeleteMajor(row.id)">
              <template #reference>
                <el-button type="danger" link size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, School } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import {
  getSchools, createSchool, updateSchool, deleteSchool,
  getSchoolMajors, createMajor, updateMajor, deleteMajor,
  createScoreLine
} from '../../api/graduate'

// 院校相关
const schools = ref([])
const allSchools = ref([])
const loadingSchools = ref(false)
const schoolPage = ref(1)
const schoolTotal = ref(0)
const schoolKeyword = ref('')
const schoolDialogVisible = ref(false)
const editingSchool = ref(null)
const schoolForm = ref({
  name: '', code: '', province: '', city: '', type: '',
  is_985: false, is_211: false, is_double_first: false,
  website: '', phone: '', description: ''
})

// 专业相关
const majorDialogVisible = ref(false)
const editingMajor = ref(null)
const majorForm = ref({
  school_id: null, name: '', code: '', category: '',
  degree_type: '学术型', duration: 3, department: ''
})
const majorsDialogVisible = ref(false)
const currentSchool = ref(null)
const currentSchoolMajors = ref([])
const loadingMajors = ref(false)

// 分数线相关
const scoreLineDialogVisible = ref(false)
const selectedSchoolId = ref(null)
const schoolMajorsForSelect = ref([])
const scoreLineForm = ref({
  major_id: null, year: 2024, total_score: null,
  politics_score: null, english_score: null,
  math_score: null, professional_score: null,
  enrollment_num: null, applicant_num: null, remark: ''
})

const saving = ref(false)

async function loadSchools() {
  loadingSchools.value = true
  try {
    const res = await getSchools({
      page: schoolPage.value,
      page_size: 10,
      keyword: schoolKeyword.value
    })
    if (res.success) {
      schools.value = res.data.records
      schoolTotal.value = res.data.total
    }
  } finally {
    loadingSchools.value = false
  }
}

async function loadAllSchools() {
  const res = await getSchools({ page_size: 500 })
  if (res.success) {
    allSchools.value = res.data.records
  }
}

function showAddSchoolDialog() {
  editingSchool.value = null
  schoolForm.value = {
    name: '', code: '', province: '', city: '', type: '',
    is_985: false, is_211: false, is_double_first: false,
    website: '', phone: '', description: ''
  }
  schoolDialogVisible.value = true
}

function editSchool(school) {
  editingSchool.value = school
  schoolForm.value = { ...school }
  schoolDialogVisible.value = true
}

async function handleSaveSchool() {
  if (!schoolForm.value.name || !schoolForm.value.code) {
    ElMessage.warning('请填写院校名称和代码')
    return
  }
  saving.value = true
  try {
    if (editingSchool.value) {
      await updateSchool(editingSchool.value.id, schoolForm.value)
      ElMessage.success('更新成功')
    } else {
      await createSchool(schoolForm.value)
      ElMessage.success('添加成功')
    }
    schoolDialogVisible.value = false
    loadSchools()
    loadAllSchools()
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDeleteSchool(id) {
  try {
    await deleteSchool(id)
    ElMessage.success('删除成功')
    loadSchools()
    loadAllSchools()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

function showAddMajorDialog() {
  editingMajor.value = null
  majorForm.value = {
    school_id: null, name: '', code: '', category: '',
    degree_type: '学术型', duration: 3, department: ''
  }
  majorDialogVisible.value = true
}

function showAddMajorForSchool() {
  editingMajor.value = null
  majorForm.value = {
    school_id: currentSchool.value?.id, name: '', code: '', category: '',
    degree_type: '学术型', duration: 3, department: ''
  }
  majorDialogVisible.value = true
}

function editMajor(major) {
  editingMajor.value = major
  majorForm.value = { ...major }
  majorDialogVisible.value = true
}

async function handleSaveMajor() {
  if (!majorForm.value.school_id || !majorForm.value.name || !majorForm.value.code) {
    ElMessage.warning('请填写完整信息')
    return
  }
  saving.value = true
  try {
    if (editingMajor.value) {
      await updateMajor(editingMajor.value.id, majorForm.value)
      ElMessage.success('更新成功')
    } else {
      await createMajor(majorForm.value)
      ElMessage.success('添加成功')
    }
    majorDialogVisible.value = false
    if (currentSchool.value) {
      loadCurrentSchoolMajors()
    }
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDeleteMajor(id) {
  try {
    await deleteMajor(id)
    ElMessage.success('删除成功')
    loadCurrentSchoolMajors()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

async function viewMajors(school) {
  currentSchool.value = school
  majorsDialogVisible.value = true
  loadCurrentSchoolMajors()
}

async function loadCurrentSchoolMajors() {
  if (!currentSchool.value) return
  loadingMajors.value = true
  try {
    const res = await getSchoolMajors(currentSchool.value.id, { page_size: 100 })
    if (res.success) {
      currentSchoolMajors.value = res.data.records
    }
  } finally {
    loadingMajors.value = false
  }
}

function showAddScoreLineDialog() {
  selectedSchoolId.value = null
  schoolMajorsForSelect.value = []
  scoreLineForm.value = {
    major_id: null, year: 2024, total_score: null,
    politics_score: null, english_score: null,
    math_score: null, professional_score: null,
    enrollment_num: null, applicant_num: null, remark: ''
  }
  scoreLineDialogVisible.value = true
}

async function loadSchoolMajorsForSelect() {
  if (!selectedSchoolId.value) {
    schoolMajorsForSelect.value = []
    return
  }
  const res = await getSchoolMajors(selectedSchoolId.value, { page_size: 100 })
  if (res.success) {
    schoolMajorsForSelect.value = res.data.records
  }
}

async function handleSaveScoreLine() {
  if (!scoreLineForm.value.major_id || !scoreLineForm.value.year || !scoreLineForm.value.total_score) {
    ElMessage.warning('请填写完整信息')
    return
  }
  saving.value = true
  try {
    await createScoreLine(scoreLineForm.value)
    ElMessage.success('添加成功')
    scoreLineDialogVisible.value = false
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadSchools()
  loadAllSchools()
})
</script>


<style scoped>
.school-management {
  padding: 10px 0;
}

.action-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.data-section {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.section-header h3 .el-icon {
  color: #667eea;
}
</style>
