<template>
  <div class="footer">
    <span>&copy; {{ currentYear }} NJ Online Judge</span>
  </div>
</template>

<script>
export default {
  name: 'Footer',
  data() {
    return {
      currentYear: new Date().getFullYear()
    }
  }
}
</script>

<style scoped>
.footer {
  text-align: center;
  padding: 10px 0;
  color: #909399;
  font-size: 13px;
  border-top: 1px solid #eaeaea;
}
</style>
