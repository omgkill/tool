const fs = require('node:fs')
const path = require('node:path')

// 建议在项目根目录安装 npm 包 "mdict" 作为 MDX 解析库：
//   npm install mdict
// 这里假定该库导出 Mdict 类，构造函数接受 mdx 文件路径，实例有 lookup(word) / lookupSync(word) 方法
let MdictClass = null
let mdictLoadError = null
try {
  console.log('[preload] 尝试 require("mdict")...')
  const mdictLib = require('mdict')
  console.log('[preload] require("mdict") 成功，返回类型:', typeof mdictLib)
  const keys = Object.keys(mdictLib)
  console.log('[preload] mdictLib keys:', keys)
  console.log('[preload] mdictLib keys 具体内容:', JSON.stringify(keys))
  if (keys.length > 0) {
    console.log('[preload] 第一个 key 是:', keys[0], ', 对应的值类型:', typeof mdictLib[keys[0]])
  }
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
  if (MdictClass) {
    console.log('[preload] MdictClass 已成功设置')
  } else {
    console.warn('[preload] require("mdict") 成功但未找到有效的构造函数')
  }
} catch (e) {
  mdictLoadError = e
  console.error('[preload] require("mdict") 失败:', e)
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
  console.log('[loadMdictInstance] 创建词典实例:', filePath)
  const mdictPromise = new MdictClass(filePath)
  console.log('[loadMdictInstance] 构造函数返回类型:', typeof mdictPromise)
  console.log('[loadMdictInstance] 是否有 then 方法:', typeof mdictPromise.then === 'function')
  
  // 如果返回的是 Promise-like 对象（有 then 方法），需要 await
  const mdict = (mdictPromise && typeof mdictPromise.then === 'function') ? await mdictPromise : mdictPromise
  console.log('[loadMdictInstance] 实例化完成，可用方法:', mdict ? Object.keys(mdict) : 'null')
  
  const name = path.basename(filePath)
  const inst = { mdict, name }
  dictInstances.set(filePath, inst)
  return inst
}

async function queryInDict(filePath, word) {
  try {
    const { mdict, name } = await loadMdictInstance(filePath)
    if (!mdict) {
      throw new Error('词典实例加载失败')
    }
    console.log('[queryInDict] 词典实例:', name, ', 可用方法:', Object.keys(mdict))
    
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
      console.log('[queryInDict] 使用方法:', method, '查询:', word)
      const r = await mdict[method](word)
      console.log('[queryInDict] 返回值类型:', typeof r, ', 是数组:', Array.isArray(r))
      console.log('[queryInDict] 返回值前 500 字符:', typeof r === 'string' ? r.substring(0, 500) : r)
      console.log('[queryInDict] 是否包含 HTML 标签:', typeof r === 'string' && /<[^>]+>/.test(r))
      console.log('[queryInDict] 内容长度:', typeof r === 'string' ? r.length : JSON.stringify(r).length)
      
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
    } else {
      console.warn('[queryInDict] 未找到查询方法，可用方法:', Object.keys(mdict))
    }

    console.log('[queryInDict] 最终 result 长度:', result.length)
    return {
      dictPath: filePath,
      dictName: name,
      ok: !!result,
      content: result
    }
  } catch (e) {
    const errMsg = e && e.message ? e.message : String(e)
    console.log('[queryInDict] 捕获异常:', errMsg)
    
    // "** NOT FOUND **" 是正常的"未查到"，不算错误
    if (errMsg.includes('NOT FOUND')) {
      return {
        dictPath: filePath,
        dictName: path.basename(filePath),
        ok: true,
        content: ''
      }
    }
    
    console.error('[queryInDict] 查询出错:', e)
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
