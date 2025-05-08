<template>
  <div class="signup-container">
    <div class="signup-card">
      <h2>创建账号</h2>
      
      <el-alert
        v-if="!allowSignup"
        title="注册功能已关闭"
        type="error"
        description="管理员已关闭注册功能。如需要账号，请联系系统管理员。"
        show-icon
        :closable="false"
        class="signup-alert"
      />
      <el-form
        ref="signupForm"
        :model="signupForm"
        :rules="rules"
        label-position="top"
        @submit.prevent="submitForm"
      >
        <el-form-item label="Username" prop="username">
          <el-input v-model="signupForm.username" placeholder="Choose a username"></el-input>
        </el-form-item>
        
        <el-form-item label="Email" prop="email">
          <el-input v-model="signupForm.email" type="email" placeholder="Enter your email"></el-input>
        </el-form-item>
        
        <el-form-item label="Full Name" prop="full_name">
          <el-input v-model="signupForm.full_name" placeholder="Enter your full name"></el-input>
        </el-form-item>
        
        <el-form-item label="Password" prop="password">
          <el-input
            v-model="signupForm.password"
            type="password"
            placeholder="Choose a password"
            show-password
          ></el-input>
        </el-form-item>
        
        <el-form-item label="Confirm Password" prop="confirmPassword">
          <el-input
            v-model="signupForm.confirmPassword"
            type="password"
            placeholder="Confirm your password"
            show-password
          ></el-input>
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            native-type="submit" 
            :loading="loading" 
            class="submit-btn"
            :disabled="!allowSignup"
          >
            注册
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="form-footer">
        <p>已有账号？ <router-link to="/login">登录</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'
import api from '@/services/api'

export default {
  name: 'SignupView',
  data() {
    // Custom validator to check if passwords match
    const validatePasswordMatch = (rule, value, callback) => {
      if (value !== this.signupForm.password) {
        callback(new Error('密码不匹配'))
      } else {
        callback()
      }
    }
    
    return {
      signupForm: {
        username: '',
        email: '',
        full_name: '',
        password: '',
        confirmPassword: ''
      },
      rules: {
        username: [
          { required: true, message: '请输入用户名', trigger: 'blur' },
          { min: 3, max: 20, message: '用户名必须在3-20个字符之间', trigger: 'blur' }
        ],
        email: [
          { required: true, message: '请输入您的电子邮箱', trigger: 'blur' },
          { type: 'email', message: '请输入有效的电子邮箱地址', trigger: 'blur' }
        ],
        full_name: [
          { required: true, message: '请输入您的全名', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' },
          { min: 6, message: '密码至少需要六个字符', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: '请确认您的密码', trigger: 'blur' },
          { validator: validatePasswordMatch, trigger: 'blur' }
        ]
      },
      loading: false,
      allowSignup: true
    }
  },
  created() {
    this.checkSignupStatus()
  },
  methods: {
    ...mapActions({
      signup: 'auth/signup',
      setError: 'setError',
      clearError: 'clearError'
    }),
    async checkSignupStatus() {
      try {
        const response = await api.get('/system-config')
        this.allowSignup = response.data.allow_signup
      } catch (error) {
        console.error('获取注册状态失败', error)
      }
    },
    async submitForm() {
      this.clearError()
      
      // 如果注册被禁用，直接返回
      if (!this.allowSignup) {
        this.setError('系统当前不允许注册新用户')
        return
      }
      
      try {
        await this.$refs.signupForm.validate()
        
        this.loading = true
        
        // Create user data object (exclude confirmPassword)
        const userData = {
          username: this.signupForm.username,
          email: this.signupForm.email,
          full_name: this.signupForm.full_name,
          password: this.signupForm.password
        }
        
        const success = await this.signup(userData)
        
        if (success) {
          this.$router.push('/')
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
.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
  padding: 20px;
}

.signup-card {
  width: 100%;
  max-width: 500px;
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.signup-alert {
  margin-bottom: 20px;
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
