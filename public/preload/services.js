const fs = require('node:fs')
const path = require('node:path')
// 直接引用 mdict 内部解析器，绕过 index.js 的封装以支持 MDD 和更灵活的加载
// 注意：mdict 库本身对 .mdd 的支持需要传入具有 name 属性的文件对象，这里通过 Buffer hack 实现
const mdictParser = require('mdict/mdict-parser.js')

// 词典配置在 utools.db 中的 key
const DICT_CONFIG_KEY = 'mdict-config'

// 内存中缓存已加载的词典实例
// key: filePath, value: { mdxLookup, mddLookup, name, filePath }
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

  // 准备文件对象列表
  // mdict-parser 依赖 file.name 来判断扩展名，而 fs.open 支持 Buffer 作为路径
  // 所以我们创建一个 Buffer 并附加 name 属性，以此欺骗 parser 正确识别文件类型
  const files = []

  // MDX 文件
  const mdxBuf = Buffer.from(filePath)
  mdxBuf.name = filePath
  files.push(mdxBuf)

  // 检查 MDD 文件
  const mddPath = filePath.replace(/\.mdx$/i, '.mdd')
  const hasMdd = fs.existsSync(mddPath)
  if (hasMdd) {
    const mddBuf = Buffer.from(mddPath)
    mddBuf.name = mddPath
    files.push(mddBuf)
  }

  try {
    // 调用 mdict-parser 加载
    // load 返回一个 Promise，解析为 resources 数组
    // resources 数组上挂载了 mdx 和 mdd 的 Promise 属性
    const resources = await mdictParser.load(files)

    // 获取查询函数
    const mdxLookup = await resources.mdx
    let mddLookup = null
    
    // 注意：mdict parser 内部是通过文件扩展名来决定 key 的
    // 由于我们传入的 Buffer 有 name 属性，它会解析出 'mdd' 属性
    // 但在某些实现中可能是 resources['mdd']
    if (resources.mdd) {
      try {
        mddLookup = await resources.mdd
      } catch (e) {
        console.error('MDD load failed', e)
      }
    } else if (resources['.mdd']) { // 有可能是带点的
       try {
        mddLookup = await resources['.mdd']
      } catch (e) {
        console.error('MDD load failed', e)
      }
    }

    const name = path.basename(filePath)
    const inst = { mdxLookup, mddLookup, name, filePath }
    dictInstances.set(filePath, inst)
    return inst

  } catch (e) {
    console.error('Load mdict failed', e)
    throw new Error(`词典加载失败: ${e.message}`)
  }
}

function getMimeType(filename) {
  const ext = path.extname(filename).toLowerCase()
  switch (ext) {
    case '.jpg': case '.jpeg': return 'image/jpeg'
    case '.png': return 'image/png'
    case '.gif': return 'image/gif'
    case '.bmp': return 'image/bmp'
    case '.svg': return 'image/svg+xml'
    case '.mp3': return 'audio/mpeg'
    case '.wav': return 'audio/wav'
    case '.ogg': return 'audio/ogg'
    case '.css': return 'text/css'
    case '.js': return 'text/javascript'
    default: return 'application/octet-stream'
  }
}

async function replaceResources(html, mddLookup) {
  if (!html || !mddLookup) return html
  
  const regex = /(src|href)=["']([^"']+)["']/g
  const matches = []
  let match
  
  // 收集所有资源引用
  while ((match = regex.exec(html)) !== null) {
    matches.push({ full: match[0], attr: match[1], val: match[2] })
  }
  
  if (matches.length === 0) return html
  
  const replacements = new Map()
  const uniqueVals = [...new Set(matches.map(m => m.val))]
  
  // 并行加载资源
  await Promise.all(uniqueVals.map(async (val) => {
    // 跳过非本地资源
    if (val.startsWith('entry://') || val.startsWith('http') || val.startsWith('https') || val.startsWith('data:')) {
      return
    }
    
    try {
      // mdict 的 mdd lookup 会自动处理路径分隔符和反斜杠前缀
      // 直接传入原始路径即可
      const buffer = await mddLookup(val)
      console.log(`[MDD Resource] Loaded: ${val}`, {
        type: typeof buffer,
        isBuffer: Buffer.isBuffer(buffer),
        length: buffer ? buffer.length : 'N/A',
        preview: buffer ? buffer.slice(0, 20).toString('hex') : 'null'
      })
      
      if (buffer) {
        const base64 = Buffer.from(buffer).toString('base64')
        const mime = getMimeType(val)
        replacements.set(val, `data:${mime};base64,${base64}`)
      }
    } catch (e) {
      console.warn(`[MDD Resource] Failed to load: ${val}`, e.message || e)
      // 资源未找到是正常的，忽略错误
    }
  }))
  
  // 替换 HTML
  return html.replace(regex, (match, attr, val) => {
    if (replacements.has(val)) {
      return `${attr}="${replacements.get(val)}"`
    }
    return match
  })
}

async function queryInDict(filePath, word) {
  try {
    const { mdxLookup, mddLookup, name } = await loadMdictInstance(filePath)
    
    if (!mdxLookup) {
      throw new Error('词典查询函数未就绪')
    }
    
    let result = ''
    try {
      // mdict 的 lookup 返回数组（多条释义）
      const definitions = await mdxLookup(word)
      if (Array.isArray(definitions) && definitions.length > 0) {
        result = definitions.join('\n<hr>\n')
      }
    } catch (e) {
      // NOT FOUND 也是通过 throw 抛出的
      if (typeof e === 'string' && e.includes('NOT FOUND')) {
        result = ''
      } else {
        throw e
      }
    }
    
    // 如果有结果且有 MDD，替换资源
    if (result && mddLookup) {
      try {
        result = await replaceResources(result, mddLookup)
      } catch (e) {
        console.error('Resource replacement failed', e)
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
    return {
      dictPath: filePath,
      dictName: path.basename(filePath),
      ok: false,
      error: errMsg
    }
  }
}

// 注入到 window
window.services = {
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

  getDictList() {
    const config = loadConfig()
    const alive = config.dicts.filter(d => fs.existsSync(d.path))
    if (alive.length !== config.dicts.length) {
      config.dicts = alive
      saveConfig(config)
    }
    return alive
  },

  updateDictOrder(dicts) {
    const config = loadConfig()
    config.dicts = dicts || []
    saveConfig(config)
    return config.dicts
  },

  removeDict(filePath) {
    const config = loadConfig()
    config.dicts = config.dicts.filter(d => d.path !== filePath)
    saveConfig(config)
    dictInstances.delete(filePath)
    return config.dicts
  },

  async queryWord(word) {
    const w = (word || '').trim()
    if (!w) return []
    const config = loadConfig()
    const dicts = config.dicts || []
    
    // 串行查询以保证顺序，或者并行查询后排序？
    // 并行查询通常更快
    const promises = dicts
      .filter(d => fs.existsSync(d.path))
      .map(d => queryInDict(d.path, w))
      
    return await Promise.all(promises)
  }
}
