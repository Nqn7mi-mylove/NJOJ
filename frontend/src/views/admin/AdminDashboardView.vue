<template>
  <div class="admin-dashboard">
    <h1>管理员控制台</h1>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>题目管理</span>
            </div>
          </template>
          <div class="card-content">
            <p>添加、编辑和管理在线评判系统的题目库</p>
            <div class="action-buttons">
              <el-button type="primary" @click="$router.push('/admin/problems')">管理题目</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>系统设置</span>
            </div>
          </template>
          <div class="card-content">
            <p>配置在线评判系统的全局设置，包括用户注册控制等功能</p>
            <div class="action-buttons">
              <el-button type="primary" @click="$router.push('/admin/settings')">系统设置</el-button>
            </div>
          </div>
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
  },
  mounted() {
    if (!this.isAdmin) {
      this.$router.push('/')
    }
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

.action-buttons {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.card-content p {
  color: #606266;
  line-height: 1.6;
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
