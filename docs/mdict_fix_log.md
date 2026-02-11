# mdict 库 MDD 文件支持修复文档

## 问题背景

在本项目中，我们使用 `mdict` (v1.0.3) 库来解析 `.mdx` 词典文件。该库基于 `mdict-js` 修改，针对 Node.js 环境进行了优化，查词速度非常快。

然而，在尝试加载配套的 `.mdd` 资源文件（包含图片、音频、CSS 等）时，遇到了严重问题：无法正确读取资源内容，导致图片裂图、音频无法播放。

## 原因分析

经过深入的源码分析，发现 `mdict` 库在处理 `.mdd` 文件时存在以下核心缺陷：

1.  **二进制数据处理错误**：
    *   `mdict` 的核心设计目标是查词（文本），因此其底层数据读取函数 `readRaw` 默认返回的是 `Uint8Array` 视图。
    *   在 Node.js 环境下，这种视图在后续处理流程中容易被隐式转换为字符串（String），或者在传递给需要 `Buffer` 的接口时出现类型不兼容。
    *   对于 `.mdd` 文件中的图片、音频等二进制数据，一旦被当作文本编码（如 UTF-8）处理，数据就会被截断或损坏。

2.  **加载逻辑的限制**：
    *   库的加载入口依赖于传入文件对象的 `name` 属性来判断扩展名（从而决定是作为 `.mdx` 还是 `.mdd` 解析）。
    *   直接传入文件路径字符串时，无法触发 `.mdd` 的特定解析逻辑。

3.  **API 参数类型错误**：
    *   在使用 `Buffer` 模拟文件对象传入时，底层的 `fs.open` 调用在某些情况下接收到了错误类型的参数（如 `undefined` 或 `Buffer` 对象本身），导致崩溃。

## 解决方案

我们采用了**“最小侵入式修改”**的策略，在保留 `mdict` 高性能查词优势的前提下，通过以下步骤完美修复了 `.mdd` 支持：

### 1. 加载层 Hack (在 `services.js` 中)

为了绕过库的文件扩展名检测逻辑，我们利用 Node.js `fs.open` 支持 Buffer 路径的特性，构造了一个带有 `name` 属性的 Buffer 对象：

```javascript
// 伪造一个带有 name 属性的文件对象
const mddBuf = Buffer.from(mddPath);
mddBuf.name = mddPath; // 关键：让 parser 识别出 .mdd 后缀
files.push(mddBuf);
```

### 2. 源码层修正 (在 `node_modules/mdict/mdict-parser.js` 中)

我们对库的源码进行了精准的手术式修改：

*   **修复 `sliceThen` 函数**：
    显式处理传入的 Buffer 路径，将其转换回字符串，确保 `fs.open` 始终接收标准的文件路径，避免了 "The first argument must be of type string..." 错误。

    ```javascript
    // 修复前：直接传 Buffer 给 fs.open，可能导致兼容性问题
    // 修复后：
    if (Buffer.isBuffer(file)) {
      file = file.toString('utf8');
    }
    ```

*   **重写 `readRaw` 函数**：
    这是最关键的一步。强制使用 Node.js 的 `Buffer` 来存储读取的数据，确保二进制内容的绝对完整性。

    ```javascript
    // 修复前：返回 Uint8Array，导致二进制数据在后续处理中损坏
    // 修复后：
    readRaw: function(len) {
      if (typeof len !== 'number') {
        len = buf.length - offset; // 修复 len 为 undefined 时的报错
      }
      var raw = Buffer.alloc(len); // 使用 Buffer.alloc 分配内存
      buf.copy(raw, 0, offset, offset + len); // 拷贝数据
      return conseq(raw, ...); // 返回真正的 Buffer 对象
    }
    ```

*   **资源泄露修复**：
    顺手修复了原库在读取文件后未关闭文件描述符 (`fd`) 的问题，添加了 `fs.close(fd)`。

## 结果验证

经过上述修复：
1.  **查词速度**：`.mdx` 查询依然保持毫秒级的极速响应。
2.  **资源加载**：`.mdd` 中的图片（JPG/PNG）、音频（MP3/WAV）等资源现在能被正确读取为 Node.js `Buffer` 对象。
3.  **前端展示**：配合前端的 `replaceResources` 逻辑（将 Buffer 转为 Base64 Data URI），所有词典资源均能完美显示和播放。

现在，项目拥有了一个既高性能又功能完整的词典解析核心。
