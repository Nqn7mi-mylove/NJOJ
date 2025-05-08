<template>
  <div class="home">
    <div class="hero">
      <h1>Online Judge System</h1>
      <p>Improve your coding skills by solving programming problems</p>
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="$router.push('/problems')">
          Start Coding
        </el-button>
        <el-button v-if="!isLoggedIn" size="large" @click="$router.push('/signup')">
          Sign Up
        </el-button>
      </div>
    </div>

    <div class="features">
      <h2>Features</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <el-icon><Document /></el-icon>
          <h3>Problem Bank</h3>
          <p>Access a growing collection of programming problems with markdown support</p>
        </div>
        <div class="feature-card">
          <el-icon><Edit /></el-icon>
          <h3>VS Code Editor</h3>
          <p>Solve problems using our embedded VS Code-style editor</p>
        </div>
        <div class="feature-card">
          <el-icon><Cpu /></el-icon>
          <h3>Code Evaluation</h3>
          <p>Submit your code and get instant feedback on your solution</p>
        </div>
        <div class="feature-card">
          <el-icon><Trophy /></el-icon>
          <h3>Track Progress</h3>
          <p>Monitor your progress and improve your problem-solving skills</p>
        </div>
      </div>
    </div>

    <div class="recent-problems">
      <h2>Recent Problems</h2>
      <el-table :data="recentProblems" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="Title">
          <template #default="scope">
            <router-link :to="`/problems/${scope.row.id}`">{{ scope.row.title }}</router-link>
          </template>
        </el-table-column>
        <el-table-column prop="difficulty" label="Difficulty" width="120">
          <template #default="scope">
            <el-tag :type="getDifficultyType(scope.row.difficulty)">
              {{ scope.row.difficulty }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Acceptance" width="120">
          <template #default="scope">
            {{ calculateAcceptanceRate(scope.row) }}%
          </template>
        </el-table-column>
      </el-table>
      <div class="view-all">
        <el-button type="text" @click="$router.push('/problems')">View All Problems</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'HomeView',
  data() {
    return {
      recentProblems: []
    }
  },
  computed: {
    ...mapGetters({
      isLoggedIn: 'auth/isLoggedIn'
    })
  },
  methods: {
    ...mapActions({
      fetchProblems: 'problems/fetchProblems'
    }),
    async loadRecentProblems() {
      await this.fetchProblems({ limit: 5 })
      this.recentProblems = this.$store.getters['problems/allProblems']
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
    }
  },
  mounted() {
    this.loadRecentProblems()
  }
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.hero {
  text-align: center;
  margin: 40px 0 60px;
}

.hero h1 {
  font-size: 3rem;
  color: #409EFF;
  margin-bottom: 10px;
}

.hero p {
  font-size: 1.2rem;
  color: #606266;
  margin-bottom: 30px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.features {
  margin: 60px 0;
}

.features h2 {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 40px;
  color: #303133;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card i {
  font-size: 40px;
  color: #409EFF;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 15px;
  color: #303133;
}

.feature-card p {
  color: #606266;
}

.recent-problems {
  margin: 60px 0;
}

.recent-problems h2 {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 40px;
  color: #303133;
}

.view-all {
  text-align: center;
  margin-top: 20px;
}

a {
  text-decoration: none;
  color: #409EFF;
}
</style>
