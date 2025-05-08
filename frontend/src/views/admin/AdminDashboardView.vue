<template>
  <div class="admin-dashboard">
    <h1>Admin Dashboard</h1>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>Problems</span>
              <el-button type="primary" @click="$router.push('/admin/problems')">Manage</el-button>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-value">{{ stats.problemCount }}</div>
            <div class="stat-label">Total Problems</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>Users</span>
              <el-button type="primary" disabled>Manage</el-button>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-value">{{ stats.userCount }}</div>
            <div class="stat-label">Registered Users</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>Submissions</span>
              <el-button type="primary" disabled>Manage</el-button>
            </div>
          </template>
          <div class="card-content">
            <div class="stat-value">{{ stats.submissionCount }}</div>
            <div class="stat-label">Total Submissions</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="dashboard-row">
      <el-col :span="24">
        <el-card class="dashboard-card mb-20">
          <template #header>
            <div class="card-header">
              <span>系统设置</span>
              <el-button type="primary" @click="$router.push('/admin/settings')">管理</el-button>
            </div>
          </template>
          <div class="card-content">
            <p>配置在线评判系统的全局设置，包括用户注册控制等功能</p>
          </div>
        </el-card>
        
        <el-card class="recent-submissions">
          <template #header>
            <div class="card-header">
              <span>Recent Submissions</span>
            </div>
          </template>
          <el-table :data="recentSubmissions" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column label="Problem" width="250">
              <template #default="scope">
                <router-link :to="`/problems/${scope.row.problem_id}`">
                  {{ getProblemTitle(scope.row.problem_id) }}
                </router-link>
              </template>
            </el-table-column>
            <el-table-column label="User" width="150">
              <template #default="scope">
                {{ getUserName(scope.row.user_id) }}
              </template>
            </el-table-column>
            <el-table-column label="Status" width="150">
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
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import api from '@/services/api'

export default {
  name: 'AdminDashboardView',
  data() {
    return {
      stats: {
        problemCount: 0,
        userCount: 0,
        submissionCount: 0
      },
      recentSubmissions: [],
      problemsMap: {},
      usersMap: {},
      loading: false
    }
  },
  computed: {
    ...mapGetters({
      isAdmin: 'auth/isAdmin'
    })
  },
  methods: {
    ...mapActions({
      setError: 'setError'
    }),
    async fetchDashboardStats() {
      this.loading = true
      try {
        // Get problems count
        const problemsResponse = await api.get('/problems?limit=1')
        this.stats.problemCount = problemsResponse.data.length > 0 ? 
          parseInt(problemsResponse.headers['x-total-count'] || '0') : 0
        
        // Get recent submissions
        const submissionsResponse = await api.get('/submissions?limit=10')
        this.recentSubmissions = submissionsResponse.data
        this.stats.submissionCount = submissionsResponse.data.length > 0 ? 
          parseInt(submissionsResponse.headers['x-total-count'] || '0') : 0
        
        // Get users count (this would need a new API endpoint)
        // For now, we'll just set a placeholder
        this.stats.userCount = 0
        
        // Load problem and user details for display
        await this.loadProblemDetails()
        await this.loadUserDetails()
      } catch (error) {
        console.error('Error fetching dashboard stats', error)
        this.setError('Failed to load dashboard statistics')
      } finally {
        this.loading = false
      }
    },
    async loadProblemDetails() {
      // Get problem details for recent submissions
      const problemIds = [...new Set(this.recentSubmissions.map(s => s.problem_id))]
      
      try {
        for (const id of problemIds) {
          const response = await api.get(`/problems/${id}`)
          this.problemsMap[id] = response.data
        }
      } catch (error) {
        console.error('Error loading problem details', error)
      }
    },
    async loadUserDetails() {
      // Get user details for recent submissions
      const userIds = [...new Set(this.recentSubmissions.map(s => s.user_id))]
      
      try {
        for (const id of userIds) {
          const response = await api.get(`/users/${id}`)
          this.usersMap[id] = response.data
        }
      } catch (error) {
        console.error('Error loading user details', error)
      }
    },
    getProblemTitle(problemId) {
      return this.problemsMap[problemId]?.title || problemId
    },
    getUserName(userId) {
      return this.usersMap[userId]?.username || userId
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
  mounted() {
    if (!this.isAdmin) {
      this.$router.push('/')
      return
    }
    
    this.fetchDashboardStats()
  }
}
</script>

<style scoped>
.admin-dashboard {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 30px;
  color: #303133;
}

.dashboard-card {
  height: 100%;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-content {
  text-align: center;
  padding: 20px 0;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 1rem;
  color: #606266;
}

.dashboard-row {
  margin-top: 20px;
}

.recent-submissions {
  margin-bottom: 20px;
}

a {
  text-decoration: none;
  color: #409EFF;
}
</style>
