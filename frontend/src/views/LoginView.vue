<template>
  <div class="login-container">
    <div class="login-card">
      <h2>登录在线评测系统</h2>
      <el-form
        ref="loginForm"
        :model="loginForm"
        :rules="rules"
        label-position="top"
        @submit.prevent="submitForm"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" class="submit-btn">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="form-footer">
        <p>还没有账号？ <router-link to="/signup">立即注册</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'LoginView',
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    ...mapActions({
      login: 'auth/login',
      setError: 'setError',
      clearError: 'clearError'
    }),
    async submitForm() {
      this.clearError()
      
      try {
        await this.$refs.loginForm.validate()
        
        this.loading = true
        const success = await this.login({
          username: this.loginForm.username,
          password: this.loginForm.password
        })
        
        if (success) {
          // Check if there's a redirect URL in query params
          const redirectUrl = this.$route.query.redirect || '/'
          this.$router.push(redirectUrl)
        }
      } catch (error) {
        // Form validation failed
        console.error('Form validation failed', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.submit-btn {
  width: 100%;
  margin-top: 10px;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
  font-size: 14px;
  color: #606266;
}

.form-footer a {
  color: #409EFF;
  text-decoration: none;
}
</style>
