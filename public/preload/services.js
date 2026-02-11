const fs = require('node:fs')
const path = require('node:path')

// 建议在项目根目录安装 npm 包 "mdict" 作为 MDX 解析库：
//   npm install mdict
let MdictClass = null
try {
  const mdictLib = require('mdict')
  // 兼容几种可能的导出形式
  if (typeof mdictLib === 'function') {
    MdictClass = mdictLib
  } else if (typeof mdictLib.dictionary === 'function') {
    MdictClass = mdictLib.dictionary
  } else if (typeof mdictLib.Mdict === 'function') {
    MdictClass = mdictLib.Mdict
  } else if (typeof mdictLib.default === 'function') {
    MdictClass = mdictLib.default
  }
} catch (e) {
  MdictClass = null
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

async function loadMdictInstance(filePath) {
  if (dictInstances.has(filePath)) {
    return dictInstances.get(filePath)
  }
  if (!MdictClass) {
    throw new Error('MDX 解析库未安装或加载失败，请先在项目根目录执行：npm install mdict')
  }
  
  // 检查是否有对应的 MDD 文件
  const mddPath = filePath.replace(/\.mdx$/i, '.mdd')
  const hasMdd = fs.existsSync(mddPath)
  
  // 初始化 MDX
  const mdictPromise = new MdictClass(filePath)
  const mdict = (mdictPromise && typeof mdictPromise.then === 'function') ? await mdictPromise : mdictPromise
  
  // 如果有 MDD，也加载它
  let mdd = null
  if (hasMdd) {
    try {
      const mddPromise = new MdictClass(mddPath)
      mdd = (mddPromise && typeof mddPromise.then === 'function') ? await mddPromise : mddPromise
    } catch (e) {
      // MDD 加载失败不影响 MDX 使用
    }
  }
  
  const name = path.basename(filePath)
  const inst = { mdict, mdd, name, filePath }
  dictInstances.set(filePath, inst)
  return inst
}

async function queryInDict(filePath, word) {
  try {
    const { mdict, name } = await loadMdictInstance(filePath)
    if (!mdict) {
      throw new Error('词典实例加载失败')
    }
    
    let result = ''
    
    // 尝试多种常见的查询方法名
    const lookupMethods = ['lookup', 'search', 'query', 'find', 'definition']
    let method = null
    
    for (const methodName of lookupMethods) {
      if (typeof mdict[methodName] === 'function') {
        method = methodName
        break
      }
    }
    
    if (method) {
      const r = await mdict[method](word)
      
      // 处理各种可能的返回格式
      if (!r) {
        result = ''
      } else if (typeof r === 'string') {
        result = r
      } else if (Array.isArray(r)) {
        if (r.length > 0) {
          // 如果数组元素是对象，尝试提取 definition/content/html 等字段
          if (typeof r[0] === 'object' && r[0] !== null) {
            result = r.map(item => 
              item.definition || item.content || item.html || item.text || JSON.stringify(item)
            ).join('\n\n')
          } else {
            result = r.join('\n\n')
          }
        }
      } else if (typeof r === 'object') {
        // 如果返回对象，尝试提取常见字段
        result = r.definition || r.content || r.html || r.text || JSON.stringify(r)
      } else {
        result = String(r)
      }
    }

    return {
      dictPath: filePath,
      dictName: name,
      ok: !!result,
      content: result
    }
  } catch (e) {
    const errMsg = e && e.message ? e.message : String(e)
    
    // "** NOT FOUND **" 是正常的"未查到"，不算错误
    if (errMsg.includes('NOT FOUND')) {
      return {
        dictPath: filePath,
        dictName: path.basename(filePath),
        ok: true,
        content: ''
      }
    }
    
    return {
      dictPath: filePath,
      dictName: path.basename(filePath),
      ok: false,
      error: errMsg
    }
  }
}

// 通过 window 对象向渲染进程注入 nodejs 能力
window.services = {
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
