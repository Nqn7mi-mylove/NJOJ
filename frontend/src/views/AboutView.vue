<template>
  <div class="about">
    <h1>关于 NJOJ</h1>
    
    <div class="about-content">
      <div class="section">
        <h2>关于系统</h2>
        <p>
          NJOJ（在线评测系统）是一个为程序员提供练习和提高编程技能的平台。系统提供了各种难度级别的编程问题，
          用户可以提交C++语言的解决方案（未来计划支持更多语言）。
        </p>
        <p>
          每次提交都会由我们的评判系统自动评估，系统会在安全的Docker容器中编译并运行代码，
          使用多个测试用例对其进行测试，以确保代码的正确性、性能和内存使用情况符合要求。
        </p>
        <p>
          该系统为开发者本科毕设，借助Windsurf ide从零开发。
        </p>
      </div>
      
      <div class="section">
        <h2>功能特点</h2>
        <ul>
          <li>题库管理系统，支持Markdown格式题目描述</li>
          <li>代码提交和自动评判系统</li>
          <li>基于Docker的隔离评判环境</li>
          <li>支持C++语言（计划扩展更多语言）</li>
          <li>管理员题目管理和系统配置工具</li>
          <li>用户认证和提交记录跟踪</li>
        </ul>
      </div>
      
      <div class="section">
        <h2>技术栈</h2>
        <ul>
          <li><strong>后端:</strong> FastAPI (Python), MongoDB</li>
          <li><strong>前端:</strong> Vue.js, Element Plus</li>
          <li><strong>评判系统:</strong> Docker</li>
          <li><strong>服务器:</strong> Debian 12</li>
        </ul>
      </div>
      
      <div class="section">
        <h2>开始使用</h2>
        <p>
          要开始使用，请先<router-link to="/signup">创建一个账户</router-link>，然后前往<router-link to="/problems">题目页面</router-link>浏览可用的题目。
          选择一个题目，编写解决方案，并提交代码进行评估。
        </p>
        <p>
          您可以在<router-link to="/submissions">提交记录页面</router-link>跟踪您的提交和进度。
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AboutView'
}
</script>

<style scoped>
.about {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 40px;
  color: #303133;
  text-align: center;
}

.about-content {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.section {
  margin-bottom: 30px;
}

.section:last-child {
  margin-bottom: 0;
}

h2 {
  color: #409EFF;
  font-size: 1.5rem;
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 1px solid #EBEEF5;
}

p {
  line-height: 1.6;
  margin-bottom: 15px;
  color: #606266;
}

ul {
  padding-left: 20px;
  color: #606266;
}

li {
  margin-bottom: 8px;
  line-height: 1.6;
}

a {
  color: #409EFF;
  text-decoration: none;
}
</style>
