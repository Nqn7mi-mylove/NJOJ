<template>
  <div class="problem-edit">
    <div class="page-header">
      <h1>{{ isEditMode ? 'Edit Problem' : 'Create Problem' }}</h1>
    </div>
    
    <el-form
      ref="problemForm"
      :model="formData"
      :rules="rules"
      label-position="top"
      v-loading="loading"
    >
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>Basic Information</span>
          </div>
        </template>
        
        <el-form-item label="Custom ID" prop="custom_id">
          <el-input v-model="formData.custom_id" placeholder="自定义问题ID，如P1001"></el-input>
          <div class="form-tip">自定义ID将用于显示和URL引用，如不填写将使用系统ID</div>
        </el-form-item>
        
        <el-form-item label="Title" prop="title">
          <el-input v-model="formData.title" placeholder="Problem title"></el-input>
        </el-form-item>
        
        <el-form-item label="Difficulty" prop="difficulty">
          <el-select v-model="formData.difficulty" placeholder="Select difficulty">
            <el-option label="Easy" value="easy"></el-option>
            <el-option label="Medium" value="medium"></el-option>
            <el-option label="Hard" value="hard"></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="Tags" prop="tags">
          <el-select
            v-model="formData.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="Add tags"
          >
            <el-option
              v-for="tag in availableTags"
              :key="tag"
              :label="tag"
              :value="tag"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="Time Limit (ms)" prop="time_limit">
          <el-input-number
            v-model="formData.time_limit"
            :min="100"
            :max="10000"
            :step="100"
          ></el-input-number>
        </el-form-item>
        
        <el-form-item label="Memory Limit (MB)" prop="memory_limit">
          <el-input-number
            v-model="formData.memory_limit"
            :min="16"
            :max="1024"
            :step="16"
          ></el-input-number>
        </el-form-item>
        
        <el-form-item>
          <el-switch
            v-model="formData.is_public"
            active-text="Make problem public"
            inactive-text="Keep problem private"
          ></el-switch>
        </el-form-item>
      </el-card>
      
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>Problem Description (Markdown)</span>
            <div class="preview-toggle">
              <el-switch
                v-model="showPreview"
                active-text="Preview"
                inactive-text="Edit"
              ></el-switch>
            </div>
          </div>
        </template>
        
        <el-form-item prop="description">
          <div v-if="showPreview" class="markdown-preview">
            <MarkdownRenderer :content="formData.description" />
          </div>
          <el-input
            v-else
            v-model="formData.description"
            type="textarea"
            rows="15"
            placeholder="Write problem description in Markdown format"
          ></el-input>
        </el-form-item>
      </el-card>
      
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>测试用例</span>
            <div class="test-case-actions">
              <el-button type="primary" size="small" @click="addTestCase">
                <i class="el-icon-plus"></i> 添加测试用例
              </el-button>
              <el-button v-if="formData.test_cases.length > 0" type="danger" size="small" @click="batchRemoveTestCases" :disabled="selectedTestCases.length === 0">
                <i class="el-icon-delete"></i> 批量删除 ({{ selectedTestCases.length }})
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="file-upload-area">
          <el-upload
            action="#"
            :multiple="true"
            :auto-upload="false"
            :on-change="handleFileChange"
            :file-list="uploadFiles"
            accept=".in,.out"
            drag
            class="test-case-uploader"
          >
            <i class="el-icon-upload"></i>
            <div class="el-upload__text">拖拽测试用例文件到此处或 <em>点击选择</em></div>
            <div class="el-upload__tip">请选择成对的 .in 和 .out 文件，文件名应相同（仅后缀不同）</div>
          </el-upload>
          
          <div class="upload-actions" v-if="hasFilesToUpload">
            <el-button type="success" @click="uploadTestCases">
              <i class="el-icon-upload2"></i> 导入选择的文件
            </el-button>
          </div>
        </div>
        
        <el-alert
          v-if="formData.test_cases.length === 0"
          title="No test cases added. Add at least one test case."
          type="warning"
          :closable="false"
          show-icon
          style="margin-top: 15px;"
        ></el-alert>
        
        <div class="test-cases">
          <el-collapse v-model="activeTestCases">
            <el-collapse-item
              v-for="(testCase, index) in formData.test_cases"
              :key="index"
              :title="`测试用例 #${index + 1}${testCase.is_sample ? ' (示例)' : ''}`"
              :name="index"
            >
              <div class="test-case-form">
                <div class="test-case-header">
                  <div class="test-case-left-controls">
                    <el-checkbox 
                      v-model="testCase.selected" 
                      @change="updateSelectedTestCases"
                      class="test-case-checkbox"
                    ></el-checkbox>
                    <el-switch
                      v-model="testCase.is_sample"
                      active-text="示例测试用例(对用户可见)"
                      inactive-text="隐藏测试用例"
                    ></el-switch>
                  </div>
                  
                  <el-button
                    type="danger"
                    size="small"
                    @click.prevent="removeTestCase(index)"
                    class="delete-test-case"
                  >
                    删除
                  </el-button>
                </div>
                
                <div class="test-case-content">
                  <div class="test-case-input">
                    <div class="input-header">
                      <span>Input:</span>
                    </div>
                    <el-input
                      v-model="testCase.input"
                      type="textarea"
                      rows="5"
                      placeholder="Test case input"
                    ></el-input>
                  </div>
                  
                  <div class="test-case-output">
                    <div class="output-header">
                      <span>Expected Output:</span>
                    </div>
                    <el-input
                      v-model="testCase.output"
                      type="textarea"
                      rows="5"
                      placeholder="Expected output"
                    ></el-input>
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>
      
      <el-card class="form-card">
        <template #header>
          <div class="card-header">
            <span>Special Judge</span>
            <el-switch
              v-model="formData.has_special_judge"
              active-text="Use Special Judge"
              inactive-text="Standard Judge"
            ></el-switch>
          </div>
        </template>
        
        <div v-if="formData.has_special_judge" class="special-judge">
          <p class="special-judge-info">
            Special judge is used when the problem has multiple correct answers.
            Write C++ code to check if the contestant's output is correct.
          </p>
          
          <div class="code-editor-container">
            <CodeEditor 
              :code="formData.special_judge_code"
              language="cpp"
              @change="onSpecialJudgeCodeChange"
            />
          </div>
        </div>
      </el-card>
      
      <div class="form-actions">
        <el-button type="primary" @click="saveProblem" :loading="saving">
          {{ isEditMode ? 'Update Problem' : 'Create Problem' }}
        </el-button>
        <el-button @click="cancel">Cancel</el-button>
      </div>
    </el-form>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
