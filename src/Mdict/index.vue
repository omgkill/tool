<script lang="ts" setup>
import { ref, onMounted } from 'vue'

const props = defineProps<{ enterAction: any }>()

const word = ref('')
const loading = ref(false)

// 假数据结果列表
const results = ref<
  Array<{
    id: number
    dictName: string
    content: string
  }>
>([])

// 控制每个词典结果是否展开
const expanded = ref<Record<number, boolean>>({})

function mockQuery(wordValue: string) {
  const w = wordValue || 'example'
  // 模拟从多个词典查出的不同结果
  return [
    {
      id: 1,
      dictName: '英汉词典 A',
      content: `${w} (A): 这里是来自英汉词典 A 的解释，支持多行，\n可以展示较长的释义内容。`
    },
    {
      id: 2,
      dictName: '英英词典 B',
      content: `${w} (B): This is a mock definition from English-English dictionary B.\nYou can put more detailed examples here.`
    },
    {
      id: 3,
      dictName: '专业术语词典 C',
      content: `${w} (C): 专业领域术语解释，示例句子等。`
    }
  ]
}

function handleSearch() {
  const w = word.value.trim()
  if (!w) return
  loading.value = true
  // 模拟异步查询
  setTimeout(() => {
    const res = mockQuery(w)
    results.value = res
    const exp: Record<number, boolean> = {}
    res.forEach(r => {
      exp[r.id] = true // 默认全部展开
    })
    expanded.value = exp
    loading.value = false
  }, 300)
}

function toggleExpand(id: number) {
  expanded.value[id] = !expanded.value[id]
}

onMounted(() => {
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
    <h1>MDict 多词典查词（假数据演示版）</h1>

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
      <div v-for="item in results" :key="item.id" class="result-item">
        <div class="result-header" @click="toggleExpand(item.id)">
          <span class="collapse-icon">{{ expanded[item.id] ? '▼' : '▶' }}</span>
          <span class="dict-name">{{ item.dictName }}</span>
        </div>
        <pre v-if="expanded[item.id]" class="result-content">{{ item.content }}</pre>
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
  background: rgba(0, 0, 0, 0.03);
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
  padding: 6px;
  background: #fff;
  border-radius: 4px;
  font-size: 13px;
  white-space: pre-wrap;
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
    background: #424242;
    color: #f5f5f5;
  }
}
</style>
