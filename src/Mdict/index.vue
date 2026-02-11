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
  // 如果 enterAction 里带了输入内容，自动填入并查询
  if (props.enterAction && props.enterAction.payload) {
    try {
      const inputWord = String((props.enterAction as any).payload).trim()
      if (inputWord) {
        word.value = inputWord
        // 自动查询
        handleSearch()
      }
    } catch (e) {
      // ignore
    }
  }
})
</script>

<template>
  <div class="mdict-page">
    <div v-if="loading" class="loading">
      查询中...
    </div>

    <div v-else-if="results.length" class="result-list">
      <div v-for="item in results" :key="item.dictPath" class="result-item">
        <div class="result-header" @click="toggleExpand(item.dictPath)">
          <span class="collapse-icon">{{ expanded[item.dictPath] ? '▼' : '▶' }}</span>
          <span class="dict-name">{{ item.dictName }}</span>
        </div>
        <div v-if="expanded[item.dictPath]" class="result-body">
          <div v-if="item.ok && item.content" class="result-content" v-html="item.content" />
          <div v-else-if="item.error" class="error-text">{{ item.error }}</div>
          <div v-else class="empty-text">未查到结果</div>
        </div>
      </div>
    </div>

    <div v-else class="no-result">
      未查到结果
    </div>
  </div>
</template>

<style scoped>
.mdict-page {
  padding: 8px;
  font-size: 15px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  height: 100vh;
  box-sizing: border-box;
  overflow: auto;
}

.loading {
  padding: 20px;
  text-align: center;
  color: #86868b;
  font-size: 14px;
}

.result-list {
  height: 100%;
  overflow: auto;
}

.result-item {
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  padding: 6px;
  margin: -6px;
  border-radius: 8px;
  transition: background-color 0.15s ease;
}

.result-header:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.collapse-icon {
  width: 16px;
  display: inline-block;
  font-size: 12px;
  color: #007aff;
}

.dict-name {
  font-weight: 500;
  font-size: 14px;
  color: #1d1d1f;
}

.result-body {
  margin-top: 8px;
}

.result-content {
  padding: 12px;
  background: #f5f5f7;
  border-radius: 8px;
  font-size: 15px;
  line-height: 1.7;
  word-wrap: break-word;
  color: #1d1d1f;
}

/* 美化词典返回的 HTML 内容 - Apple 风格 */
.result-content :deep(a) {
  color: #007aff;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.15s ease;
}

.result-content :deep(a:hover) {
  color: #0051d5;
  text-decoration: underline;
}

.result-content :deep(b),
.result-content :deep(strong) {
  font-weight: 600;
  color: #1d1d1f;
}

.result-content :deep(i),
.result-content :deep(em) {
  font-style: italic;
  color: #6e6e73;
}

.result-content :deep(ul),
.result-content :deep(ol) {
  margin: 12px 0;
  padding-left: 28px;
}

.result-content :deep(li) {
  margin: 6px 0;
}

.result-content :deep(p) {
  margin: 10px 0;
}

.result-content :deep(hr) {
  margin: 16px 0;
  border: none;
  border-top: 1px solid rgba(0, 0, 0, 0.08);
}

.error-text,
.empty-text {
  padding: 8px;
  font-size: 13px;
  border-radius: 6px;
}

.error-text {
  color: #ff3b30;
  background: rgba(255, 59, 48, 0.05);
}

.empty-text {
  color: #86868b;
  background: rgba(142, 142, 147, 0.05);
}

.no-result {
  padding: 20px;
  text-align: center;
  color: #86868b;
  font-size: 13px;
}

@media (prefers-color-scheme: dark) {
  .mdict-page {
    background: #000;
  }

  .mdict-page h1 {
    color: #f5f5f7;
  }

  .dict-info {
    background: rgba(142, 142, 147, 0.16);
  }

  .dict-summary,
  .dict-empty {
    color: #98989d;
  }

  .search-input {
    background: #1c1c1e;
    border-color: rgba(255, 255, 255, 0.1);
    color: #f5f5f7;
  }

  .search-input:focus {
    border-color: #0a84ff;
    box-shadow: 0 0 0 4px rgba(10, 132, 255, 0.2);
  }

  .search-btn {
    background: #0a84ff;
  }

  .search-btn:hover {
    background: #409cff;
  }

  .manage-btn {
    background: #0a84ff;
  }

  .manage-btn:hover {
    background: #409cff;
  }

  .result-item {
    background: #1c1c1e;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  }

  .result-item:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
  }

  .result-header:hover {
    background-color: rgba(255, 255, 255, 0.05);
  }

  .collapse-icon {
    color: #0a84ff;
  }

  .dict-name {
    color: #f5f5f7;
  }

  .result-content {
    background: #2c2c2e;
    color: #f5f5f7;
  }

  .result-content :deep(a) {
    color: #0a84ff;
  }

  .result-content :deep(a:hover) {
    color: #409cff;
  }

  .result-content :deep(b),
  .result-content :deep(strong) {
    color: #fff;
  }

  .result-content :deep(i),
  .result-content :deep(em) {
    color: #98989d;
  }

  .result-content :deep(hr) {
    border-top-color: rgba(255, 255, 255, 0.1);
  }

  .error-text {
    color: #ff453a;
    background: rgba(255, 69, 58, 0.15);
  }

  .empty-text {
    color: #98989d;
    background: rgba(142, 142, 147, 0.15);
  }

  .no-result {
    color: #98989d;
    background: rgba(142, 142, 147, 0.15);
  }

  .status-badge.error {
    background: rgba(255, 69, 58, 0.2);
    color: #ff453a;
  }

  .status-badge.empty {
    background: rgba(142, 142, 147, 0.2);
    color: #98989d;
  }
}
</style>
