<template>
  <div class="submission-detail">
    <div class="submission-header">
      <div class="submission-info">
        <div class="info-item">
          <span class="label">状态:</span>
          <el-tag :type="getStatusType(submission.status)">
            {{ formatStatus(submission.status) }}
          </el-tag>
        </div>
        <div class="info-item">
          <span class="label">编程语言:</span>
          <span>{{ submission.language }}</span>
        </div>
        <div class="info-item">
          <span class="label">执行时间:</span>
          <span>{{ submission.time_used }} ms</span>
        </div>
        <div class="info-item">
          <span class="label">内存占用:</span>
          <span>{{ submission.memory_used }} KB</span>
        </div>
        <div class="info-item">
          <span class="label">提交时间:</span>
          <span>{{ formatDate(submission.submitted_at) }}</span>
        </div>
      </div>
    </div>

    <div class="code-section">
      <h3>提交的代码</h3>
      <div class="code-viewer">
        <CodeEditor 
          :code="submission.code" 
          :language="getEditorLanguage(submission.language)"
          :readOnly="true"
          theme="vs-dark"
        />
      </div>
    </div>

    <div v-if="submission.error_message" class="error-section">
      <h3>错误信息</h3>
      <div class="error-message">
        <pre>{{ submission.error_message }}</pre>
      </div>
    </div>

    <div v-if="submission.test_case_results && submission.test_case_results.length > 0" class="results-section">
      <h3>测试用例结果</h3>
      <el-collapse>
        <el-collapse-item 
          v-for="(result, index) in submission.test_case_results" 
          :key="result.test_case_id || index"
          :title="`测试用例 #${index + 1}: ${formatStatus(result.status)}`"
          :name="index"
        >
          <div class="test-case-result">
            <div class="result-info">
              <div class="info-item">
                <span class="label">状态:</span>
                <el-tag :type="getStatusType(result.status)">{{ formatStatus(result.status) }}</el-tag>
              </div>
              <div class="info-item">
                <span class="label">执行时间:</span>
                <span>{{ result.time_used }} ms</span>
              </div>
              <div class="info-item">
                <span class="label">内存占用:</span>
                <span>{{ result.memory_used }} KB</span>
              </div>
            </div>
            
            <div v-if="result.output" class="output-section">
              <h4>输出结果:</h4>
              <pre>{{ result.output }}</pre>
            </div>
            
            <div v-if="result.error_message" class="error-section">
              <h4>错误信息:</h4>
              <pre>{{ result.error_message }}</pre>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 大模型评估结果部分 -->
    <div v-if="submission.llm_evaluation" class="llm-evaluation-section">
      <h3>AI代码评估</h3>

      <div class="evaluation-container">
        <!-- 评估失败消息 -->
        <div v-if="evaluationFailed" class="evaluation-error">
          <el-alert
            title="AI评估暂时不可用"
            type="info"
            description="我们的AI评估系统目前遇到了一些困难。您的代码已经成功提交并通过测试用例评判，但AI质量评估暂时无法提供。"
            show-icon
            :closable="false"
          />
        </div>

        <!-- 正常显示评估结果 -->
        <template v-else>
          <!-- 错误分析部分 -->
          <div v-if="submission.llm_evaluation.error_types && submission.llm_evaluation.error_types.length > 0" class="error-analysis">
            <h4>错误分析</h4>
            <div class="error-types">
              <span class="label">错误类型:</span>
              <el-tag 
                v-for="(error, index) in submission.llm_evaluation.error_types" 
                :key="`error-type-${index}`"
                :type="getErrorTagType(error)"
                effect="dark"
                class="error-tag"
              >
                {{ error }}
              </el-tag>
            </div>

            <div v-if="submission.llm_evaluation.explanation" class="explanation">
              <p>{{ submission.llm_evaluation.explanation }}</p>
            </div>

            <div v-if="submission.llm_evaluation.error_details && submission.llm_evaluation.error_details.length > 0" class="error-details">
              <h5>详细分析</h5>
              <div v-for="(detail, index) in submission.llm_evaluation.error_details" :key="`error-detail-${index}`" class="error-detail-item">
                <div class="error-detail-type">
                  <strong>{{ detail.type }}</strong>
                </div>
                <div class="error-detail-description">
                  {{ detail.description }}
                </div>
                <div v-if="detail.test_cases && detail.test_cases.length > 0" class="error-test-cases">
                  <span class="label">受影响的测试用例:</span>
                  <el-tag
                    v-for="(testCase, tcIndex) in detail.test_cases"
                    :key="`tc-${index}-${tcIndex}`"
                    size="small"
                    effect="plain"
                  >
                    {{ testCase }}
                  </el-tag>
                </div>
              </div>
            </div>
          </div>

          <!-- 总体评估部分 - 改进的UI -->
          <div v-if="submission.llm_evaluation.summary" class="evaluation-summary">
            <h4>总体评估</h4>
            <el-card shadow="hover" class="summary-card">
              <div class="summary-content">
                <i class="el-icon-document summary-icon"></i>
                <p>{{ submission.llm_evaluation.summary }}</p>
              </div>
            </el-card>
          </div>
          
          <!-- 改进建议部分 - 改进的UI -->
          <div v-if="submission.llm_evaluation.improvement_suggestions && submission.llm_evaluation.improvement_suggestions.length > 0" class="improvement-suggestions">
            <h4>改进建议</h4>
            <el-card shadow="hover" class="suggestions-card">
              <ul class="suggestions-list">
                <li v-for="(suggestion, index) in submission.llm_evaluation.improvement_suggestions" :key="`suggestion-${index}`" class="suggestion-item">
                  <i class="el-icon-light-bulb suggestion-icon"></i>
                  <span>{{ suggestion }}</span>
                </li>
              </ul>
            </el-card>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import CodeEditor from '@/components/editor/CodeEditor.vue'

