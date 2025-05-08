<template>
  <div class="system-settings-container">
    <h1>系统设置</h1>
    
    <el-card class="settings-card">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else>
        <el-form label-position="top" :model="settings" ref="settingsForm">
          <el-form-item label="用户注册">
            <el-switch
              v-model="settings.allow_signup"
              active-text="开启注册"
              inactive-text="关闭注册"
              @change="saveSettings"
            />
            <div class="setting-description">
              {{ settings.allow_signup ? '当前允许新用户自行注册账号' : '当前禁止新用户自行注册账号' }}
            </div>
          </el-form-item>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script>
import api from '@/services/api'
import { ElMessage } from 'element-plus'

export default {
  name: 'SystemSettingsView',
  data() {
    return {
      loading: true,
      settings: {
        allow_signup: true
      }
    }
  },
  created() {
    this.loadSettings()
  },
  methods: {
    async loadSettings() {
      this.loading = true
      try {
        const response = await api.get('/system-config')
        this.settings = response.data
      } catch (error) {
        console.error('加载系统设置失败', error)
        ElMessage.error('加载系统设置失败')
      } finally {
        this.loading = false
      }
    },
    async saveSettings() {
      try {
        await api.put('/system-config', {
          allow_signup: this.settings.allow_signup
        })
        ElMessage.success('设置已保存')
      } catch (error) {
        console.error('保存设置失败', error)
        ElMessage.error('保存设置失败')
        // 回滚设置状态
        this.loadSettings()
      }
    }
  }
}
</script>

<style scoped>
.system-settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.settings-card {
  margin-top: 20px;
}

.loading-container {
  padding: 20px 0;
}

.setting-description {
  color: #909399;
  font-size: 14px;
  margin-top: 5px;
}
</style>
