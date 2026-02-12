
## fengdh/mdict-js/js-mdict vs mdict

| 特性 | 当前 mdict (Node.js) | 旧版 fengdh/mdict-js (浏览器) |
|------|---------------------|------------------------------|
| **文件访问** | 直接磁盘访问 (fs.read, fs.readSync) | Blob/ArrayBuffer (浏览器API) |
| **索引构建** | 流式解析，按需读取 | 全量加载到内存 |
| **内存使用** | 只缓存索引，内容按需读取 | 整个文件或大块载入内存 |
| **性能特点** | 初始化快，查询快，内存占用低 | 初始化慢，查询快，内存占用高 |
| **适用场景** | Node.js/Electron 后端 | 纯浏览器前端 |

## 关键原理详解：

### 1. **Node.js mdict 的工作机制**
```javascript
// 实际上是"懒加载"数据库模式
class MdictNodeJS {
  constructor(filePath) {
    this.filePath = filePath;
    this.index = null;      // 只存索引
    this.contentOffsets = new Map(); // 内容偏移量映射
  }
  
  async init() {
    // 1. 读取文件头部信息（快速）
    const header = await readFileHeader(this.filePath);
    
    // 2. 解析关键块（key block）建立索引
    // 只读取索引部分，不读取内容！
    this.index = await parseKeyBlock(this.filePath, header.keyBlockInfo);
    
    // 3. 记录每个词条的内容位置（偏移量，大小）
    // 不实际读取内容，只记录"指针"
    this.contentOffsets = await buildOffsetMap(this.filePath);
  }
  
  lookup(word) {
    // 1. 在内存索引中查找单词
    const entry = this.index.binarySearch(word);
    
    if (entry) {
      // 2. 根据记录的偏移量，只读取这个单词的内容
      const content = this.readContentAtOffset(entry.offset, entry.size);
      return content;
    }
    
    return null;
  }
  
  // 关键：按需读取特定位置的内容
  readContentAtOffset(offset, size) {
    // 使用 fs.read 直接读取文件的特定部分
    const buffer = Buffer.alloc(size);
    const fd = fs.openSync(this.filePath, 'r');
    fs.readSync(fd, buffer, 0, size, offset);
    fs.closeSync(fd);
    return buffer.toString('utf-8');
  }
}
```

### 2. **为什么你的应用查询快？**

你的 `services.js` 中是这样使用的：
```javascript
// 1. 先加载词典（只加载索引）
const dict = new MdictClass(filePath);
await dict.init();  // 这里只加载索引，不加载内容

// 2. 查询时按需读取内容
const definition = dict.lookup(word);
// 实际发生：fs.read(特定偏移量, 特定大小)
```

**这就是"数据库模式"的优势**：
- 词典文件像数据库表
- 索引在内存中（搜索快）
- 内容在磁盘上（按需读取）

### 3. **验证：查看 mdict 库的源码**

查看 `node_modules/mdict/lib/mdict-base.js`，你会发现：

```javascript
// 简化的源码结构
class MDict {
  constructor(filePath) {
    this.filePath = filePath;
    this._keyList = [];    // 词条列表（索引）
    this._recordBlock = []; // 记录块信息（不包含内容）
    this._rs = null;       // 文件读取流
  }
  
  async init() {
    // 1. 打开文件流
    this._rs = fs.createReadStream(this.filePath);
    
    // 2. 读取并解析头部
    await this._parseHeader();
    
    // 3. 读取并解析关键块（建立索引）
    await this._parseKeyBlock();
    
    // 4. 读取记录块信息（记录位置，不读内容）
    await this._parseRecordBlock();
  }
  
  lookup(keyword) {
    // 1. 在内存索引中查找
    const index = this._keyList.findIndex(item => item.key === keyword);
    
    if (index >= 0) {
      // 2. 获取记录块信息
      const recordInfo = this._recordBlock[index];
      
      // 3. 按需读取内容
      return this._readRecord(recordInfo);
    }
    
    return null;
  }
  
  _readRecord(recordInfo) {
    // 关键：使用 fs.read 读取特定位置
    const buffer = Buffer.alloc(recordInfo.compressedSize);
    const fd = fs.openSync(this.filePath, 'r');
    
    // 直接跳到文件中的 recordInfo.offset 位置
    fs.readSync(fd, buffer, 0, recordInfo.compressedSize, recordInfo.offset);
    fs.closeSync(fd);
    
    // 解压并返回
    return this._decompress(buffer, recordInfo);
  }
}
```

