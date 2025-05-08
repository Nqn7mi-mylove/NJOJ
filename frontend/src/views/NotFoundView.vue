<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>The page you are looking for does not exist or has been moved.</p>
      <el-button type="primary" @click="$router.push('/')">
        Back to Home
      </el-button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFoundView'
}
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 120px);
  text-align: center;
}

.not-found-content {
  max-width: 500px;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 8rem;
  margin: 0;
  color: #409EFF;
  line-height: 1;
}

h2 {
  font-size: 2rem;
  margin: 0 0 20px 0;
  color: #303133;
}

p {
  margin-bottom: 30px;
  color: #606266;
}
</style>
