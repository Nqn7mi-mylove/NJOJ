<template>
  <div class="profile-view">
    <h1>我的个人资料</h1>
    
    <div class="profile-container" v-loading="loading">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="资料信息" name="profile">
          <el-form
            ref="profileForm"
            :model="formData"
            :rules="rules"
            label-position="top"
            class="profile-form"
          >
            <el-form-item label="用户名" prop="username">
              <el-input v-model="formData.username" disabled></el-input>
            </el-form-item>
            
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="formData.email" type="email"></el-input>
            </el-form-item>
            
            <el-form-item label="姓名" prop="full_name">
              <el-input v-model="formData.full_name"></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="updating">
                更新资料
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="修改密码" name="password">
          <el-form
            ref="passwordForm"
            :model="passwordData"
            :rules="passwordRules"
            label-position="top"
            class="password-form"
          >
            <el-form-item label="当前密码" prop="current_password">
              <el-input
                v-model="passwordData.current_password"
                type="password"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordData.new_password"
                type="password"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item label="确认新密码" prop="confirm_password">
              <el-input
                v-model="passwordData.confirm_password"
                type="password"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="changingPassword">
                修改密码
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="已解决题目" name="solved">
          <div class="solved-problems">
            <div v-if="solvedProblems.length === 0" class="empty-state">
              <p>您还没有解决任何题目。</p>
              <el-button type="primary" @click="$router.push('/problems')">
                浏览题目
              </el-button>
            </div>
            
            <el-table v-else :data="solvedProblems">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="题目">
                <template #default="scope">
                  <router-link :to="`/problems/${scope.row.id}`">
                    {{ scope.row.title }}
                  </router-link>
                </template>
              </el-table-column>
              <el-table-column prop="difficulty" label="难度" width="120">
                <template #default="scope">
                  <el-tag :type="getDifficultyType(scope.row.difficulty)">
                    {{ getChineseDifficulty(scope.row.difficulty) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="标签" width="220">
                <template #default="scope">
                  <div class="tag-container">
                    <el-tag 
                      v-for="tag in scope.row.tags" 
                      :key="tag" 
                      size="small"
                      effect="plain"
                      class="tag-item"
                    >
                      {{ getChineseTag(tag) }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import api from '@/services/api'

export default {
  name: 'ProfileView',
  data() {
    // Custom validator to check if passwords match
    const validatePasswordMatch = (rule, value, callback) => {
      if (value !== this.passwordData.new_password) {
        callback(new Error('密码不匹配'))
      } else {
        callback()
      }
    }
    
    return {
      activeTab: 'profile',
      formData: {
        username: '',
        email: '',
        full_name: ''
      },
      passwordData: {
        current_password: '',
        new_password: '',
        confirm_password: ''
      },
      rules: {
        email: [
          { required: true, message: '请输入您的电子邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入有效的电子邮箱地址', trigger: 'blur' }
        ],
        full_name: [
          { required: true, message: '请输入您的姓名', trigger: 'blur' }
        ]
      },
      passwordRules: {
        current_password: [
          { required: true, message: '请输入您的当前密码', trigger: 'blur' }
        ],
        new_password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码必须至少为6个字符', trigger: 'blur' }
        ],
        confirm_password: [
          { required: true, message: '请确认您的新密码', trigger: 'blur' },
          { validator: validatePasswordMatch, trigger: 'blur' }
        ]
      },
      solvedProblems: [],
      loading: false,
      updating: false,
      changingPassword: false
    }
  },
  computed: {
    ...mapGetters({
      currentUser: 'auth/currentUser',
      isLoggedIn: 'auth/isLoggedIn'
    })
  },
  methods: {
    ...mapActions({
      updateProfileAction: 'auth/updateProfile',
      setError: 'setError',
      clearError: 'clearError'
    }),
    loadUserData() {
      if (!this.currentUser) return
      
      this.formData = {
        username: this.currentUser.username,
        email: this.currentUser.email,
        full_name: this.currentUser.full_name || ''
      }
    },
    async loadSolvedProblems() {
      if (!this.currentUser || !this.currentUser.solved_problems || this.currentUser.solved_problems.length === 0) {
        return
      }
      
      this.loading = true
      
      try {
        const problemIds = this.currentUser.solved_problems
        
        // Fetch details for each solved problem
        this.solvedProblems = []
        
        for (const id of problemIds) {
          try {
            const response = await api.get(`/problems/${id}`)
            this.solvedProblems.push(response.data)
          } catch (error) {
            console.error(`Error loading problem ${id}`, error)
          }
        }
      } catch (error) {
        console.error('Error loading solved problems', error)
        this.setError('加载已解决题目失败')
      } finally {
        this.loading = false
      }
    },
    async updateProfile() {
      this.clearError()
      
      try {
        await this.$refs.profileForm.validate()
        
        this.updating = true
        
        const success = await this.updateProfileAction({
          email: this.formData.email,
          full_name: this.formData.full_name
        })
        
        if (success) {
          this.$message.success('个人资料更新成功')
        } else {
          this.$message.error('更新个人资料失败')
        }
      } catch (error) {
        // Form validation failed
        console.error('Form validation failed', error)
      } finally {
        this.updating = false
      }
    },
    async changePassword() {
      this.clearError()
      
      try {
        await this.$refs.passwordForm.validate()
        
        this.changingPassword = true
        
        try {
          await api.put('/users/me/password', {
            current_password: this.passwordData.current_password,
            new_password: this.passwordData.new_password
          })
          
          this.$message.success('密码修改成功')
          
          // Reset the form
          this.passwordData = {
            current_password: '',
            new_password: '',
            confirm_password: ''
          }
        } catch (error) {
          console.error('Error changing password', error)
          this.setError(error.response?.data?.detail || '修改密码失败')
        }
      } catch (error) {
        // Form validation failed
        console.error('Form validation failed', error)
      } finally {
        this.changingPassword = false
      }
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
    getChineseTag(tag) {
      const tagMap = {
        'array': '数组',
        'string': '字符串',
        'hash-table': '哈希表',
        'dynamic-programming': '动态规划',
        'math': '数学',
        'sorting': '排序',
        'greedy': '贪心算法',
        'depth-first-search': '深度优先搜索',
        'binary-search': '二分搜索',
        'tree': '树',
        'graph': '图',
        'breadth-first-search': '广度优先搜索'
      }
      return tagMap[tag] || tag
    }
  },
  mounted() {
    if (!this.isLoggedIn) {
      this.$router.push('/login')
      return
    }
    
    this.loadUserData()
    this.loadSolvedProblems()
  },
  watch: {
    currentUser(newUser) {
      if (newUser) {
        this.loadUserData()
        this.loadSolvedProblems()
      }
    }
  }
}
</script>

<style scoped>
.profile-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

.profile-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.profile-form,
.password-form {
  max-width: 500px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #909399;
}

.empty-state p {
  margin-bottom: 20px;
}

.tag-container {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag-item {
  margin-right: 0;
}

a {
  text-decoration: none;
  color: #409EFF;
}
</style>
