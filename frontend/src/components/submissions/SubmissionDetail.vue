<template>
  <div class="submission-detail">
    <div class="submission-header">
      <div class="submission-info">
        <div class="info-item">
          <span class="label">Status:</span>
          <el-tag :type="getStatusType(submission.status)">
            {{ formatStatus(submission.status) }}
          </el-tag>
        </div>
        <div class="info-item">
          <span class="label">Language:</span>
          <span>{{ submission.language }}</span>
        </div>
        <div class="info-item">
          <span class="label">Time:</span>
          <span>{{ submission.time_used }} ms</span>
        </div>
        <div class="info-item">
          <span class="label">Memory:</span>
          <span>{{ submission.memory_used }} KB</span>
        </div>
        <div class="info-item">
          <span class="label">Submitted At:</span>
          <span>{{ formatDate(submission.submitted_at) }}</span>
        </div>
      </div>
    </div>

    <div class="code-section">
      <h3>Submitted Code</h3>
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
      <h3>Error Message</h3>
      <div class="error-message">
        <pre>{{ submission.error_message }}</pre>
      </div>
    </div>

    <div v-if="submission.test_case_results && submission.test_case_results.length > 0" class="results-section">
      <h3>Test Case Results</h3>
      <el-collapse>
        <el-collapse-item 
          v-for="(result, index) in submission.test_case_results" 
          :key="result.test_case_id"
          :title="`Test Case #${index + 1}: ${formatStatus(result.status)}`"
          :name="index"
        >
          <div class="test-case-result">
            <div class="result-info">
              <div class="info-item">
                <span class="label">Status:</span>
                <el-tag :type="getStatusType(result.status)">{{ formatStatus(result.status) }}</el-tag>
              </div>
              <div class="info-item">
                <span class="label">Time Used:</span>
                <span>{{ result.time_used }} ms</span>
              </div>
              <div class="info-item">
                <span class="label">Memory Used:</span>
                <span>{{ result.memory_used }} KB</span>
              </div>
            </div>
            
            <div v-if="result.output" class="output-section">
              <h4>Output:</h4>
              <pre>{{ result.output }}</pre>
            </div>
            
            <div v-if="result.error_message" class="error-section">
              <h4>Error:</h4>
              <pre>{{ result.error_message }}</pre>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>

    <!-- 大模型评估结果部分 -->
    <div v-if="submission.llm_evaluation" class="llm-evaluation-section">
      <h3>AI Code Evaluation</h3>

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
          <!-- Error Analysis Section (New) -->
          <div v-if="submission.llm_evaluation.error_types && submission.llm_evaluation.error_types.length > 0" class="error-analysis">
            <h4>Error Analysis</h4>
            <div class="error-types">
              <span class="label">Error Types:</span>
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
              <h5>Detailed Analysis</h5>
              <div v-for="(detail, index) in submission.llm_evaluation.error_details" :key="`error-detail-${index}`" class="error-detail-item">
                <div class="error-detail-type">
                  <strong>{{ detail.type }}</strong>
                </div>
                <div class="error-detail-description">
                  {{ detail.description }}
                </div>
                <div v-if="detail.test_cases && detail.test_cases.length > 0" class="error-test-cases">
                  <span class="label">Affected Test Cases:</span>
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

          <div v-if="submission.llm_evaluation.summary" class="evaluation-summary">
            <h4>Overall Summary</h4>
            <div class="summary-content">
              <p>{{ submission.llm_evaluation.summary }}</p>
              <div v-if="submission.llm_evaluation.overall_score" class="score-badge">
                Score: {{ submission.llm_evaluation.overall_score }}
              </div>
            </div>
          </div>
          
          <el-collapse v-model="activeNames">
            <el-collapse-item title="Code Standard" name="code_standard">
              <div class="evaluation-dimension">
                <div v-if="hasCodeStandardFeedback">
                  <div v-if="submission.llm_evaluation.code_standard.pros && submission.llm_evaluation.code_standard.pros.length > 0" class="pros">
                    <h5>Pros:</h5>
                    <ul>
                      <li v-for="(pro, index) in submission.llm_evaluation.code_standard.pros" :key="`cs-pro-${index}`">{{ pro }}</li>
                    </ul>
                  </div>
                  <div v-if="submission.llm_evaluation.code_standard.cons && submission.llm_evaluation.code_standard.cons.length > 0" class="cons">
                    <h5>Cons:</h5>
                    <ul>
                      <li v-for="(con, index) in submission.llm_evaluation.code_standard.cons" :key="`cs-con-${index}`">{{ con }}</li>
                    </ul>
                  </div>
                </div>
                <div v-else class="no-feedback">
                  <p>没有关于代码规范的具体反馈。</p>
                </div>
              </div>
            </el-collapse-item>
            
            <el-collapse-item title="Code Logic" name="code_logic">
              <div class="evaluation-dimension">
                <div v-if="hasCodeLogicFeedback">
                  <div v-if="submission.llm_evaluation.code_logic.pros && submission.llm_evaluation.code_logic.pros.length > 0" class="pros">
                    <h5>Pros:</h5>
                    <ul>
                      <li v-for="(pro, index) in submission.llm_evaluation.code_logic.pros" :key="`cl-pro-${index}`">{{ pro }}</li>
                    </ul>
                  </div>
                  <div v-if="submission.llm_evaluation.code_logic.cons && submission.llm_evaluation.code_logic.cons.length > 0" class="cons">
                    <h5>Cons:</h5>
                    <ul>
                      <li v-for="(con, index) in submission.llm_evaluation.code_logic.cons" :key="`cl-con-${index}`">{{ con }}</li>
                    </ul>
                  </div>
                </div>
                <div v-else class="no-feedback">
                  <p>没有关于代码逻辑的具体反馈。</p>
                </div>
              </div>
            </el-collapse-item>
            
            <el-collapse-item title="Code Efficiency" name="code_efficiency">
              <div class="evaluation-dimension">
                <div v-if="hasCodeEfficiencyFeedback">
                  <div v-if="submission.llm_evaluation.code_efficiency.pros && submission.llm_evaluation.code_efficiency.pros.length > 0" class="pros">
                    <h5>Pros:</h5>
                    <ul>
                      <li v-for="(pro, index) in submission.llm_evaluation.code_efficiency.pros" :key="`ce-pro-${index}`">{{ pro }}</li>
                    </ul>
                  </div>
                  <div v-if="submission.llm_evaluation.code_efficiency.cons && submission.llm_evaluation.code_efficiency.cons.length > 0" class="cons">
                    <h5>Cons:</h5>
                    <ul>
                      <li v-for="(con, index) in submission.llm_evaluation.code_efficiency.cons" :key="`ce-con-${index}`">{{ con }}</li>
                    </ul>
                  </div>
                </div>
                <div v-else class="no-feedback">
                  <p>没有关于代码效率的具体反馈。</p>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
          
          <div v-if="submission.llm_evaluation.improvement_suggestions && submission.llm_evaluation.improvement_suggestions.length > 0" class="improvement-suggestions">
            <h4>Improvement Suggestions</h4>
            <ul>
              <li v-for="(suggestion, index) in submission.llm_evaluation.improvement_suggestions" :key="`suggestion-${index}`">{{ suggestion }}</li>
            </ul>
          </div>
        </template>
        
        <div v-if="submission.llm_evaluation.error" class="llm-error">
          <p>{{ submission.llm_evaluation.error }}</p>
        </div>
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
      activeNames: ['code_standard'], // 默认展开代码标准部分
      loading: true,
      error: null
    }
  },
  computed: {
    // 检查评估是否失败
    evaluationFailed() {
      const evaluation = this.submission.llm_evaluation;
      if (!evaluation) return false;
      
      return (
        (evaluation.summary && evaluation.summary.includes('评估失败')) ||
        evaluation.error ||
        (evaluation.overall_score === '0' && 
         (!evaluation.code_standard || 
          !evaluation.code_standard.pros || 
          !evaluation.code_standard.pros.length) && 
         (!evaluation.code_standard || 
          !evaluation.code_standard.cons || 
          !evaluation.code_standard.cons.length))
      );
    },
    // 检查是否有代码规范反馈
    hasCodeStandardFeedback() {
      const cs = this.submission.llm_evaluation?.code_standard;
      if (!cs) return false;
      
      return (
        (cs.pros && cs.pros.length > 0) || 
        (cs.cons && cs.cons.length > 0)
      );
    },
    // 检查是否有代码逻辑反馈
    hasCodeLogicFeedback() {
      const cl = this.submission.llm_evaluation?.code_logic;
      if (!cl) return false;
      
      return (
        (cl.pros && cl.pros.length > 0) || 
        (cl.cons && cl.cons.length > 0)
      );
    },
    // 检查是否有代码效率反馈
    hasCodeEfficiencyFeedback() {
      const ce = this.submission.llm_evaluation?.code_efficiency;
      if (!ce) return false;
      
      return (
        (ce.pros && ce.pros.length > 0) || 
        (ce.cons && ce.cons.length > 0)
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
      return types[status] || 'info'
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
      return formatted[status] || status
    },
    formatDate(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleString()
    },
    getEditorLanguage(language) {
      const languages = {
        cpp: 'cpp'
        // Add more language mappings as needed
      }
      return languages[language] || language
    },
    getErrorTagType(errorType) {
      // 根据错误类型返回不同的标签样式
      const typeMap = {
        'WA': 'danger',    // 错误答案
        'TLE': 'warning',  // 超时
        'MLE': 'warning',  // 内存超限
        'RE': 'danger',    // 运行时错误
        'CE': 'danger',    // 编译错误
        'AC': 'success'    // 通过
      }
      
      // 如果完全匹配则返回，否则模糊匹配
      if (typeMap[errorType]) {
        return typeMap[errorType]
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
  background-color: #fff;
  padding: 20px;
}

.submission-header {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eaeaea;
}

.submission-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-weight: bold;
  color: #606266;
}

.code-section,
.error-section,
.results-section {
  margin-bottom: 30px;
}

h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-size: 18px;
}

.code-viewer {
  height: 400px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.error-message,
.output-section pre,
.error-section pre {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: monospace;
  margin: 0;
}

.error-message,
.error-section pre {
  color: #f56c6c;
  background-color: #fef0f0;
}

.test-case-result {
  padding: 15px;
}

.result-info {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
}

h4 {
  margin-top: 15px;
  margin-bottom: 10px;
  color: #303133;
  font-size: 16px;
}

.llm-evaluation-section {
  margin-bottom: 30px;
}

.evaluation-card {
  padding: 20px;
}

.evaluation-summary {
  margin-bottom: 20px;
}

.summary-content {
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.score-badge {
  background-color: #f5f7fa;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
  color: #606266;
}

.evaluation-details {
  margin-bottom: 20px;
}

.evaluation-dimension {
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.pros,
.cons {
  margin-bottom: 15px;
}

.pros ul,
.cons ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.pros li,
.cons li {
  padding: 5px;
  border-bottom: 1px solid #dcdfe6;
}

.pros li:last-child,
.cons li:last-child {
  border-bottom: none;
}

.improvement-suggestions {
  margin-bottom: 20px;
}

.improvement-suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.improvement-suggestions li {
  padding: 5px;
  border-bottom: 1px solid #dcdfe6;
}

.improvement-suggestions li:last-child {
  border-bottom: none;
}

.llm-error {
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

.evaluation-error {
  margin-bottom: 20px;
}
</style>
