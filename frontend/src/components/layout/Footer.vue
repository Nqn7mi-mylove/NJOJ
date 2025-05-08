<template>
  <div class="footer">
    <p>&copy; {{ currentYear }} Online Judge System. All rights reserved.</p>
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
  padding: 10px 0;
  text-align: center;
  color: #909399;
  font-size: 14px;
}
</style>
