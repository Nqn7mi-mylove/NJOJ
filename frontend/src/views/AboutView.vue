<template>
  <div class="about">
    <h1>About Online Judge</h1>
    
    <div class="about-content">
      <div class="section">
        <h2>About the System</h2>
        <p>
          This Online Judge system is a platform designed for programmers to practice and improve their
          coding skills. It provides a collection of programming problems with varying difficulty levels,
          allowing users to submit solutions in C++ (with plans to support more languages in the future).
        </p>
        <p>
          Each submission is automatically evaluated by our judging system, which compiles and runs the code
          in a secure Docker container, testing it against multiple test cases to ensure correctness,
          performance, and memory usage.
        </p>
      </div>
      
      <div class="section">
        <h2>Features</h2>
        <ul>
          <li>Problem repository with markdown support</li>
          <li>VS Code-style editor for code submission</li>
          <li>Automatic judging system</li>
          <li>Support for C++ language</li>
          <li>Administrative tools for problem management</li>
          <li>User authentication and submission tracking</li>
        </ul>
      </div>
      
      <div class="section">
        <h2>Technology Stack</h2>
        <ul>
          <li><strong>Backend:</strong> FastAPI (Python), MongoDB</li>
          <li><strong>Frontend:</strong> Vue.js, Element Plus, Monaco Editor</li>
          <li><strong>Judging System:</strong> Docker</li>
          <li><strong>Server:</strong> Debian 12</li>
        </ul>
      </div>
      
      <div class="section">
        <h2>Getting Started</h2>
        <p>
          To get started, <router-link to="/signup">create an account</router-link> and navigate to the 
          <router-link to="/problems">problems page</router-link> where you can browse available problems.
          Choose a problem, solve it in the editor, and submit your solution for evaluation.
        </p>
        <p>
          You can track your submissions and progress on the 
          <router-link to="/submissions">submissions page</router-link>.
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