## 为什么 m3.mdx 加载仍然慢？

虽然这个库是优化的，但 **m3.mdx 有 340 万词条**：

### 加载过程：
```
1. 读取文件头部: 快速
2. 解析关键块（key block）: 需要解析 340 万条索引
3. 构建内存索引: 340 万条记录需要内存和时间

总耗时: 44秒（主要花在解析和构建索引上）
```

### 但查询很快：
```javascript
// 查询时：
dict.lookup('make'); 
// 1. 在340万条索引中二分查找（内存中，很快）
// 2. 找到后，直接读取磁盘上对应的内容（很快）
```

## 与其他词典软件对比：

### GoldenDict / MDict PC：
```python
# 类似的原理
def load_mdx(self, filepath):
    # 1. 读取mdx文件
    # 2. 解析索引到内存（可能用B+树或哈希表）
    # 3. 内容保留在磁盘或缓存中
    
def query(self, word):
    # 1. 内存索引查找
    # 2. 磁盘读取内容
```

### 纯浏览器版本：
```javascript
// 受浏览器限制
async loadMdxInBrowser(file) {
  // 1. 读取整个文件到内存
  const arrayBuffer = await file.arrayBuffer();
  
  // 2. 在内存中解析（消耗大量内存）
  const dataView = new DataView(arrayBuffer);
  
  // 3. 所有内容都在内存中
  // 对于340万词条的词典，可能占用>1GB内存
}
```

## 性能优化建议（针对当前库）：

### 1. **延迟索引构建**
```javascript
// 对于超大词典，可以延迟构建完整索引
class LazyMdict extends MDict {
  async initPartial() {
    // 只加载必要的部分
    await this._parseHeader();
    
    // 延迟加载索引：先加载前10万条常用词
    await this._loadPartialKeyBlock(0, 100000);
    
    // 其他索引在后台加载
    this._loadRemainingKeyBlockInBackground();
  }
}
```

### 2. **使用更高效的索引结构**
```javascript
// 当前可能是数组 + 二分查找
// 可以改为：前缀树、哈希表等

// 改进的查找
class OptimizedMDict extends MDict {
  buildTrieIndex() {
    // 为常用前缀构建前缀树
    // 对于"make"这样的词，可以直接在树中查找
  }
}
```

### 3. **内容缓存**
```javascript
// 缓存最近查询的内容
class CachedMDict extends MDict {
  constructor(filePath) {
    super(filePath);
    this.cache = new LRUCache(1000); // 缓存1000条最近查询
  }
  
  lookup(keyword) {
    // 1. 检查缓存
    if (this.cache.has(keyword)) {
      return this.cache.get(keyword);
    }
    
    // 2. 正常查询
    const result = super.lookup(keyword);
    
    // 3. 加入缓存
    if (result) {
      this.cache.set(keyword, result);
    }
    
    return result;
  }
}
```

## 总结

**你的应用现在查询快的原因是：**

1. **使用了专门优化的 Node.js mdict 库**
2. **库采用了"数据库"模式：索引在内存，内容在磁盘**
3. **按需读取内容，而不是全量加载**
4. **直接文件系统访问，没有浏览器限制**

**但加载 m3.mdx 慢的原因是：**
- 340万词条的索引构建本身就是耗时的
- 这是不可避免的，但可以通过延迟加载、分块加载等策略优化用户体验

**正确的做法是：**
- 小词典立即加载
- 大词典延迟加载或在后台加载
- 查询时使用已加载的词典（查询是快的）
