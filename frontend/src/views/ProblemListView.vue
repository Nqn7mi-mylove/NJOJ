<template>
  <div class="problem-list">
    <h1>题目列表</h1>
    
    <div class="filters">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="难度">
          <el-select 
            v-model="filters.difficulty" 
            placeholder="所有难度" 
            clearable
            class="wider-select"
          >
            <el-option label="简单" value="easy" />
            <el-option label="中等" value="medium" />
            <el-option label="困难" value="hard" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select 
            v-model="filters.tags" 
            multiple 
            placeholder="选择标签" 
            clearable
            class="tag-select"
            collapse-tags
          >
            <el-option v-for="tag in availableTags" :key="tag" :label="getChineseTag(tag)" :value="tag" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="applyFilters">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <el-table 
      :data="problems" 
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="custom_id" label="ID" width="80" />
      <el-table-column prop="title" label="标题">
        <template #default="scope">
          <router-link :to="`/problems/${scope.row.custom_id}`">{{ scope.row.title }}</router-link>
        </template>
      </el-table-column>
      <el-table-column prop="difficulty" label="难度" width="120">
        <template #default="scope">
          <el-tag :type="getDifficultyType(scope.row.difficulty)">
            {{ getChineseDifficulty(scope.row.difficulty) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="标签" width="220">
        <template #default="scope">
          <div class="tag-container">
            <el-tag 
              v-for="tag in scope.row.tags" 
              :key="tag" 
              size="small"
              effect="plain"
              class="tag-item"
            >
              {{ getChineseTag(tag) }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="通过率" width="120">
        <template #default="scope">
          {{ calculateAcceptanceRate(scope.row) }}%
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
        <template #default="scope">
          <el-tag v-if="isSolved(scope.row.id)" type="success">已解决</el-tag>
          <el-tag v-else type="info">未解决</el-tag>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination">
      <el-pagination
        layout="prev, pager, next"
        :total="totalProblems"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'ProblemListView',
  data() {
    return {
      currentPage: 1,
      pageSize: 10,
      filters: {
        difficulty: '',
        tags: []
      },
      availableTags: [
        'array', 'string', 'hash-table', 'dynamic-programming', 
        'math', 'sorting', 'greedy', 'depth-first-search', 
        'binary-search', 'tree', 'graph', 'breadth-first-search'
      ],
      loading: false
    }
  },
  computed: {
    ...mapGetters({
      problems: 'problems/allProblems',
      totalProblems: 'problems/totalProblems',
      isLoading: 'isLoading',
      currentUser: 'auth/currentUser'
    })
  },
  methods: {
    ...mapActions({
      fetchProblems: 'problems/fetchProblems'
    }),
    async loadProblems() {
      this.loading = true
      const skip = (this.currentPage - 1) * this.pageSize
      
      await this.fetchProblems({
        skip,
        limit: this.pageSize,
        difficulty: this.filters.difficulty,
        tags: this.filters.tags
      })
      
      this.loading = false
    },
    handlePageChange(page) {
      this.currentPage = page
      this.loadProblems()
    },
    applyFilters() {
      this.currentPage = 1
      this.loadProblems()
    },
    resetFilters() {
      this.filters = {
        difficulty: '',
        tags: []
      }
      this.currentPage = 1
      this.loadProblems()
    },
    getDifficultyType(difficulty) {
      const types = {
        easy: 'success',
        medium: 'warning',
        hard: 'danger'
      }
      return types[difficulty] || 'info'
    },
    calculateAcceptanceRate(problem) {
      if (!problem.submission_count) return 0
      return Math.round((problem.accepted_count / problem.submission_count) * 100)
    },
    getChineseDifficulty(difficulty) {
      const difficultyMap = {
        easy: '简单',
        medium: '中等',
        hard: '困难'
      }
      return difficultyMap[difficulty] || difficulty
    },
    getChineseTag(tag) {
      const tagMap = {
        'array': '数组',
        'string': '字符串',
        'hash-table': '哈希表',
        'dynamic-programming': '动态规划',
        'math': '数学',
        'sorting': '排序',
        'greedy': '贪心算法',
        'depth-first-search': '深度优先搜索',
        'binary-search': '二分搜索',
        'tree': '树',
        'graph': '图',
        'breadth-first-search': '广度优先搜索'
      }
      return tagMap[tag] || tag
    },
    isSolved(problemId) {
      if (!this.currentUser) return false
      return this.currentUser.solved_problems.includes(problemId)
    }
  },
  mounted() {
    this.loadProblems()
  }
}
</script>

<style scoped>
.problem-list {
  padding: 20px;
}

.wider-select {
  width: 160px;
}

.tag-select {
  width: 240px;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

.filters {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.filter-form {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag-item {
  margin-right: 0;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

a {
  text-decoration: none;
  color: #409EFF;
}
</style>
