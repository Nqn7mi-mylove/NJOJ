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
            <span>Test Cases</span>
            <el-button type="primary" size="small" @click="addTestCase">
              Add Test Case
            </el-button>
          </div>
        </template>
        
        <el-alert
          v-if="formData.test_cases.length === 0"
          title="No test cases added. Add at least one test case."
          type="warning"
          :closable="false"
          show-icon
        ></el-alert>
        
        <div class="test-cases">
          <el-collapse v-model="activeTestCases">
            <el-collapse-item
              v-for="(testCase, index) in formData.test_cases"
              :key="index"
              :title="`Test Case #${index + 1}${testCase.is_sample ? ' (Sample)' : ''}`"
              :name="index"
            >
              <div class="test-case-form">
                <div class="test-case-header">
                  <el-switch
                    v-model="testCase.is_sample"
                    active-text="Sample test case (visible to users)"
                    inactive-text="Hidden test case"
                  ></el-switch>
                  
                  <el-button
                    type="danger"
                    size="small"
                    @click.prevent="removeTestCase(index)"
                    class="delete-test-case"
                  >
                    Delete
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
              v-model:code="formData.special_judge_code" 
              language="cpp"
              theme="vs-dark"
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

export default {
  name: 'ProblemEditView',
  components: {
    MarkdownRenderer,
    CodeEditor
  },
  data() {
    return {
      formData: {
        title: '',
        description: '',
        difficulty: 'medium',
        tags: [],
        time_limit: 1000,
        memory_limit: 256,
        is_public: true,
        test_cases: [],
        has_special_judge: false,
        special_judge_code: `// Special judge template (C++)\n\n#include <iostream>\n#include <fstream>\n#include <string>\n\nusing namespace std;\n\n// The special judge should read these files:\n// - input.txt: The input of the test case\n// - expected_output.txt: The expected output\n// - output.txt: The contestant's output\n\n// Return exit code 0 if the output is correct, non-zero otherwise\n\nint main() {\n    ifstream input_file("input.txt");\n    ifstream expected_output_file("expected_output.txt");\n    ifstream output_file("output.txt");\n    \n    // Add your custom validation logic here\n    // Example: Check if the contestant's output is correct\n    \n    return 0; // 0 means correct, any other value means wrong answer\n}`
      },
      rules: {
        title: [
          { required: true, message: 'Please enter a title', trigger: 'blur' }
        ],
        description: [
          { required: true, message: 'Please provide a description', trigger: 'blur' }
        ],
        difficulty: [
          { required: true, message: 'Please select a difficulty level', trigger: 'change' }
        ]
      },
      availableTags: [
        'array', 'string', 'hash-table', 'dynamic-programming', 
        'math', 'sorting', 'greedy', 'depth-first-search', 
        'binary-search', 'tree', 'graph', 'breadth-first-search'
      ],
      showPreview: false,
      activeTestCases: [],
      loading: false,
      saving: false
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
    async loadProblem() {
      if (!this.isEditMode) return
      
      this.loading = true
      
      try {
        await this.fetchProblem(this.problemId)
        
        if (this.problem) {
          // Copy the problem data to the form
          const {
            title, description, difficulty, tags, time_limit, memory_limit,
            is_public, test_cases, has_special_judge, special_judge_code
          } = this.problem
          
          this.formData = {
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
        is_sample: false
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

.test-cases {
  margin-top: 15px;
}

.test-case-form {
  padding: 10px 0;
}

.test-case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.test-case-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
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
