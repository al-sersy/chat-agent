import { marked } from 'marked'
import hljs from 'highlight.js/lib/core'
import js from 'highlight.js/lib/languages/javascript'
import ts from 'highlight.js/lib/languages/typescript'
import py from 'highlight.js/lib/languages/python'
import sh from 'highlight.js/lib/languages/bash'
import json from 'highlight.js/lib/languages/json'
import xml from 'highlight.js/lib/languages/xml'
import css from 'highlight.js/lib/languages/css'

hljs.registerLanguage('javascript', js)
hljs.registerLanguage('js', js)
hljs.registerLanguage('typescript', ts)
hljs.registerLanguage('ts', ts)
hljs.registerLanguage('python', py)
hljs.registerLanguage('bash', sh)
hljs.registerLanguage('sh', sh)
hljs.registerLanguage('json', json)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('css', css)

// configure marked once with hljs code highlighting
marked.use({
  renderer: {
    code(token) {
      const lang = token.lang
      const language = lang && hljs.getLanguage(lang) ? lang : undefined
      const cls = language ? ` language-${language}` : ''
      const code = language ? hljs.highlight(token.text, { language }).value : token.text
      return `<pre><code class="hljs${cls}">${code}</code></pre>`
    },
  },
  gfm: true,
  breaks: true,
})

export { marked }
