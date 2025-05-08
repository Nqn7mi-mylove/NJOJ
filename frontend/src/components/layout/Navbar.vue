<template>
  <div class="navbar">
    <div class="left-section">
      <div class="logo-container">
        <router-link to="/">
          <h1 class="logo">NJOJ</h1>
        </router-link>
      </div>
      <div class="nav-links">
        <router-link to="/" class="nav-link">首页</router-link>
        <router-link to="/problems" class="nav-link">题库</router-link>
        <router-link to="/submissions" class="nav-link">提交记录</router-link>
        <router-link to="/about" class="nav-link">关于</router-link>
      </div>
    </div>
    <div class="right-section">
      <!-- 导航条中的管理员和个人资料链接 -->
      <template v-if="isLoggedIn">
        <div class="nav-links">
          <router-link v-if="isAdmin" to="/admin" class="nav-link admin-link">管理后台</router-link>
          <router-link to="/profile" class="nav-link profile-link">个人资料</router-link>
        </div>
        
        <!-- 用户菜单 -->
        <div class="user-menu">
          <el-dropdown trigger="click">
            <span class="user-dropdown">
              <span class="username">{{ currentUser.username }}</span>
              <i class="el-icon-arrow-down"></i>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </template>
      <template v-else>
        <div class="auth-buttons">
          <router-link to="/login" class="login-btn">登录</router-link>
          <router-link to="/signup" class="signup-btn">注册</router-link>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
  name: 'Navbar',
  computed: {
    ...mapGetters({
      isLoggedIn: 'auth/isLoggedIn',
      currentUser: 'auth/currentUser',
      isAdmin: 'auth/isAdmin'
    })
  },
  methods: {
    ...mapActions({
      logoutAction: 'auth/logout'
    }),
    async logout() {
      await this.logoutAction()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.left-section {
  display: flex;
  align-items: center;
}

.logo-container {
  display: flex;
  align-items: center;
  margin-right: 40px;
}

.logo-container a {
  text-decoration: none;
}

.logo {
  margin: 0;
  font-size: 24px;
  color: #409EFF;
}

.nav-links {
  display: flex;
  gap: 30px;
}

.nav-link {
  text-decoration: none;
  color: #606266;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s;
  padding: 6px 0;
  position: relative;
}

.nav-link:after {
  content: '';
  position: absolute;
  width: 0;
  height: 2px;
  bottom: 0;
  left: 0;
  background-color: #409EFF;
  transition: width 0.3s;
}

.nav-link:hover,
.nav-link.router-link-exact-active {
  color: #409EFF;
}

.nav-link:hover:after,
.nav-link.router-link-exact-active:after {
  width: 100%;
}

.right-section {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: color 0.3s;
}

.user-dropdown:hover {
  color: #409EFF;
}

.username {
  font-weight: 500;
  color: inherit;
  margin-right: 5px;
  font-size: 16px;
}

.auth-buttons {
  display: flex;
  gap: 10px;
}

.login-btn,
.signup-btn {
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s;
}

.login-btn {
  color: #409EFF;
  border: 1px solid #409EFF;
}

.login-btn:hover {
  background-color: rgba(64, 158, 255, 0.1);
}

.signup-btn {
  color: #fff;
  background-color: #409EFF;
}

.signup-btn:hover {
  background-color: #66b1ff;
}

.admin-link {
  color: #E6A23C;
  font-weight: 600;
}

.admin-link:after {
  background-color: #E6A23C;
}

.profile-link {
  color: #67C23A;
}

.profile-link:after {
  background-color: #67C23A;
}
</style>
