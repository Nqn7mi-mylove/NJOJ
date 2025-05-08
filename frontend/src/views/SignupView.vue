<template>
  <div class="signup-container">
    <div class="signup-card">
      <h2>Create an Account</h2>
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
          <el-button type="primary" native-type="submit" :loading="loading" class="submit-btn">
            Sign Up
          </el-button>
        </el-form-item>
      </el-form>
      
      <div class="form-footer">
        <p>Already have an account? <router-link to="/login">Log in</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'SignupView',
  data() {
    // Custom validator to check if passwords match
    const validatePasswordMatch = (rule, value, callback) => {
      if (value !== this.signupForm.password) {
        callback(new Error('Passwords do not match'))
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
          { required: true, message: 'Please enter a username', trigger: 'blur' },
          { min: 3, max: 20, message: 'Username must be 3-20 characters', trigger: 'blur' }
        ],
        email: [
          { required: true, message: 'Please enter your email', trigger: 'blur' },
          { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
        ],
        full_name: [
          { required: true, message: 'Please enter your full name', trigger: 'blur' }
        ],
        password: [
          { required: true, message: 'Please enter a password', trigger: 'blur' },
          { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
        ],
        confirmPassword: [
          { required: true, message: 'Please confirm your password', trigger: 'blur' },
          { validator: validatePasswordMatch, trigger: 'blur' }
        ]
      },
      loading: false
    }
  },
  methods: {
    ...mapActions({
      signup: 'auth/signup',
      setError: 'setError',
      clearError: 'clearError'
    }),
    async submitForm() {
      this.clearError()
      
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
