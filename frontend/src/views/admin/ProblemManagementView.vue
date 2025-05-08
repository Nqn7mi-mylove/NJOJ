<template>
  <div class="problem-management">
    <div class="page-header">
      <h1>Problem Management</h1>
      <el-button type="primary" @click="$router.push('/admin/problems/create')">
        Create Problem
      </el-button>
    </div>
    
    <el-table 
      :data="problems" 
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="title" label="Title">
        <template #default="scope">
          <router-link :to="`/problems/${scope.row.id}`" target="_blank">
            {{ scope.row.title }}
          </router-link>
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
      <el-table-column label="Public" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_public ? 'success' : 'info'">
            {{ scope.row.is_public ? 'Yes' : 'No' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Submissions" width="120">
        <template #default="scope">
          {{ scope.row.submission_count }}
        </template>
      </el-table-column>
      <el-table-column label="Acceptance" width="120">
        <template #default="scope">
          {{ calculateAcceptanceRate(scope.row) }}%
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="200">
        <template #default="scope">
          <el-button 
            size="small" 
            type="primary" 
            @click="editProblem(scope.row.id)"
          >
            Edit
          </el-button>
          <el-button 
            size="small" 
            type="danger" 
            @click="confirmDelete(scope.row)"
          >
            Delete
          </el-button>
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
    
    <!-- Delete Confirmation Dialog -->
    <el-dialog
      v-model="deleteDialog.visible"
      title="Confirm Delete"
      width="30%"
    >
      <span>Are you sure you want to delete the problem "{{ deleteDialog.problem?.title }}"?</span>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteDialog.visible = false">Cancel</el-button>
          <el-button type="danger" @click="deleteProblem" :loading="deleteDialog.loading">
            Delete
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'ProblemManagementView',
  data() {
    return {
      currentPage: 1,
      pageSize: 10,
      loading: false,
      deleteDialog: {
        visible: false,
        problem: null,
        loading: false
      }
    }
  },
  computed: {
    ...mapGetters({
      problems: 'problems/allProblems',
      totalProblems: 'problems/totalProblems',
      isAdmin: 'auth/isAdmin'
    })
  },
  methods: {
    ...mapActions({
      fetchProblems: 'problems/fetchProblems',
      deleteProblemAction: 'problems/deleteProblem',
      setError: 'setError'
    }),
    async loadProblems() {
      this.loading = true
      const skip = (this.currentPage - 1) * this.pageSize
      
      await this.fetchProblems({
        skip,
        limit: this.pageSize
      })
      
      this.loading = false
    },
    handlePageChange(page) {
      this.currentPage = page
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
    editProblem(id) {
      this.$router.push(`/admin/problems/${id}/edit`)
    },
    confirmDelete(problem) {
      this.deleteDialog.problem = problem
      this.deleteDialog.visible = true
    },
    async deleteProblem() {
      if (!this.deleteDialog.problem) return
      
      this.deleteDialog.loading = true
      
      try {
        const success = await this.deleteProblemAction(this.deleteDialog.problem.id)
        
        if (success) {
          this.$message.success('Problem deleted successfully')
          this.loadProblems() // Refresh problem list
        } else {
          this.$message.error('Failed to delete problem')
        }
      } catch (error) {
        console.error('Error deleting problem', error)
        this.setError('Failed to delete problem')
      } finally {
        this.deleteDialog.loading = false
        this.deleteDialog.visible = false
        this.deleteDialog.problem = null
      }
    }
  },
  mounted() {
    if (!this.isAdmin) {
      this.$router.push('/')
      return
    }
    
    this.loadProblems()
  }
}
</script>

<style scoped>
.problem-management {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h1 {
  margin: 0;
  color: #303133;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
