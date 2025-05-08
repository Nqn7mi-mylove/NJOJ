<template>
  <div class="submission-list">
    <h1>My Submissions</h1>
    
    <div class="filters">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="Problem">
          <el-select v-model="filters.problem_id" placeholder="All Problems" clearable filterable>
            <el-option 
              v-for="problem in problems" 
              :key="problem.id" 
              :label="problem.title" 
              :value="problem.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="Status">
          <el-select v-model="filters.status" placeholder="All Statuses" clearable>
            <el-option label="Accepted" value="accepted" />
            <el-option label="Wrong Answer" value="wrong_answer" />
            <el-option label="Time Limit Exceeded" value="time_limit_exceeded" />
            <el-option label="Memory Limit Exceeded" value="memory_limit_exceeded" />
            <el-option label="Runtime Error" value="runtime_error" />
            <el-option label="Compilation Error" value="compilation_error" />
            <el-option label="Pending" value="pending" />
            <el-option label="Judging" value="judging" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="applyFilters">Filter</el-button>
          <el-button @click="resetFilters">Reset</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <el-table 
      :data="submissions" 
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="Problem" width="250">
        <template #default="scope">
          <router-link :to="`/problems/${scope.row.problem_id}`">
            {{ getProblemTitle(scope.row.problem_id) }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="Status" width="200">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ formatStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Language" width="100">
        <template #default="scope">
          {{ scope.row.language }}
        </template>
      </el-table-column>
      <el-table-column label="Time" width="120">
        <template #default="scope">
          {{ scope.row.time_used }} ms
        </template>
      </el-table-column>
      <el-table-column label="Memory" width="120">
        <template #default="scope">
          {{ scope.row.memory_used }} KB
        </template>
      </el-table-column>
      <el-table-column label="Submitted At" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.submitted_at) }}
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="120">
        <template #default="scope">
          <el-button 
            size="small" 
            type="primary" 
            @click="viewSubmission(scope.row.id)"
          >
            View
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination">
      <el-pagination
        layout="prev, pager, next"
        :total="totalSubmissions"
        :page-size="pageSize"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import api from '@/services/api'

export default {
  name: 'SubmissionListView',
  data() {
    return {
      currentPage: 1,
      pageSize: 10,
      filters: {
        problem_id: '',
        status: ''
      },
      problems: [],
      problemsMap: {},
      loading: false
    }
  },
  computed: {
    ...mapGetters({
      submissions: 'submissions/allSubmissions',
      totalSubmissions: 'submissions/totalSubmissions',
      isLoggedIn: 'auth/isLoggedIn'
    })
  },
  methods: {
    ...mapActions({
      fetchSubmissions: 'submissions/fetchSubmissions',
      setError: 'setError'
    }),
    async loadSubmissions() {
      this.loading = true
      const skip = (this.currentPage - 1) * this.pageSize
      
      try {
        await this.fetchSubmissions({
          skip,
          limit: this.pageSize,
          problemId: this.filters.problem_id,
          status: this.filters.status
        })
        
        await this.loadProblemDetails()
      } catch (error) {
        console.error('Error loading submissions', error)
        this.setError('Failed to load submissions')
      } finally {
        this.loading = false
      }
    },
    async loadProblemsList() {
      try {
        // Load problems list for filter dropdown
        const response = await api.get('/problems?limit=100')
        this.problems = response.data
        
        // Create a map for quick lookup
        this.problems.forEach(problem => {
          this.problemsMap[problem.id] = problem
        })
      } catch (error) {
        console.error('Error loading problems list', error)
      }
    },
    async loadProblemDetails() {
      // Get problem details for submissions if not already in the map
      const problemIds = [...new Set(this.submissions.map(s => s.problem_id))]
      const missingIds = problemIds.filter(id => !this.problemsMap[id])
      
      if (missingIds.length === 0) return
      
      try {
        for (const id of missingIds) {
          const response = await api.get(`/problems/${id}`)
          this.problemsMap[id] = response.data
        }
      } catch (error) {
        console.error('Error loading problem details', error)
      }
    },
    handlePageChange(page) {
      this.currentPage = page
      this.loadSubmissions()
    },
    applyFilters() {
      this.currentPage = 1
      this.loadSubmissions()
    },
    resetFilters() {
      this.filters = {
        problem_id: '',
        status: ''
      }
      this.currentPage = 1
      this.loadSubmissions()
    },
    getProblemTitle(problemId) {
      return this.problemsMap[problemId]?.title || problemId
    },
    getStatusType(status) {
      const types = {
        accepted: 'success',
        wrong_answer: 'danger',
        time_limit_exceeded: 'warning',
        memory_limit_exceeded: 'warning',
        runtime_error: 'danger',
        compilation_error: 'danger',
        pending: 'info',
        judging: 'info',
        system_error: 'danger'
      }
      return types[status] || 'info'
    },
    formatStatus(status) {
      const formatted = {
        accepted: 'Accepted',
        wrong_answer: 'Wrong Answer',
        time_limit_exceeded: 'Time Limit Exceeded',
        memory_limit_exceeded: 'Memory Limit Exceeded',
        runtime_error: 'Runtime Error',
        compilation_error: 'Compilation Error',
        pending: 'Pending',
        judging: 'Judging',
        system_error: 'System Error'
      }
      return formatted[status] || status
    },
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    viewSubmission(submissionId) {
      this.$router.push(`/submissions/${submissionId}`)
    }
  },
  async mounted() {
    if (!this.isLoggedIn) {
      this.$router.push('/login')
      return
    }
    
    await this.loadProblemsList()
    await this.loadSubmissions()
  }
}
</script>

<style scoped>
.submission-list {
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
