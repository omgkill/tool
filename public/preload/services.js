const fs = require('node:fs')
const path = require('node:path')

// 请先在项目根目录安装 MDX 解析库（例如 mdict-js）：
//   npm install mdict-js
// 这里假定库导出 MDict 类，构造函数接受 mdx 文件路径，实例有 async lookup(word) 方法返回 HTML 字符串
let MDict
try {
  // 动态 require，避免未安装时直接崩溃
  // 你可以根据实际使用的库 API 调整这里
  MDict = require('mdict-js').MDict || require('mdict-js')
} catch (e) {
  MDict = null
}

// 词典配置在 utools.db 中的 key
const DICT_CONFIG_KEY = 'mdict-config'

// 内存中缓存已加载的词典实例，避免重复读取大文件
// key: filePath, value: { mdict, name }
const dictInstances = new Map()

function loadConfig() {
  const doc = window.utools.db.get(DICT_CONFIG_KEY)
  if (!doc) return { _id: DICT_CONFIG_KEY, dicts: [] }
  return doc
}

function saveConfig(config) {
  window.utools.db.put(config)
}

function loadMdictInstance(filePath) {
  if (dictInstances.has(filePath)) {
    return dictInstances.get(filePath)
  }
  if (!MDict) {
    throw new Error('MDX 解析库未安装，请先在项目根目录执行：npm install mdict-js')
  }
  const mdict = new MDict(filePath)
  const name = path.basename(filePath)
  const inst = { mdict, name }
  dictInstances.set(filePath, inst)
  return inst
}

async function queryInDict(filePath, word) {
  try {
    const { mdict, name } = loadMdictInstance(filePath)
    let result = ''
    // 这里根据你实际使用的库 API 调整 lookup 调用方式
    if (typeof mdict.lookup === 'function') {
      const r = await mdict.lookup(word)
      if (Array.isArray(r)) {
        result = r.join('\n')
      } else if (r != null) {
        result = String(r)
      }
    } else if (typeof mdict.lookupSync === 'function') {
      const r = mdict.lookupSync(word)
      result = r ? String(r) : ''
    }

    return {
      dictPath: filePath,
      dictName: name,
      ok: !!result,
      content: result
    }
  } catch (e) {
    return {
      dictPath: filePath,
      dictName: path.basename(filePath),
      ok: false,
      error: e && e.message ? e.message : String(e)
    }
  }
}

// 通过 window 对象向渲染进程注入 nodejs 能力
window.services = {
  // 读文件
  readFile(file) {
    return fs.readFileSync(file, { encoding: 'utf-8' })
  },

  // 文本写入到下载目录
  writeTextFile(text) {
    const filePath = path.join(window.utools.getPath('downloads'), Date.now().toString() + '.txt')
    fs.writeFileSync(filePath, text, { encoding: 'utf-8' })
    return filePath
  },

  // 图片写入到下载目录
  writeImageFile(base64Url) {
    const matchs = /^data:image\/([a-z]{1,20});base64,/i.exec(base64Url)
    if (!matchs) return
    const filePath = path.join(window.utools.getPath('downloads'), Date.now().toString() + '.' + matchs[1])
    fs.writeFileSync(filePath, base64Url.substring(matchs[0].length), { encoding: 'base64' })
    return filePath
  },

  // 选择 MDX 词典文件（多选），并保存到配置中
  selectDictFiles() {
    const files = window.utools.showOpenDialog({
      title: '选择 MDX 词典文件',
      properties: ['openFile', 'multiSelections'],
      filters: [{ name: 'MDX Dictionaries', extensions: ['mdx'] }]
    })
    if (!files || !files.length) return null

    const config = loadConfig()
    const already = new Set(config.dicts.map(d => d.path))
    for (const f of files) {
      if (!already.has(f)) {
        config.dicts.push({
          path: f,
          name: path.basename(f)
        })
      }
    }
    saveConfig(config)
    return config.dicts
  },

  // 获取当前配置的词典列表（过滤掉已删除的文件）
  getDictList() {
    const config = loadConfig()
    const alive = config.dicts.filter(d => fs.existsSync(d.path))
    if (alive.length !== config.dicts.length) {
      config.dicts = alive
      saveConfig(config)
    }
    return alive
  },

  // 更新词典顺序（前端把新的数组整体传回来）
  updateDictOrder(dicts) {
    const config = loadConfig()
    config.dicts = dicts || []
    saveConfig(config)
    return config.dicts
  },

  // 删除某个词典
  removeDict(filePath) {
    const config = loadConfig()
    config.dicts = config.dicts.filter(d => d.path !== filePath)
    saveConfig(config)
    dictInstances.delete(filePath)
    return config.dicts
  },

  // 查词：按当前顺序，依次在每个词典中查
  async queryWord(word) {
    const w = (word || '').trim()
    if (!w) return []
    const config = loadConfig()
    const dicts = config.dicts || []
    const results = []
    for (const d of dicts) {
      if (!fs.existsSync(d.path)) continue
      const r = await queryInDict(d.path, w)
      results.push(r)
    }
    return results
  }
}
