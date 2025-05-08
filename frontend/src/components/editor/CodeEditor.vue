<template>
  <div class="simple-editor-container">
    <textarea
      ref="textarea"
      :value="code"
      :readonly="readOnly"
      @input="handleInput"
      @paste="handlePaste"
      @keydown="handleKeyDown"
      class="code-textarea"
      :class="{ 'read-only': readOnly }"
      spellcheck="false"
      autocomplete="off"
      autocorrect="off"
      autocapitalize="off"
    ></textarea>
  </div>
</template>

<script>
export default {
  name: 'CodeEditor',
  props: {
    code: {
      type: String,
      default: ''
    },
    language: {
      type: String,
      default: 'cpp'
    },
    readOnly: {
      type: Boolean,
      default: false
    },
    theme: {
      type: String,
      default: 'light'
    }
  },
  emits: ['update:code', 'change'],
  data() {
    return {
      internalValue: '',
      isComposing: false,
      lastUpdate: Date.now(),
      updateDelay: 300 // ms
    }
  },
  mounted() {
    this.$nextTick(() => {
      if (this.code) {
        this.$refs.textarea.value = this.code
        this.internalValue = this.code
      }
    })
  },
  methods: {
    handleInput(e) {
      const value = e.target.value
      this.internalValue = value
      
      const now = Date.now()
      // 如果距离上次更新的时间太短，使用防抖处理
      if (now - this.lastUpdate < this.updateDelay) {
        clearTimeout(this._inputTimer)
        this._inputTimer = setTimeout(() => {
          this.emitChange(value)
        }, this.updateDelay)
      } else {
        // 否则直接更新
        this.emitChange(value)
      }
      this.lastUpdate = now
    },
    handlePaste(e) {
      // 让浏览器默认处理粘贴
      // 手动触发input事件以确保值更新
      setTimeout(() => {
        const value = this.$refs.textarea.value
        this.internalValue = value
        this.emitChange(value)
      }, 0)
    },
    handleKeyDown(e) {
      // 处理Tab键缩进
      if (e.key === 'Tab') {
        e.preventDefault()
        const start = e.target.selectionStart
        const end = e.target.selectionEnd
        const value = e.target.value
        
        // 在光标位置插入制表符
        e.target.value = value.substring(0, start) + '    ' + value.substring(end)
        
        // 移动光标到适当的位置
        e.target.selectionStart = e.target.selectionEnd = start + 4
        
        // 手动触发输入事件
        this.handleInput({
          target: e.target
        })
      }
    },
    emitChange(value) {
      // 同时触发update:code和change事件以兼容v-model:code和@change
      this.$emit('update:code', value)
      this.$emit('change', value)
    },
    getValue() {
      return this.internalValue || ''
    },
    setValue(value) {
      if (this.$refs.textarea) {
        const scrollPos = this.$refs.textarea.scrollTop
        this.$refs.textarea.value = value
        this.internalValue = value
        this.$refs.textarea.scrollTop = scrollPos
      }
    },
    focus() {
      this.$refs.textarea?.focus()
    }
  },
  watch: {
    code(newValue) {
      // 只有当内部值与传入值不同时才更新，避免光标跳动
      if (newValue !== this.internalValue) {
        this.setValue(newValue)
      }
    }
  }
}
</script>

<style scoped>
.simple-editor-container {
  position: relative;
  width: 100%;
  height: 500px;
  border: 1px solid #ccc;
  overflow: hidden;
}

.code-textarea {
  width: 100%;
  height: 100%;
  padding: 8px;
  box-sizing: border-box;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  background-color: #fff;
  border: none;
  resize: none;
  outline: none;
  white-space: pre;
  overflow: auto;
  tab-size: 4;
}

.code-textarea.read-only {
  background-color: #f5f5f5;
  cursor: default;
}

.dark-theme .code-textarea {
  color: #f8f8f2;
  background-color: #282a36;
}
</style>
