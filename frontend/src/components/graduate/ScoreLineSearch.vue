<template>
  <div class="scoreline-search">
    <!-- 搜索表单 -->
    <div class="search-form">
      <el-form :model="searchForm" inline>
        <el-form-item label="院校名称">
          <el-input v-model="searchForm.school_name" placeholder="输入院校名称" clearable />
        </el-form-item>
        <el-form-item label="专业名称">
          <el-input v-model="searchForm.major_name" placeholder="输入专业名称" clearable />
        </el-form-item>
        <el-form-item label="年份">
          <el-select v-model="searchForm.year" placeholder="选择年份" clearable>
            <el-option v-for="y in years" :key="y" :label="y + '年'" :value="y" />
          </el-select>
        </el-form-item>
        <el-form-item label="省份">
          <el-select v-model="searchForm.province" placeholder="选择省份" clearable>
            <el-option v-for="p in provinces" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="分数范围">
          <el-input-number v-model="searchForm.min_score" :min="0" :max="500" placeholder="最低分" />
          <span class="range-separator">-</span>
          <el-input-number v-model="searchForm.max_score" :min="0" :max="500" placeholder="最高分" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 搜索结果 -->
    <div class="search-results">
      <el-table :data="scoreLines" v-loading="loading" stripe>
        <el-table-column prop="school_name" label="院校" min-width="150" />
        <el-table-column prop="major_name" label="专业" min-width="150" />
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="total_score" label="总分线" width="90">
          <template #default="{ row }">
            <span class="score-highlight">{{ row.total_score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="politics_score" label="政治" width="70" />
        <el-table-column prop="english_score" label="英语" width="70" />
        <el-table-column prop="math_score" label="数学" width="70" />
        <el-table-column prop="professional_score" label="专业课" width="80" />
        <el-table-column prop="enrollment_num" label="录取人数" width="90" />
      </el-table>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSearch"
          @current-change="handleSearch"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { searchScoreLines, getProvinces } from '../../api/graduate'

const loading = ref(false)
const scoreLines = ref([])
const provinces = ref([])
const years = [2024, 2023, 2022, 2021, 2020]

const searchForm = ref({
  school_name: '',
  major_name: '',
  year: null,
  province: '',
  min_score: null,
  max_score: null
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

async function handleSearch() {
  loading.value = true
  try {
    const res = await searchScoreLines({
      ...searchForm.value,
      page: pagination.value.page,
      page_size: pagination.value.pageSize
    })
    if (res.success) {
      scoreLines.value = res.data.records
      pagination.value.total = res.data.total
    }
  } catch (error) {
    console.error('搜索分数线失败:', error)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  searchForm.value = {
    school_name: '',
    major_name: '',
    year: null,
    province: '',
    min_score: null,
    max_score: null
  }
  pagination.value.page = 1
  handleSearch()
}

async function loadProvinces() {
  try {
    const res = await getProvinces()
    if (res.success) {
      provinces.value = res.data
    }
  } catch (error) {
    console.error('加载省份失败:', error)
  }
}

onMounted(() => {
  loadProvinces()
  handleSearch()
})
</script>

<style scoped>
.scoreline-search {
  padding: 10px 0;
}

.search-form {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
}

.range-separator {
  margin: 0 8px;
  color: #909399;
}

.search-results {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
}

.score-highlight {
  color: #f56c6c;
  font-weight: 600;
  font-size: 16px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
