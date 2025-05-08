<template>
  <div class="problem-detail" v-loading="isLoading">
    <div v-if="problem" class="problem-container">
      <div class="problem-header">
        <h1>{{ problem.title }}</h1>
        <div class="problem-meta">
          <el-tag :type="getDifficultyType(problem.difficulty)">
            {{ problem.difficulty }}
          </el-tag>
          <span class="problem-stats">
            Submissions: {{ problem.submission_count }} | 
            Acceptance: {{ calculateAcceptanceRate(problem) }}%
          </span>
          <div class="problem-tags">
            <el-tag 
              v-for="tag in problem.tags" 
              :key="tag"
              size="small"
              effect="plain"
              class="tag-item"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="problem-tabs">
        <el-tab-pane label="Description" name="description">
          <div class="problem-description">
            <MarkdownRenderer :content="problem.description" />
          </div>
        </el-tab-pane>
        <el-tab-pane label="Submissions" name="submissions" v-if="isLoggedIn">
          <div class="submissions-list">
            <el-table 
              :data="problemSubmissions" 
              style="width: 100%"
              v-loading="submissionsLoading"
            >
              <!-- ID列已被移除，以简化界面显示 -->
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
          </div>
        </el-tab-pane>
        <el-tab-pane label="Submit" name="submit" v-if="isLoggedIn">
          <div class="submission-form">
            <div class="language-select">
              <span>Language:</span>
              <el-select v-model="submission.language" placeholder="Select Language">
                <el-option label="C++" value="cpp" />
              </el-select>
            </div>
            
            <div class="code-editor">
              <CodeEditor 
                v-model:code="submission.code" 
                :language="getEditorLanguage(submission.language)"
                :theme="editorTheme"
                @change="onCodeChange"
              />
            </div>
            
            <div class="submission-actions">
              <el-button type="primary" @click="submitSolution" :loading="submitting">
                Submit
              </el-button>
              <el-button @click="resetEditor">Reset</el-button>
              <el-button type="text" @click="toggleEditorTheme">
                Toggle Theme
              </el-button>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <el-dialog
        v-model="showSubmissionDialog"
        title="Submission Details"
        width="80%"
        class="submission-dialog"
      >
        <SubmissionDetailComponent 
          v-if="currentSubmission"
          :submission="currentSubmission"
        />
      </el-dialog>
    </div>
    <div v-else-if="!isLoading" class="not-found">
      <h2>Problem not found</h2>
      <p>The problem you're looking for doesn't exist or you don't have permission to view it.</p>
      <el-button type="primary" @click="$router.push('/problems')">
        Back to Problems
      </el-button>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import MarkdownRenderer from '@/components/markdown/MarkdownRenderer.vue'
import CodeEditor from '@/components/editor/CodeEditor.vue'
import SubmissionDetailComponent from '@/components/submissions/SubmissionDetail.vue'

export default {
  name: 'ProblemDetailView',
  components: {
    MarkdownRenderer,
    CodeEditor,
    SubmissionDetailComponent
  },
  data() {
    return {
      activeTab: 'description',
      submission: {
        code: '// Your C++ solution here\n\n#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your code here\n    \n    return 0;\n}',
        language: 'cpp'
      },
      editorTheme: 'vs',
      submitting: false,
      problemSubmissions: [],
      submissionsLoading: false,
      showSubmissionDialog: false,
      currentSubmission: null
    }
  },
  computed: {
    ...mapGetters({
      problem: 'problems/currentProblem',
      isLoading: 'isLoading',
      isLoggedIn: 'auth/isLoggedIn'
    }),
    problemId() {
      return this.$route.params.id
    }
  },
  methods: {
    ...mapActions({
      fetchProblem: 'problems/fetchProblem',
      fetchSubmissions: 'submissions/fetchSubmissions',
      fetchSubmission: 'submissions/fetchSubmission',
      submitCode: 'submissions/submitCode',
      pollSubmissionStatus: 'submissions/pollSubmissionStatus'
    }),
    async loadProblem() {
      await this.fetchProblem(this.problemId)
    },
    async loadSubmissions() {
      this.submissionsLoading = true
      await this.fetchSubmissions({
        problemId: this.problemId
      })
      this.problemSubmissions = this.$store.getters['submissions/allSubmissions']
      this.submissionsLoading = false
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
    getEditorLanguage(language) {
      const languages = {
        cpp: 'cpp'
        // Add more language mappings as needed
      }
      return languages[language] || language
    },
    onCodeChange(value) {
      this.submission.code = value
    },
    toggleEditorTheme() {
      this.editorTheme = this.editorTheme === 'vs' ? 'vs-dark' : 'vs'
    },
    resetEditor() {
      this.submission.code = '// Your C++ solution here\n\n#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your code here\n    \n    return 0;\n}'
    },
    async submitSolution() {
      if (!this.isLoggedIn) {
        this.$message.warning('Please log in to submit a solution')
        this.$router.push('/login')
        return
      }
      
      this.submitting = true
      
      try {
        const result = await this.submitCode({
          problemId: this.problemId,
          code: this.submission.code,
          language: this.submission.language
        })
        
        if (result) {
          this.$message.success('Solution submitted successfully')
          
          // Poll for submission status
          await this.pollSubmissionStatus(result.id)
          
          // Refresh submissions list
          this.loadSubmissions()
          
          // Switch to submissions tab
          this.activeTab = 'submissions'
        }
      } catch (error) {
        this.$message.error('Failed to submit solution')
        console.error(error)
      } finally {
        this.submitting = false
      }
    },
    async viewSubmission(submissionId) {
      const submission = await this.fetchSubmission(submissionId)
      if (submission) {
        this.currentSubmission = submission
        this.showSubmissionDialog = true
      }
    }
  },
  async mounted() {
    await this.loadProblem()
    if (this.isLoggedIn) {
      this.loadSubmissions()
    }
  },
  watch: {
    problemId(newId, oldId) {
      if (newId !== oldId) {
        this.loadProblem()
        if (this.isLoggedIn) {
          this.loadSubmissions()
        }
      }
    },
    isLoggedIn(newValue) {
      if (newValue && this.activeTab === 'submit') {
        this.loadSubmissions()
      }
    }
  }
}
</script>

<style scoped>
.problem-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.problem-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.problem-header {
  padding: 20px;
  border-bottom: 1px solid #eaeaea;
}

.problem-header h1 {
  margin: 0 0 10px 0;
  color: #303133;
}

.problem-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
}

.problem-stats {
  color: #606266;
  font-size: 14px;
}

.problem-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag-item {
  margin-right: 0;
}

.problem-tabs {
  padding: 20px;
}

.problem-description {
  padding: 0 10px;
}

.submission-form {
  padding: 20px 0;
}

.language-select {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.code-editor {
  height: 500px;
  margin-bottom: 20px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.submission-actions {
  display: flex;
  gap: 10px;
}

.not-found {
  text-align: center;
  padding: 50px 0;
}

.submissions-list {
  margin-top: 20px;
}

.submission-dialog :deep(.el-dialog__body) {
  padding: 0;
}
</style>
