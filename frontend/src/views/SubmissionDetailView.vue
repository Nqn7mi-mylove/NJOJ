<template>
  <div class="submission-detail-view">
    <div class="page-header">
      <h1>Submission Details</h1>
      <div class="page-actions">
        <el-button @click="$router.push('/submissions')">
          Back to Submissions
        </el-button>
      </div>
    </div>
    
    <div v-if="submission" class="submission-container" v-loading="loading">
      <div class="problem-info">
        <h2>
          <router-link :to="`/problems/${submission.problem_id}`">
            {{ problemTitle }}
          </router-link>
        </h2>
      </div>
      
      <SubmissionDetail :submission="submission" />
    </div>
    
    <div v-else-if="!loading" class="not-found">
      <h2>Submission not found</h2>
      <p>The submission you're looking for doesn't exist or you don't have permission to view it.</p>
      <el-button type="primary" @click="$router.push('/submissions')">
        Back to Submissions
      </el-button>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import SubmissionDetail from '@/components/submissions/SubmissionDetail.vue'
import api from '@/services/api'

export default {
  name: 'SubmissionDetailView',
  components: {
    SubmissionDetail
  },
  data() {
    return {
      problemTitle: '',
      loading: false
    }
  },
  computed: {
    ...mapGetters({
      submission: 'submissions/currentSubmission',
      isLoggedIn: 'auth/isLoggedIn'
    }),
    submissionId() {
      return this.$route.params.id
    }
  },
  methods: {
    ...mapActions({
      fetchSubmission: 'submissions/fetchSubmission',
      setError: 'setError'
    }),
    async loadSubmission() {
      this.loading = true
      
      try {
        await this.fetchSubmission(this.submissionId)
        
        if (this.submission) {
          await this.loadProblemDetails()
        }
      } catch (error) {
        console.error('Error loading submission', error)
        this.setError('Failed to load submission details')
      } finally {
        this.loading = false
      }
    },
    async loadProblemDetails() {
      try {
        const response = await api.get(`/problems/${this.submission.problem_id}`)
        this.problemTitle = response.data.title
      } catch (error) {
        console.error('Error loading problem details', error)
        this.problemTitle = `Problem #${this.submission.problem_id}`
      }
    }
  },
  async mounted() {
    if (!this.isLoggedIn) {
      this.$router.push('/login')
      return
    }
    
    await this.loadSubmission()
  },
  watch: {
    submissionId(newId, oldId) {
      if (newId !== oldId) {
        this.loadSubmission()
      }
    }
  }
}
</script>

<style scoped>
.submission-detail-view {
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

.submission-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.problem-info {
  padding: 20px;
  border-bottom: 1px solid #eaeaea;
}

.problem-info h2 {
  margin: 0;
  font-size: 1.5rem;
}

.problem-info a {
  text-decoration: none;
  color: #409EFF;
}

.not-found {
  text-align: center;
  padding: 50px 0;
}
</style>
