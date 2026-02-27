# 修改记录

## 2026-02-26 16:30 - 创建 README.md 说明文档

### 为什么修改
项目需要清晰的说明文档，方便用户快速了解如何使用。

### 修改内容
创建 `README.md` 文件，包含：
1. 快速开始 - 运行指令
2. 命令参数说明 - 参数表格
3. 示例 - 常见使用场景
4. 功能特性
5. 依赖说明
6. 项目结构
7. 自定义配置

### 修改后结果
- 用户可以快速了解项目用法
- 文档清晰易懂

---

## 2026-02-26 16:20 - 改用 wkhtmltopdf 直接从 URL 生成 PDF

### 为什么修改
之前保存 HTML 到本地后，wkhtmltopdf 处理本地文件时无法正确加载外部资源（CSS、JS、图片），导致 `ContentNotFoundError` 错误。

### 修改内容
1. 移除 HTML 缓存功能，不再保存 HTML 到本地
2. 改用 `pdfkit.from_url()` 直接从 URL 生成 PDF
3. 添加 `load-error-handling: ignore` 和 `load-media-error-handling: ignore` 选项，忽略资源加载错误
4. 简化代码：移除 `html_dir`、`get_html_filename()` 等

### 修改后结果
- PDF 可以正确渲染网页样式
- 外部资源（CSS、JS、图片）可以正常加载
- 不再有 `ContentNotFoundError` 错误

---

## 2026-02-26 16:10 - 隐藏面包屑导航 + 添加 PDF 目录

### 为什么修改
1. PDF 中仍然显示面包屑导航（如 "Documentation > Effective Go"），影响阅读
2. PDF 缺少目录/书签，不方便查找内容

### 修改内容
1. 更新 `hide_header.css` - 添加隐藏面包屑导航的 CSS 规则
2. 在 `save_page_as_pdf()` 中添加 PDF 目录选项

### 修改后结果
- PDF 中不再显示面包屑导航
- PDF 自动生成目录书签（基于 HTML 标题 h1/h2/h3）

---

## 2026-02-26 15:50 - 隐藏网站 Header 菜单

### 为什么修改
生成的 PDF 中网站 header/navigation 会覆盖在文档内容上，影响阅读。

### 修改内容
1. 创建 `hide_header.css` 文件，定义隐藏 header 的 CSS 规则
2. 在 `save_page_as_pdf()` 中添加 `user-style-sheet` 选项

### 修改后结果
- PDF 中不再显示网站的 header/navigation

---

## 2026-02-26 15:40 - 添加排除路径功能

### 为什么修改
用户只需要标准文档页面（纯文本），不需要 Codewalk（交互式代码教程）等页面。

### 修改内容
1. 添加 `EXCLUDE_PATHS` 常量
2. 添加 `is_excluded_path()` 方法

### 修改后结果
- 只爬取标准文档页面，排除 Codewalk、Tutorial 等交互式页面

---

## 2026-02-26 15:30 - 多线程优化 + 页面数量限制

### 为什么修改
提升性能，支持测试时限制页面数量。

### 修改内容
1. 添加 `max_pages` 参数
2. 添加 `max_workers` 参数
3. 使用 `ThreadPoolExecutor` 多线程处理

### 修改后结果
- 性能大幅提升（50 线程并发处理）

---

## 2026-02-26 15:20 - 添加路径过滤功能

### 为什么修改
用户只需要 `/doc/` 路径下的文档页面。

### 修改内容
1. 添加 `path_prefix` 参数
2. 添加 `is_valid_path()` 方法

### 修改后结果
- 只爬取指定路径前缀下的页面

---

## 2026-02-26 15:10 - 指定 wkhtmltopdf 路径

### 为什么修改
pdfkit 找不到 wkhtmltopdf 可执行文件。

### 修改内容
添加 `WKHTMLTOPDF_PATH` 常量指定路径。

### 修改后结果
- 程序可以正确找到 wkhtmltopdf

---

## 2026-02-26 14:30 - 初始项目创建

### 为什么修改
用户需要将 Go 官方文档网站及其子页面转换成 PDF 文件。

### 修改内容
1. 创建 `requirements.txt`
2. 创建 `web_to_pdf.py`

### 修改后结果
- 项目结构完整，可直接运行
