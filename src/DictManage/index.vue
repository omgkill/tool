<script lang="ts" setup>
import { ref, onMounted } from 'vue'

interface DictItem {
  path: string
  name: string
}

const dicts = ref<DictItem[]>([])

function loadDicts() {
  try {
    dicts.value = (window as any).services.getDictList() || []
  } catch (e) {
    console.error('getDictList error', e)
  }
}

function handleAddDict() {
  try {
    const res = (window as any).services.selectDictFiles()
    if (res) {
      dicts.value = res
    }
  } catch (e) {
    console.error('selectDictFiles error', e)
  }
}

function saveOrder() {
  try {
    const res = (window as any).services.updateDictOrder(dicts.value)
    if (res) dicts.value = res
  } catch (e) {
    console.error('updateDictOrder error', e)
  }
}

function moveUp(index: number) {
  if (index <= 0) return
  const arr = dicts.value.slice()
  const tmp = arr[index - 1]
  arr[index - 1] = arr[index]
  arr[index] = tmp
  dicts.value = arr
  saveOrder()
}

function moveDown(index: number) {
  if (index >= dicts.value.length - 1) return
  const arr = dicts.value.slice()
  const tmp = arr[index + 1]
  arr[index + 1] = arr[index]
  arr[index] = tmp
  dicts.value = arr
  saveOrder()
}

function handleRemove(path: string) {
  try {
    const res = (window as any).services.removeDict(path)
    if (res) dicts.value = res
  } catch (e) {
    console.error('removeDict error', e)
  }
}

onMounted(() => {
  loadDicts()
})
</script>

<template>
  <div class="dict-manage">
    <div class="header">
      <h1>词典管理</h1>
      <p class="subtitle">管理 MDX 词典顺序，查词时将按此顺序依次展示结果</p>
    </div>

    <div class="info-card">
      <div class="info-icon">ℹ️</div>
      <div class="info-text">
        <strong>自动加载资源文件</strong>
        <p>添加 MDX 词典时，会自动加载同目录下同名的 MDD 文件（图片、音频等资源）</p>
      </div>
    </div>

    <div class="toolbar">
      <button class="add-btn" @click="handleAddDict">
        <span class="btn-icon">+</span>
        添加词典
      </button>
    </div>

    <div v-if="dicts.length" class="dict-list">
      <div
        v-for="(item, index) in dicts"
        :key="item.path"
        class="dict-item"
      >
        <div class="dict-number">{{ index + 1 }}</div>
        <div class="dict-main">
          <div class="dict-name">{{ item.name }}</div>
          <div class="dict-path">{{ item.path }}</div>
        </div>
        <div class="dict-actions">
          <button 
            class="action-btn" 
            :disabled="index === 0" 
            @click="moveUp(index)"
            title="上移"
          >
            ↑
          </button>
          <button 
            class="action-btn" 
            :disabled="index === dicts.length - 1" 
            @click="moveDown(index)"
            title="下移"
          >
            ↓
          </button>
          <button 
            class="action-btn danger" 
            @click="handleRemove(item.path)"
            title="删除"
          >
            ×
          </button>
        </div>
      </div>
    </div>

    <div v-else class="empty">
      <div class="empty-icon">📚</div>
      <p>还没有添加任何词典</p>
      <p class="empty-hint">点击上方"添加词典"按钮开始使用</p>
    </div>
  </div>
</template>

<style scoped>
.dict-manage {
  padding: 20px;
  font-size: 15px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  max-width: 900px;
  margin: 0 auto;
}

.header {
  margin-bottom: 20px;
}

.header h1 {
  margin: 0 0 6px;
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #86868b;
  font-weight: 400;
}

.info-card {
  display: flex;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 122, 255, 0.05);
  border-radius: 12px;
  margin-bottom: 20px;
  border-left: 3px solid #007aff;
}

.info-icon {
  font-size: 20px;
  line-height: 1;
}

.info-text {
  flex: 1;
}

.info-text strong {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 4px;
}

.info-text p {
  margin: 0;
  font-size: 13px;
  color: #6e6e73;
  line-height: 1.6;
}

.toolbar {
  margin-bottom: 20px;
}

.add-btn {
  padding: 12px 24px;
  background: #007aff;
  color: #fff;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.add-btn:hover {
  background: #0051d5;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 122, 255, 0.3);
}

.add-btn:active {
  transform: translateY(0);
}

.btn-icon {
  font-size: 18px;
  font-weight: 300;
}

.dict-list {
  /* 不限制高度，让所有词典完全展开 */
}

.dict-item {
  padding: 16px;
  margin-bottom: 12px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s ease;
}

.dict-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.dict-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(0, 122, 255, 0.1);
  color: #007aff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.dict-main {
  flex: 1;
  min-width: 0;
}

.dict-name {
  font-weight: 600;
  font-size: 15px;
  color: #1d1d1f;
  margin-bottom: 4px;
}

.dict-path {
  font-size: 12px;
  color: #86868b;
  word-break: break-all;
  font-family: Monaco, Consolas, monospace;
}

.dict-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: #fff;
  color: #1d1d1f;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
}

.action-btn:hover:not(:disabled) {
  background: #f5f5f7;
  border-color: #007aff;
  color: #007aff;
}

.action-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.action-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.action-btn.danger {
  color: #ff3b30;
  border-color: rgba(255, 59, 48, 0.2);
}

.action-btn.danger:hover:not(:disabled) {
  background: rgba(255, 59, 48, 0.05);
  border-color: #ff3b30;
}

.empty {
  margin-top: 40px;
  text-align: center;
  color: #86868b;
  padding: 40px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty p {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 500;
}

.empty-hint {
  font-size: 13px;
  color: #98989d;
}

@media (prefers-color-scheme: dark) {
  .header h1 {
    color: #f5f5f7;
  }

  .subtitle {
    color: #98989d;
  }

  .info-card {
    background: rgba(10, 132, 255, 0.15);
    border-left-color: #0a84ff;
  }

  .info-text strong {
    color: #f5f5f7;
  }

  .info-text p {
    color: #98989d;
  }

  .add-btn {
    background: #0a84ff;
  }

  .add-btn:hover {
    background: #409cff;
  }

  .dict-item {
    background: #1c1c1e;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
  }

  .dict-item:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  }

  .dict-number {
    background: rgba(10, 132, 255, 0.2);
    color: #0a84ff;
  }

  .dict-name {
    color: #f5f5f7;
  }

  .dict-path {
    color: #98989d;
  }

  .action-btn {
    background: #2c2c2e;
    border-color: rgba(255, 255, 255, 0.1);
    color: #f5f5f7;
  }

  .action-btn:hover:not(:disabled) {
    background: #3a3a3c;
    border-color: #0a84ff;
    color: #0a84ff;
  }

  .action-btn.danger {
    color: #ff453a;
    border-color: rgba(255, 69, 58, 0.3);
  }

  .action-btn.danger:hover:not(:disabled) {
    background: rgba(255, 69, 58, 0.15);
    border-color: #ff453a;
  }

  .empty {
    color: #98989d;
  }
}
</style>
