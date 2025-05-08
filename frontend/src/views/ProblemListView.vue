<template>
  <div class="problem-list">
    <h1>Problem List</h1>
    
    <div class="filters">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="Difficulty">
          <el-select v-model="filters.difficulty" placeholder="All Difficulties" clearable>
            <el-option label="Easy" value="easy" />
            <el-option label="Medium" value="medium" />
            <el-option label="Hard" value="hard" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Tags">
          <el-select v-model="filters.tags" multiple placeholder="Select Tags" clearable>
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="applyFilters">Filter</el-button>
          <el-button @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <el-table 
      :data="problems" 
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="custom_id" label="ID" width="80" />
      <el-table-column prop="title" label="Title">
        <template #default="scope">
          <router-link :to="`/problems/${scope.row.custom_id}`">{{ scope.row.title }}</router-link>
        </template>
      </el-table-column>
      <el-table-column prop="difficulty" label="Difficulty" width="120">
        <template #default="scope">
          <el-tag :type="getDifficultyType(scope.row.difficulty)">
            {{ scope.row.difficulty }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Tags" width="220">
        <template #default="scope">
          <div class="tag-container">
            <el-tag 
              v-for="tag in scope.row.tags" 
              :key="tag" 
              size="small"
              effect="plain"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="Acceptance" width="120">
        <template #default="scope">
          {{ calculateAcceptanceRate(scope.row) }}%
        </template>
      </el-table-column>
      <el-table-column label="Status" width="120">
        <template #default="scope">
          <el-tag v-if="isSolved(scope.row.id)" type="success">Solved</el-tag>
          <el-tag v-else type="info">Unsolved</el-tag>
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
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
