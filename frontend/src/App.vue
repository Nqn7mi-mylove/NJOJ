<template>
  <div id="app">
    <el-container class="layout-container">
      <el-header>
        <Navbar />
      </el-header>
      <el-main>
        <router-view />
      </el-main>
      <el-footer>
        <Footer />
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import Navbar from '@/components/layout/Navbar.vue'
import Footer from '@/components/layout/Footer.vue'

export default {
  name: 'App',
  components: {
    Navbar,
    Footer
  }
}
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

#app {
  height: 100vh;
}

.layout-container {
  height: 100%;
}

.el-header {
  padding: 0;
  border-bottom: 1px solid #eaeaea;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
}

.el-footer {
  padding: 20px;
  text-align: center;
  font-size: 14px;
  color: #909399;
  border-top: 1px solid #eaeaea;
}
</style>
