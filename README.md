# uTools + Vite + Vue 插件开发说明（当前项目）

## 1. 项目整体结构

当前主要目录和文件结构：

```text
根目录
├─ index.html          // 网页入口（Vite 使用）
├─ package.json        // 项目依赖和脚本
├─ vite.config.js      // Vite 配置
├─ public/             // 静态资源 & uTools 配置、preload
│  ├─ plugin.json      // uTools 插件清单（指令、入口、预加载等）
│  ├─ logo.png         // 插件图标
│  └─ preload/
│     ├─ services.js   // 预加载脚本（注入 Node 能力到 window）
│     └─ package.json  // 指定 type: commonjs
└─ src/                // Vue 前端代码
   ├─ main.js          // Vue 应用入口
   ├─ main.css         // 全局样式
   ├─ App.vue          // 根组件，负责根据 uTools 功能 code 切换页面
   ├─ Hello/index.vue  // 功能：hello 示例
   ├─ Read/index.vue   // 功能：读文件示例
   └─ Write/index.vue  // 功能：写文件示例
```

简单理解：

- `public/`：给 uTools 和浏览器 **直接访问** 的静态文件（不参与打包编译，原样拷贝）
- `src/`：Vue SPA 应用源码，所有页面、逻辑都在这里
- `index.html`：Vite 的 HTML 入口文件，里面挂载 `#app`，加载 `src/main.js`

---

## 2. 运行与开发流程

### 2.1 安装依赖

在项目根目录：

```bash
npm install
```

### 2.2 启动开发服务器

```bash
npm run dev
```

默认会启动在 `http://localhost:5173`。

此时你可以：

- 直接在浏览器打开 `http://localhost:5173` 调试界面（开发阶段）
- 在 uTools 的插件开发/调试模式中，让插件使用这个地址作为前端入口

项目里已经在 `public/plugin.json` 配好了：

```jsonc
"development": {
  "main": "http://localhost:5173"
}
```

这表示：在开发模式下，uTools 会用这个 URL 作为插件窗口的网页内容（而不是本地打包后的 HTML）。

---

## 3. public 目录的作用

`public/` 是 Vite 的静态资源目录，有两个关键特性：

1. **开发时**：通过 `/文件名` 直接访问，例如 `/plugin.json`、`/logo.png`、`/preload/services.js`
2. **打包时**：所有文件原样拷贝到 `dist/` 根目录

与你的 uTools 插件相关的内容：

- `public/plugin.json`：插件配置（指令、入口、图标、预加载等）
- `public/logo.png`：插件图标
- `public/preload/services.js`：预加载脚本（在 BrowserWindow 中注入 `window.services` 等）

> 你不需要“导出到 public”。
> 只要把要给 uTools 用的静态文件直接放进 `public/`，构建时会自动拷贝到 `dist/`。

---

## 4. plugin.json 与“指令”的关系

`public/plugin.json` 的作用：告诉 uTools：

- 这个插件有哪些功能（`features`）
- 每个功能用什么“指令”（`cmds`）触发
- 要载入哪个页面（`main`）以及哪个 preload（`preload`）

关键字段示例：

```jsonc
{
  "main": "index.html",          // 插件窗口加载的页面（构建后在 dist/index.html）
  "preload": "preload/services.js",
  "logo": "logo.png",
  "development": {
    "main": "http://localhost:5173"
  },
  "features": [
    {
      "code": "hello",
      "explain": "这是插件应用的第一个功能",
      "cmds": [
        "你好",
        "hello"
      ]
    },
    {
      "code": "read",
      "explain": "使用 node.js 能力读文件",
      "cmds": [
        "读文件",
        {
          "type": "files",
          "fileType": "file",
          "maxLength": 1,
          "label": "读文件"
        }
      ]
    }
  ]
}
```

含义：

- `code`：功能的唯一标识（例如 `"hello"`、`"read"`）
- `cmds`：用户在 uTools 搜索框输入的内容
  - 词条 `"你好"`、`"hello"`：普通文字指令
  - 对象 `{ "type": "files", ... }`：文件匹配指令
- 在 uTools 中，当用户输入匹配到 `cmds` 的内容时，uTools 会：
  1. 打开插件窗口
  2. 执行 `preload/services.js`
  3. 载入 `main` 指定的页面（开发时是 `development.main`）

然后在网页里，通过 `window.utools.onPluginEnter` 拿到这个进入事件。

---

## 5. preload：如何把 Node 能力注入前端

`public/preload/services.js`：

```js
const fs = require('node:fs')
const path = require('node:path')

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
  }
}
```

作用：

- 在 uTools 的 BrowserWindow 启动时，这个脚本会先执行
- 它是 Node 环境，可以使用 `fs`、`path` 等 Node 模块
- 把需要的能力挂到 `window.services`，在前端页面里就能 `window.services.xxx()` 调用

例如在 `Read/index.vue` 中：

```ts
const content = window.services.readFile(_filePath)
```

---

## 6. App.vue：如何根据“指令对应的 code”切换页面

`src/App.vue` 做的事情：

1. 监听 uTools 的“插件进入”事件
2. 读取 `action.code`（也就是 `plugin.json` 中的 `features[i].code`）
3. 根据不同 code 显示不同组件

简化版流程：

```vue
<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import Hello from './Hello/index.vue'
import Read from './Read/index.vue'
import Write from './Write/index.vue'

const route = ref('')
const enterAction = ref<any>({})

onMounted(() => {
  // uTools 中，插件被指令触发时会调用这里
  window.utools.onPluginEnter((action) => {
    // action.code 就是 plugin.json 里配置的 code
    route.value = action.code
    enterAction.value = action
  })

  window.utools.onPluginOut(() => {
    route.value = ''
  })
})
</script>

<template>
  <template v-if="route === 'hello'">
    <Hello :enterAction="enterAction" />
  </template>
  <template v-else-if="route === 'read'">
    <Read :enterAction="enterAction" />
  </template>
  <template v-else-if="route === 'write'">
    <Write :enterAction="enterAction" />
  </template>
</template>
```

对应关系：

- uTools 输入“你好” → 触发 `code: "hello"` → `route = "hello"` → 显示 `<Hello>`
- uTools 输入“读文件” → 触发 `code: "read"` → `route = "read"` → 显示 `<Read>`

当你以后要增加“MDX 查词”功能时，只需要：

1. 在 `plugin.json` 的 `features` 里新增一个功能，例如：

   ```jsonc
   {
     "code": "mdict",
     "explain": "多词典 MDX 查询",
     "cmds": ["查词", "mdict"]
   }
   ```

2. 新建一个 `src/Mdict/index.vue` 页面
3. 在 `App.vue` 里 `import Mdict from './Mdict/index.vue'`，然后：

   ```vue
   <template v-if="route === 'mdict'">
     <Mdict :enterAction="enterAction" />
   </template>
   ```

就完成了“指令 → code → 前端页面”的整个闭环。

---

## 7. 构建和打包给 uTools 使用

开发完成后，构建前端：

```bash
npm run build
```

会生成一个 `dist/` 目录，大致结构：

```text
dist/
├─ index.html          // 构建后的入口页面
├─ assets/             // 打包好的 JS、CSS
├─ plugin.json         // 从 public 拷贝来
├─ logo.png            // 从 public 拷贝来
└─ preload/
   └─ services.js      // 从 public/preload 拷贝来
```

此时：

- `plugin.json` 指向的 `"main": "index.html"`、`"preload": "preload/services.js"` 会在 `dist/` 中都能找到
- 按 uTools 官方要求将 `dist` 内容打包成 `.upx` 插件文件即可
