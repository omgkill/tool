<script lang="ts" setup>
import { ref, onMounted } from 'vue'

const props = defineProps<{ enterAction: any }>()

const word = ref('')
const loading = ref(false)

// 当前配置的词典列表（顺序即查询顺序）
const dicts = ref<Array<{ path: string; name: string }>>([])

// 查询结果：按词典返回
const results = ref<
  Array<{
    dictPath: string
    dictName: string
    ok: boolean
    content?: string
    error?: string
  }>
>([])

// 控制每个词典结果是否展开，key 用 dictPath
const expanded = ref<Record<string, boolean>>({})

function loadDicts() {
  try {
    dicts.value = (window as any).services.getDictList() || []
  } catch (e) {
    console.error('getDictList error', e)
  }
}

async function handleSearch() {
  const w = word.value.trim()
  if (!w) return
  loading.value = true
  try {
    const res = await (window as any).services.queryWord(w)
    results.value = res || []
    const exp: Record<string, boolean> = {}
    for (const r of results.value) {
      if (r.ok && r.content) {
        exp[r.dictPath] = true // 默认展开有内容的词典
      }
    }
    expanded.value = exp
  } catch (e) {
    console.error('queryWord error', e)
  } finally {
    loading.value = false
  }
}

function toggleExpand(dictPath: string) {
  expanded.value[dictPath] = !expanded.value[dictPath]
}

function openManage() {
  // 通过重新进入插件并传 code 的方式跳转到管理功能
  try {
    // 如果 utools 提供 runCommand / redirect 能力，可以在这里调用
    // 这里简单提示用户使用“管理词典”指令打开管理页
    window.utools.showNotification('请在 uTools 中输入 “管理词典” 打开词典管理页面')
  } catch (e) {
    console.error('openManage error', e)
  }
}

onMounted(() => {
  loadDicts()
  // 如果 enterAction 里带了选中文本，可以自动填入
  if (props.enterAction && props.enterAction.payload) {
    try {
      word.value = String((props.enterAction as any).payload)
    } catch (e) {
      // ignore
    }
  }
})
</script>

<template>
  <div class="mdict-page">
    <h1>MDict 多词典查词</h1>

    <div class="dict-info">
      <span v-if="dicts.length" class="dict-summary">
        当前词典顺序：{{ dicts.map(d => d.name).join(' / ') }}
      </span>
      <span v-else class="dict-empty">尚未添加任何词典</span>
      <button class="manage-btn" @click="openManage">管理词典</button>
    </div>

    <div class="search-bar">
      <input
        v-model="word"
        class="search-input"
        type="text"
        placeholder="输入要查询的单词，回车或点击查询"
        @keyup.enter="handleSearch"
      />
      <button class="search-btn" :disabled="loading" @click="handleSearch">
        {{ loading ? '查询中...' : '查询' }}
      </button>
    </div>

    <div v-if="results.length" class="result-list">
      <div v-for="item in results" :key="item.dictPath" class="result-item">
        <div class="result-header" @click="toggleExpand(item.dictPath)">
          <span class="collapse-icon">{{ expanded[item.dictPath] ? '▼' : '▶' }}</span>
          <span class="dict-name">{{ item.dictName }}</span>
          <span v-if="!item.ok" class="status-badge error">错误</span>
          <span v-else-if="!item.content" class="status-badge empty">无结果</span>
        </div>
        <div v-if="expanded[item.dictPath]" class="result-body">
          <div v-if="item.ok && item.content" class="result-content" v-html="item.content" />
          <div v-else-if="item.error" class="error-text">查询失败：{{ item.error }}</div>
          <div v-else class="empty-text">未查到结果</div>
        </div>
      </div>
    </div>

    <div v-else class="no-result">
      请输入单词并点击查询，将展示来自多个“词典”的结果，每个结果都可以展开 / 折叠。
    </div>
  </div>
</template>

<style scoped>
.mdict-page {
  padding: 16px;
  font-size: 14px;
}

.mdict-page h1 {
  margin: 0 0 12px;
  font-size: 18px;
}

.search-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.search-input {
  flex: 1;
  padding: 4px 8px;
  font-size: 14px;
  box-sizing: border-box;
}

.search-btn {
  padding: 0 12px;
  line-height: 2;
}

.result-list {
  max-height: 70vh;
  overflow: auto;
}

.result-item {
  border-radius: 6px;
  padding: 6px 8px;
  margin-bottom: 8px;
  background: rgb(230, 230, 230);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
}

.result-header:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.collapse-icon {
  width: 16px;
  display: inline-block;
}

.dict-name {
  font-weight: bold;
}

.result-content {
  margin-top: 4px;
  padding: 12px;
  background: rgb(204, 204, 204);
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.8;
  word-wrap: break-word;
  color: #212121;
}

/* 美化词典返回的 HTML 内容 */
.result-content :deep(a) {
  color: #0d47a1;
  text-decoration: none;
  font-weight: 600;
}

.result-content :deep(a:hover) {
  text-decoration: underline;
}

.result-content :deep(b),
.result-content :deep(strong) {
  font-weight: 700;
  color: #01579b;
}

.result-content :deep(i),
.result-content :deep(em) {
  font-style: italic;
  color: #424242;
}

.result-content :deep(ul),
.result-content :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

.result-content :deep(li) {
  margin: 4px 0;
}

.result-content :deep(p) {
  margin: 8px 0;
}

.result-content :deep(hr) {
  margin: 12px 0;
  border: none;
  border-top: 1px solid #e0e0e0;
}

.result-content :deep(font) {
  /* 覆盖旧式 font 标签的样式 */
}

.result-content :deep(span) {
  /* 保持原有样式，但确保可读 */
}

.no-result {
  margin-top: 8px;
  color: #999;
  font-size: 13px;
}

@media (prefers-color-scheme: dark) {
  .result-item {
    background: rgba(255, 255, 255, 0.06);
  }

  .result-content {
    background: #2e2e2e;
    color: #e0e0e0;
  }

  .result-content :deep(b),
  .result-content :deep(strong) {
    color: #fff;
  }

  .result-content :deep(i),
  .result-content :deep(em) {
    color: #b0b0b0;
  }

  .result-content :deep(a) {
    color: #64b5f6;
  }

  .result-content :deep(hr) {
    border-top-color: #555;
  }
}
</style>
