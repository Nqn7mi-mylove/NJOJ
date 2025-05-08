<template>
  <div class="profile-view">
    <h1>My Profile</h1>
    
    <div class="profile-container" v-loading="loading">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="Profile Information" name="profile">
          <el-form
            ref="profileForm"
            :model="formData"
            :rules="rules"
            label-position="top"
            class="profile-form"
          >
            <el-form-item label="Username" prop="username">
              <el-input v-model="formData.username" disabled></el-input>
            </el-form-item>
            
            <el-form-item label="Email" prop="email">
              <el-input v-model="formData.email" type="email"></el-input>
            </el-form-item>
            
            <el-form-item label="Full Name" prop="full_name">
              <el-input v-model="formData.full_name"></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="updateProfile" :loading="updating">
                Update Profile
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="Change Password" name="password">
          <el-form
            ref="passwordForm"
            :model="passwordData"
            :rules="passwordRules"
            label-position="top"
            class="password-form"
          >
            <el-form-item label="Current Password" prop="current_password">
              <el-input
                v-model="passwordData.current_password"
                type="password"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item label="New Password" prop="new_password">
              <el-input
                v-model="passwordData.new_password"
                type="password"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item label="Confirm New Password" prop="confirm_password">
              <el-input
                v-model="passwordData.confirm_password"
                type="password"
                show-password
              ></el-input>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="changePassword" :loading="changingPassword">
                Change Password
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="Solved Problems" name="solved">
          <div class="solved-problems">
            <div v-if="solvedProblems.length === 0" class="empty-state">
              <p>You haven't solved any problems yet.</p>
              <el-button type="primary" @click="$router.push('/problems')">
                Browse Problems
              </el-button>
            </div>
            
            <el-table v-else :data="solvedProblems">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="title" label="Title">
                <template #default="scope">
                  <router-link :to="`/problems/${scope.row.id}`">
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
        callback(new Error('Passwords do not match'))
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
          { required: true, message: 'Please enter your email', trigger: 'blur' },
          { type: 'email', message: 'Please enter a valid email address', trigger: 'blur' }
        ],
        full_name: [
          { required: true, message: 'Please enter your full name', trigger: 'blur' }
        ]
      },
      passwordRules: {
        current_password: [
          { required: true, message: 'Please enter your current password', trigger: 'blur' }
        ],
        new_password: [
          { required: true, message: 'Please enter a new password', trigger: 'blur' },
          { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
        ],
        confirm_password: [
          { required: true, message: 'Please confirm your new password', trigger: 'blur' },
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
        this.setError('Failed to load solved problems')
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
          this.$message.success('Profile updated successfully')
        } else {
          this.$message.error('Failed to update profile')
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
          
          this.$message.success('Password changed successfully')
          
          // Reset the form
          this.passwordData = {
            current_password: '',
            new_password: '',
            confirm_password: ''
          }
        } catch (error) {
          console.error('Error changing password', error)
          this.setError(error.response?.data?.detail || 'Failed to change password')
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
