<template>
  <div class="navbar">
    <div class="logo-container">
      <router-link to="/">
        <h1 class="logo">Online Judge</h1>
      </router-link>
    </div>
    <div class="nav-links">
      <router-link to="/" class="nav-link">Home</router-link>
      <router-link to="/problems" class="nav-link">Problems</router-link>
      <router-link to="/submissions" class="nav-link">Submissions</router-link>
      <router-link to="/about" class="nav-link">About</router-link>
    </div>
    <div class="user-menu">
      <template v-if="isLoggedIn">
        <el-dropdown trigger="click">
          <span class="user-dropdown">
            {{ currentUser.username }} <i class="el-icon-arrow-down"></i>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-if="isAdmin">
                <router-link to="/admin">Admin Dashboard</router-link>
              </el-dropdown-item>
              <el-dropdown-item>
                <router-link to="/profile">Profile</router-link>
              </el-dropdown-item>
              <el-dropdown-item @click="logout">Logout</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </template>
      <template v-else>
        <router-link to="/login" class="login-btn">Login</router-link>
        <router-link to="/signup" class="signup-btn">Sign Up</router-link>
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
}

.logo-container {
  display: flex;
  align-items: center;
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
  gap: 20px;
}

.nav-link {
  text-decoration: none;
  color: #606266;
  font-size: 16px;
  transition: color 0.3s;
}

.nav-link:hover,
.nav-link.router-link-exact-active {
  color: #409EFF;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-dropdown {
  cursor: pointer;
  color: #606266;
  font-size: 16px;
}

.user-dropdown:hover {
  color: #409EFF;
}

.login-btn,
.signup-btn {
  padding: 8px 16px;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
}

.login-btn {
  color: #409EFF;
  border: 1px solid #409EFF;
}

.signup-btn {
  color: #fff;
  background-color: #409EFF;
}
</style>
