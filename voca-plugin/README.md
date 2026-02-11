# uTools + Vite + Vue 单词学习插件

这是一个基于 uTools 平台的单词学习与查词插件，技术栈采用 **Vite + Vue 3**。
它支持加载本地 MDX 词典，提供极速的查词体验，并完美适配深色模式。

## ✨ 主要功能

*   **多词典支持**：支持同时加载多个 `.mdx` 词典文件。
*   **极速查词**：基于 Node.js 优化的 `mdict` 库，毫秒级响应。
*   **富媒体支持**：完美支持 `.mdd` 资源包，图片、音频正常显示播放。
*   **深色模式**：沉浸式阅读体验，自动适配系统外观。
*   **快捷指令**：通过 uTools 关键字快速唤起。

---

## 🚀 快速开始

### 1. 环境准备

确保你已经安装了：
*   [Node.js](https://nodejs.org/) (推荐 v16+)
*   [uTools](https://u.tools/) 开发者工具

### 2. 获取代码与安装依赖

```bash
# 克隆项目
git clone https://github.com/your-repo/word-study-plugin.git
cd word-study-plugin

# 安装项目依赖
npm install

# 安装 preload 目录下的依赖 (非常重要！词典解析库在这里)
cd public/preload
npm install
cd ../..
```

### 3. 启动开发模式

在项目根目录运行：

```bash
npm run dev
```

默认会启动在 `http://localhost:5173`。

### 4. 在 uTools 中加载插件

1.  打开 uTools，输入 `插件应用市场` 并进入。
2.  点击右上角的“开发者工具”图标（或设置 -> 开发者工具）。
3.  点击“新建项目” -> “选择 `plugin.json`”。
4.  选择本项目目录下的 `public/plugin.json` 文件。
5.  插件加载成功后，你就可以在 uTools 中使用 `查词` 等指令了。

> **注意**：开发模式下，uTools 会直接加载 `http://localhost:5173`，实现代码热更新。

---

## 🛠️ 构建与发布

开发完成后，需要构建最终产物以便发布或分享。

### 1. 编译打包

在项目根目录运行：

```bash
npm run build
```

这会在根目录下生成 `dist/` 文件夹，其中包含了所有静态资源和编译后的代码。

### 2. 打包为 UPX 插件

1.  在 uTools 开发者工具中，选择本项目。
2.  点击“打包”按钮。
3.  选择 `dist` 目录作为打包目标。
4.  生成 `.upx` 文件。

---

## 📂 项目结构说明

```text
根目录
├─ index.html          // 网页入口
├─ package.json        // 前端项目依赖
├─ vite.config.js      // Vite 配置
├─ public/             // 静态资源目录 (原样拷贝到 dist)
│  ├─ plugin.json      // uTools 插件核心配置
│  ├─ logo.png         // 插件图标
│  └─ preload/         // Node.js 后端能力层
│     ├─ services.js   // 注入 window.services 的核心脚本
│     └─ package.json  // preload 层独立的依赖配置
└─ src/                // Vue 前端源码
   ├─ App.vue          // 根组件 (处理路由分发)
   ├─ Mdict/           // 核心功能：词典查询组件
   └─ ...
```

## 🧩 常见问题

**Q: 为什么图片或音频无法加载？**
A: 请确保对应的 `.mdd` 文件与 `.mdx` 文件在同一目录下，且文件名相同（仅后缀不同）。

**Q: 查词速度慢？**
A: 首次加载大词典（如几百 MB）会建立索引，稍慢是正常的。之后查询会非常快。

**Q: 开发时报错 `MDX not found`？**
A: 请务必执行 `cd public/preload && npm install`，因为词典解析库 `mdict` 是安装在 `public/preload` 目录下的。
