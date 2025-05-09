<template>
  <div class="submission-list">
    <h1>我的提交记录</h1>
    
    <div class="filters">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="题目">
          <el-input 
            v-model="filters.problemTitle" 
            placeholder="输入题目关键词" 
            clearable 
            class="search-input"
            @input="searchProblems"
          >
            <template #suffix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-select 
            v-model="filters.status" 
            placeholder="所有状态" 
            clearable
            class="status-select"
          >
            <el-option label="通过" value="accepted">
              <span class="status-option"><el-tag type="success" size="small">通过</el-tag></span>
            </el-option>
            <el-option label="答案错误" value="wrong_answer">
              <span class="status-option"><el-tag type="danger" size="small">答案错误</el-tag></span>
            </el-option>
            <el-option label="超时" value="time_limit_exceeded">
              <span class="status-option"><el-tag type="warning" size="small">超时</el-tag></span>
            </el-option>
            <el-option label="内存超限" value="memory_limit_exceeded">
              <span class="status-option"><el-tag type="warning" size="small">内存超限</el-tag></span>
            </el-option>
            <el-option label="运行时错误" value="runtime_error">
              <span class="status-option"><el-tag type="danger" size="small">运行时错误</el-tag></span>
            </el-option>
            <el-option label="编译错误" value="compilation_error">
              <span class="status-option"><el-tag type="danger" size="small">编译错误</el-tag></span>
            </el-option>
            <el-option label="等待中" value="pending">
              <span class="status-option"><el-tag type="info" size="small">等待中</el-tag></span>
            </el-option>
            <el-option label="评判中" value="judging">
              <span class="status-option"><el-tag type="info" size="small">评判中</el-tag></span>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="applyFilters">筛选</el-button>
          <el-button @click="resetFilters">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
    
    <el-table 
      :data="submissions" 
      style="width: 100%"
      v-loading="loading"
    >
      <!-- ID列已被移除，以简化界面显示 -->
      <el-table-column label="题目" width="250">
        <template #default="scope">
          <router-link :to="`/problems/${scope.row.problem_id}`">
            {{ getProblemTitle(scope.row.problem_id) }}
          </router-link>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="200">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ formatStatus(scope.row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="语言" width="100">
        <template #default="scope">
          {{ scope.row.language }}
        </template>
      </el-table-column>
      <el-table-column label="耗时" width="120">
        <template #default="scope">
          {{ scope.row.time_used }} ms
        </template>
      </el-table-column>
      <el-table-column label="内存" width="120">
        <template #default="scope">
          {{ scope.row.memory_used }} KB
        </template>
      </el-table-column>
      <el-table-column label="提交时间" width="180">
        <template #default="scope">
          {{ formatDate(scope.row.submitted_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button 
            size="small" 
            type="primary" 
            @click="viewSubmission(scope.row.id)"
          >
            查看
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
import { Search } from '@element-plus/icons-vue'

export default {
  name: 'SubmissionListView',
  components: {
    Search
  },
  data() {
    return {
      currentPage: 1,
      pageSize: 10,
      filters: {
        problem_id: '',
        problemTitle: '', // 新增题目标题关键词搜索
        status: ''
      },
      problems: [],
      problemsMap: {},
      filteredProblems: [], // 搜索后的过滤题目列表
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
        this.setError('加载提交记录失败')
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
        problemTitle: '',
        status: ''
      }
      this.filteredProblems = [];
      this.currentPage = 1
      this.loadSubmissions()
    },
    
    // 搜索题目功能
    searchProblems() {
      if (!this.filters.problemTitle) {
        this.filters.problem_id = '';
        this.filteredProblems = [];
        return;
      }
      
      const keyword = this.filters.problemTitle.toLowerCase();
      this.filteredProblems = this.problems.filter(problem => 
        problem.title.toLowerCase().includes(keyword)
      );
      
      // 如果只有一个符合的题目，自动选中
      if (this.filteredProblems.length === 1) {
        this.filters.problem_id = this.filteredProblems[0].id;
      } else {
        this.filters.problem_id = '';
      }
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
        accepted: '通过',
        wrong_answer: '答案错误',
        time_limit_exceeded: '超时',
        memory_limit_exceeded: '内存超限',
        runtime_error: '运行时错误',
        compilation_error: '编译错误',
        pending: '等待中',
        judging: '评判中',
        system_error: '系统错误'
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

.search-input {
  width: 220px;
}

.status-select {
  width: 160px;
}

.status-option {
  display: flex;
  align-items: center;
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