import MarkdownRenderer from '@/components/markdown/MarkdownRenderer.vue'
import CodeEditor from '@/components/editor/CodeEditor.vue'
import api from '@/services/api'

export default {
  name: 'ProblemEditView',
  components: {
    MarkdownRenderer,
    CodeEditor
  },
  data() {
    return {
      loading: false,
      saving: false,
      uploadFiles: [], // 上传的测试用例文件
      uploadLoading: false, // 上传测试用例加载状态
      selectedTestCases: [], // 选中的测试用例索引
      formData: {
        custom_id: '',
        title: '',
        description: '',
        difficulty: 'medium',
        tags: [],
        time_limit: 1000,
        memory_limit: 256,
        is_public: true,
        test_cases: [],
        has_special_judge: false,
        special_judge_code: `// 这是一个特殊评测函数样例 (C++)
// 参数: 
// - input: 测试输入
// - userOutput: 用户程序输出
// - expectedOutput: 期望输出
// 返回: 用户代码是否通过测试
bool check(std::string input, std::string userOutput, std::string expectedOutput) {
  // 在这里实现特殊评测逻辑
  return userOutput == expectedOutput;
}`
      },
      availableTags: [
        'Array', 'String', 'Hash Table', 'Dynamic Programming',
        'Math', 'Greedy', 'Sorting', 'Depth-First Search',
        'Binary Search', 'Tree', 'Breadth-First Search', 'Graph'
      ],
      showPreview: false,
      activeTestCases: [],
      rules: {
        title: [
          { required: true, message: 'Please enter a title', trigger: 'blur' }
        ],
        description: [
          { required: true, message: 'Please enter a description', trigger: 'blur' }
        ],
        difficulty: [
          { required: true, message: 'Please select a difficulty level', trigger: 'change' }
        ]
      }
    }
  },
  computed: {
    ...mapGetters({
      problem: 'problems/currentProblem',
      isAdmin: 'auth/isAdmin',
      currentUser: 'auth/currentUser'
    }),
    isEditMode() {
      return this.$route.params.id !== undefined
    },
    problemId() {
      return this.$route.params.id
    },
    hasFilesToUpload() {
      return this.uploadFiles.length > 0
    }
  },
  methods: {
    ...mapActions({
      fetchProblem: 'problems/fetchProblem',
      createProblem: 'problems/createProblem',
      updateProblem: 'problems/updateProblem',
      setError: 'setError',
      clearError: 'clearError'
    }),
    // 文件选择变化处理
    handleFileChange(file, fileList) {
      this.uploadFiles = fileList;
    },
    // 上传测试用例文件
    async uploadTestCases() {
      if (!this.uploadFiles.length) {
        this.$message.warning('请先选择测试用例文件')
        return
      }

      this.uploadLoading = true
      try {
        const formData = new FormData()
        this.uploadFiles.forEach(file => {
          formData.append('files', file.raw)
        })

        const response = await api.post('/test-cases/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        // 添加上传的测试用例到当前表单
        if (response.data && response.data.length) {
          response.data.forEach(testCase => {
            this.formData.test_cases.push(testCase)
          })
          this.$message.success(`成功导入 ${response.data.length} 个测试用例`)
          
          // 清空上传列表
          this.uploadFiles = []
        } else {
          this.$message.warning('没有找到有效的测试用例')
        }
      } catch (error) {
        console.error('上传测试用例失败', error)
        this.$message.error('上传测试用例失败: ' + (error.response?.data?.detail || error.message))
      } finally {
        this.uploadLoading = false
      }
    },
    async loadProblem() {
      if (!this.isEditMode) return
      
      this.loading = true
      
      try {
        await this.fetchProblem(this.problemId)
        
        if (this.problem) {
          // Copy the problem data to the form
          const {
            title, description, difficulty, tags, time_limit, memory_limit,
            is_public, test_cases, has_special_judge, special_judge_code, custom_id
          } = this.problem
          
          this.formData = {
            custom_id: custom_id || '',  // 添加custom_id字段
            title,
            description,
            difficulty,
            tags: tags || [],
            time_limit,
            memory_limit,
            is_public,
            test_cases: test_cases || [],
            has_special_judge: has_special_judge || false,
            special_judge_code: special_judge_code || this.formData.special_judge_code
          }
          
          // Add sample test cases if any
          if (this.problem.sample_test_cases && this.problem.sample_test_cases.length > 0) {
            // Merge sample test cases with regular test cases, marking them as sample
            this.problem.sample_test_cases.forEach(testCase => {
              if (!this.formData.test_cases.find(tc => 
                tc.input === testCase.input && tc.output === testCase.output
              )) {
                this.formData.test_cases.push({
                  ...testCase,
                  is_sample: true
                })
              }
            })
          }
        }
      } catch (error) {
        console.error('Error loading problem', error)
        this.setError('Failed to load problem details')
      } finally {
        this.loading = false
      }
    },
    addTestCase() {
      const newTestCase = {
        input: '',
        output: '',
        is_sample: false,
        selected: false
      }
      
      this.formData.test_cases.push(newTestCase)
      this.activeTestCases.push(this.formData.test_cases.length - 1)
    },
    removeTestCase(index) {
      this.formData.test_cases.splice(index, 1)
      
      // Update active test cases
      this.activeTestCases = this.activeTestCases
        .filter(i => i !== index)
        .map(i => i > index ? i - 1 : i)
        
      // Update selected test cases
      this.updateSelectedTestCases()
    },
    updateSelectedTestCases() {
      // 更新选中的测试用例索引列表
      this.selectedTestCases = this.formData.test_cases
        .map((testCase, index) => testCase.selected ? index : -1)
        .filter(index => index !== -1)
    },
    batchRemoveTestCases() {
      if (this.selectedTestCases.length === 0) return
      
      // 确认删除
      this.$confirm(`确定要删除选中的 ${this.selectedTestCases.length} 个测试用例吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        // 从大到小排序，避免删除时索引变化
        const indexesToRemove = [...this.selectedTestCases].sort((a, b) => b - a)
        
        // 删除选中的测试用例
        indexesToRemove.forEach(index => {
          this.formData.test_cases.splice(index, 1)
        })
        
        // 更新激活的测试用例
        this.activeTestCases = []
        
        // 清空选中列表
        this.selectedTestCases = []
        
        this.$message.success('已删除选中的测试用例')
      }).catch(() => {
        // 取消删除
      })
    },
    onSpecialJudgeCodeChange(value) {
      this.formData.special_judge_code = value
    },
    async saveProblem() {
      try {
        await this.$refs.problemForm.validate()
        
        // Check if there's at least one test case
        if (this.formData.test_cases.length === 0) {
          this.$message.error('Please add at least one test case')
          return
        }
        
        this.saving = true
        
        // Prepare the problem data
        const problemData = { ...this.formData }
        
        // Split test cases into regular and sample
        problemData.sample_test_cases = problemData.test_cases
          .filter(tc => tc.is_sample)
          .map(tc => ({ input: tc.input, output: tc.output, is_sample: true }))
        
        // If not using special judge, set the code to null
        if (!problemData.has_special_judge) {
          problemData.special_judge_code = null
        }
        
        let success
        
        if (this.isEditMode) {
          // Update existing problem
          success = await this.updateProblem({
            id: this.problemId,
            problemData
          })
        } else {
          // Create new problem
          success = await this.createProblem(problemData)
        }
        
        if (success) {
          this.$message.success(
            this.isEditMode
              ? 'Problem updated successfully'
              : 'Problem created successfully'
          )
          this.$router.push('/admin/problems')
        } else {
          this.$message.error(
            this.isEditMode
              ? 'Failed to update problem'
              : 'Failed to create problem'
          )
        }
      } catch (error) {
        console.error('Form validation failed', error)
      } finally {
        this.saving = false
      }
    },
    cancel() {
      this.$router.push('/admin/problems')
    }
  },
  mounted() {
    if (!this.isAdmin) {
      this.$router.push('/')
      return
    }
    
    this.loadProblem()
    
    // Add an initial test case if creating a new problem
    if (!this.isEditMode && this.formData.test_cases.length === 0) {
      this.addTestCase()
    }
  }
}
</script>

<style scoped>
.problem-edit {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

h1 {
  margin: 0;
  color: #303133;
}

.form-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-toggle {
  display: flex;
  align-items: center;
}

.markdown-preview {
  min-height: 200px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #f8f9fa;
  overflow-y: auto;
}

.test-case-actions {
  display: flex;
  flex-wrap: nowrap;
  gap: 10px;
  align-items: center;
}

.test-case-actions .el-button {
  margin: 0;
}

.file-upload-area {
  background-color: #f8f9fa;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.test-case-uploader {
  width: 100%;
}

.test-case-uploader :deep(.el-upload-dragger) {
  width: 100%;
  height: auto;
  padding: 20px;
}

.upload-actions {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}


.el-collapse-item__content {
  padding-bottom: 20px;
}

.test-case-form {
  width: 100%;
}

.test-case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.test-case-left-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.test-case-checkbox {
  margin-right: 0;
}

.test-case-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-case-input,
.test-case-output {
  width: 100%;
}

.input-header,
.output-header {
  margin-bottom: 5px;
  font-weight: bold;
}

.special-judge-info {
  margin-bottom: 15px;
  color: #606266;
}

.code-editor-container {
  height: 400px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.form-actions {
  display: flex;
  justify-content: flex-start;
  gap: 10px;
  margin-top: 30px;
}

@media (max-width: 768px) {
  .test-case-content {
    grid-template-columns: 1fr;
  }
}
</style>
