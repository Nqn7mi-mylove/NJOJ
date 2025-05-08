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
  width: 100%;
  overflow-x: hidden;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

#app {
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
}

.layout-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.el-header {
  padding: 0;
  border-bottom: 1px solid #eaeaea;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
  flex: 1;
  overflow-x: hidden;
  box-sizing: border-box;
  width: 100%;
}

.el-footer {
  padding: 20px;
  text-align: center;
  font-size: 14px;
  color: #909399;
  border-top: 1px solid #eaeaea;
  width: 100%;
  box-sizing: border-box;
}
</style>
