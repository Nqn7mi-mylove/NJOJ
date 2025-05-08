<template>
  <div class="markdown-content" ref="markdownContent"></div>
</template>

<script>
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import katex from 'katex'
import texmath from 'markdown-it-texmath'
import 'katex/dist/katex.min.css'

export default {
  name: 'MarkdownRenderer',
  props: {
    content: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      md: null
    };
  },
  mounted() {
    this.initRenderer();
    this.renderContent();
  },
  watch: {
    content: {
      handler() {
        this.renderContent();
      },
      immediate: true
    }
  },
  methods: {
    initRenderer() {
      // 初始化一个新的markdown-it实例
      this.md = new MarkdownIt({
        html: true,
        linkify: true,
        typographer: false, // 禁用排版功能防止干扰LaTeX
        highlight: function (str, lang) {
          if (lang && hljs.getLanguage(lang)) {
            try {
              return hljs.highlight(str, { language: lang }).value;
            } catch (__) {}
          }
          return '';
        }
      });

      // 禁用可能干扰数学公式解析的规则
      this.md.disable(['emphasis']);
      
      // 使用markdown-it-texmath插件和KaTeX渲染数学公式
      this.md.use(texmath, {
        engine: katex,
        delimiters: 'dollars',  // 使用$字符作为数学公式分隔符
        katexOptions: {
          throwOnError: false,
          errorColor: '#cc0000',
          output: 'html',
          trust: true,  // 允许所有KaTeX功能
          macros: {  // 自定义宏
            '\RR': '\mathbb{R}'
          }
        }
      });
    },
    renderContent() {
      if (!this.md || !this.$refs.markdownContent) return;
      
      // 先将markdown渲染为HTML
      const html = this.md.render(this.content || '');
      
      // 设置渲染结果
      this.$refs.markdownContent.innerHTML = html;
    }
  }
}
</script>

<style>
/* KaTeX下标修复 */
.katex .msupsub .msubsub { text-align: left !important; }
.katex .msupsub .msub { font-size: 0.7em !important; vertical-align: -0.5em !important; }
.katex .msupsub .msup { font-size: 0.7em !important; }
.katex .mord.mtight { vertical-align: -0.25em !important; }
.katex .msupsub { position: relative !important; }
.katex .vlist-t2 > .vlist-r:nth-child(2) > .vlist { height: 0 !important; }
.katex .mord .msupsub .vlist-t2 { margin-right: 0 !important; }
.katex-display { overflow-x: auto; overflow-y: hidden; }

.markdown-content {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif;
  color: #2c3e50;
  line-height: 1.6;
}

.markdown-content h1,
.markdown-content h2,
.markdown-content h3,
.markdown-content h4,
.markdown-content h5,
.markdown-content h6 {
  font-weight: 600;
  line-height: 1.25;
  margin-top: 24px;
  margin-bottom: 16px;
}

.markdown-content h1 {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-content h2 {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-content p {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-content code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
}

.markdown-content pre {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-content pre code {
  background-color: transparent;
  padding: 0;
}

.markdown-content ul,
.markdown-content ol {
  padding-left: 2em;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-content table {
  display: block;
  width: 100%;
  overflow: auto;
  border-spacing: 0;
  border-collapse: collapse;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-content table th,
.markdown-content table td {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-content table tr {
  background-color: #fff;
  border-top: 1px solid #c6cbd1;
}

.markdown-content table tr:nth-child(2n) {
  background-color: #f6f8fa;
}

.markdown-content blockquote {
  margin: 0 0 16px;
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
}

.markdown-content hr {
  height: 0.25em;
  padding: 0;
  margin: 24px 0;
  background-color: #e1e4e8;
  border: 0;
}
</style>
