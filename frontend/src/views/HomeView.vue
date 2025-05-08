<template>
  <div class="home">
    <div class="hero">
      <h1>NJOJ</h1>
      <p>创新的智能在线判题系统，支持AI评价功能</p>
      <div class="action-buttons">
        <el-button type="primary" size="large" @click="$router.push('/problems')">
          开始编程
        </el-button>
        <el-button v-if="!isLoggedIn" size="large" @click="$router.push('/signup')">
          注册账号
        </el-button>
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
    getChineseDifficulty(difficulty) {
      const difficultyMap = {
        easy: '简单',
        medium: '中等',
        hard: '困难'
      }
      return difficultyMap[difficulty] || difficulty
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
  padding: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: calc(100vh - 120px); /* 固定高度以防止滚动 */
  overflow: hidden;
}

.hero {
  text-align: center;
  padding: 40px 0;
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hero h1 {
  font-size: 4rem;
  color: #409EFF;
  margin-bottom: 20px;
  font-weight: 700;
  letter-spacing: 1px;
}

.hero p {
  font-size: 1.4rem;
  color: #606266;
  margin-bottom: 40px;
  max-width: 80%;
  line-height: 1.6;
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