export default {
  name: 'SubmissionDetail',
  components: {
    CodeEditor
  },
  props: {
    submission: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      activeNames: [],
      loading: true,
      error: null
    }
  },
  computed: {
    evaluationFailed() {
      const evaluation = this.submission.llm_evaluation;
      if (!evaluation) return false;
      
      return (
        (evaluation.summary && evaluation.summary.includes('评估失败')) ||
        evaluation.error ||
        (evaluation.overall_score === '0' && 
         (!evaluation.improvement_suggestions || 
          !evaluation.improvement_suggestions.length))
      );
    }
  },
  methods: {
    getStatusType(status) {
      const types = {
        accepted: 'success',
        wrong_answer: 'danger',
        time_limit_exceeded: 'warning',
        memory_limit_exceeded: 'warning',
        runtime_error: 'danger',
        compilation_error: 'danger',
        pending: 'info',
        judging: 'info',
        system_error: 'danger'
      }
      return types[status.toLowerCase()] || 'info'
    },
    formatStatus(status) {
      const formatted = {
        accepted: 'Accepted',
        wrong_answer: 'Wrong Answer',
        time_limit_exceeded: 'Time Limit Exceeded',
        memory_limit_exceeded: 'Memory Limit Exceeded',
        runtime_error: 'Runtime Error',
        compilation_error: 'Compilation Error',
        pending: 'Pending',
        judging: 'Judging',
        system_error: 'System Error'
      }
      return formatted[status.toLowerCase()] || status
    },
    formatDate(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleString()
    },
    getEditorLanguage(language) {
      const languages = {
        'cpp': 'cpp',
        'c++': 'cpp',
        'python': 'python',
        'python3': 'python',
        'java': 'java',
        'javascript': 'javascript',
        'js': 'javascript'
      }
      return languages[language.toLowerCase()] || 'plaintext'
    },
    getErrorTagType(errorType) {
      // 直接匹配
      if (errorType === 'Wrong Answer' || errorType === '错误答案') {
        return 'danger'
      } else if (errorType === 'Time Limit Exceeded' || errorType === '超时') {
        return 'warning'
      } else if (errorType === 'Memory Limit Exceeded' || errorType === '内存超限') {
        return 'warning'
      } else if (errorType === 'Runtime Error' || errorType === '运行时错误') {
        return 'danger'
      } else if (errorType === 'Compilation Error' || errorType === '编译错误') {
        return 'danger'
      }
      
      // 模糊匹配
      if (errorType.includes('Wrong') || errorType.includes('错误')) {
        return 'danger'
      } else if (errorType.includes('Time') || errorType.includes('效率') || errorType.includes('时间')) {
        return 'warning'
      } else if (errorType.includes('Memory') || errorType.includes('内存')) {
        return 'warning'
      } else {
        return 'info'
      }
    }
  }
}
</script>

<style scoped>
.submission-detail {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
}

.submission-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eaeaea;
}

.submission-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
}

.label {
  font-weight: 500;
  margin-right: 8px;
  color: #606266;
}

.code-section,
.error-section,
.results-section,
.llm-evaluation-section {
  margin-top: 25px;
}

h3 {
  font-size: 1.4rem;
  color: #303133;
  margin-bottom: 15px;
  font-weight: 500;
}

h4 {
  font-size: 1.2rem;
  color: #303133;
  margin: 20px 0 10px;
  font-weight: 500;
}

.code-viewer {
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid #eaeaea;
  height: 400px;
}

.error-message {
  background-color: #fef0f0;
  color: #f56c6c;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
}

.error-message pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.test-case-result {
  padding: 10px 0;
}

.result-info {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 15px;
}

.output-section,
.error-section {
  margin-top: 15px;
}

.output-section h4,
.error-section h4 {
  font-size: 1rem;
  margin-bottom: 8px;
}

.output-section pre,
.error-section pre {
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-x: auto;
  margin: 0;
}

/* LLM评估相关样式 */
.evaluation-container {
  margin-top: 10px;
}

.evaluation-error {
  margin-bottom: 20px;
}

.error-analysis {
  margin-bottom: 25px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 5px;
  border-left: 4px solid #e6a23c;
}

.error-types {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.error-tag {
  margin-right: 6px;
}

.explanation {
  margin-bottom: 15px;
  line-height: 1.5;
}

.error-details {
  margin-top: 15px;
}

.error-detail-item {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.error-detail-type {
  margin-bottom: 6px;
  color: #303133;
}

.error-detail-description {
  margin-bottom: 10px;
  color: #606266;
  line-height: 1.5;
}

.error-test-cases {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}

.no-feedback {
  color: #909399;
  font-style: italic;
  padding: 10px 0;
}

/* 美化后的总体评估和改进建议样式 */
.evaluation-summary,
.improvement-suggestions {
  margin-top: 25px;
}

.summary-card,
.suggestions-card {
  margin-top: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
  transition: all 0.3s ease;
}

.summary-card:hover,
.suggestions-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1) !important;
  transform: translateY(-2px);
}

.summary-content {
  display: flex;
  align-items: flex-start;
}

.summary-icon,
.suggestion-icon {
  color: #409EFF;
  margin-right: 10px;
  margin-top: 3px;
  flex-shrink: 0;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px dashed #eaeaea;
}

.suggestion-item:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}
</style>
