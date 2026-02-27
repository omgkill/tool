# Web to PDF

将网站页面批量转换为 PDF 文件，支持多线程处理、路径过滤、自动生成目录书签。

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行（测试模式，只处理 5 个页面）
python web_to_pdf.py https://go.dev/doc/ 2 output 5 50

# 运行（完整模式，不限制页面数）
python web_to_pdf.py https://go.dev/doc/ 2 output 0 50
```

## 命令参数说明

```
python web_to_pdf.py <URL> [深度] [输出目录] [最大页面数] [线程数]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `URL` | 起始 URL，路径前缀自动提取 | 必填 |
| `深度` | 最大爬取深度 | 2 |
| `输出目录` | PDF 输出目录 | output |
| `最大页面数` | 限制页面数量，0 表示不限制 | 0 |
| `线程数` | 线程池大小 | 50 |

## 示例

```bash
# 爬取 Go 文档，深度 2，输出到 output 目录，最多 10 个页面，20 线程
python web_to_pdf.py https://go.dev/doc/ 2 output 10 20

# 爬取 Go 博客，不限制页面数
python web_to_pdf.py https://go.dev/blog/ 2 blog_output 0 50
```

## 功能特性

- **多线程处理**：50 线程并发生成 PDF
- **路径过滤**：只爬取指定路径下的页面
- **排除路径**：自动排除交互式教程（Codewalk、Tutorial）
- **PDF 目录**：自动基于 HTML 标题生成书签
- **隐藏元素**：自动隐藏网站 header、导航栏、面包屑

## 依赖

- Python 3.10+
- [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)

## 项目结构

```
web-to-pdf/
├── web_to_pdf.py       # 主程序
├── hide_header.css     # 隐藏 header 的 CSS
├── requirements.txt    # Python 依赖
├── CHANGELOG.md        # 修改记录
└── README.md           # 说明文档
```

## 自定义

### 修改 wkhtmltopdf 路径

编辑 `web_to_pdf.py` 中的 `WKHTMLTOPDF_PATH` 常量：

```python
WKHTMLTOPDF_PATH = r"D:\soft\wkhtmltopdf\bin\wkhtmltopdf.exe"
```

### 修改隐藏的 CSS 元素

编辑 `hide_header.css` 文件，添加需要隐藏的 CSS 选择器。

### 修改排除路径

编辑 `web_to_pdf.py` 中的 `EXCLUDE_PATHS` 常量：

```python
EXCLUDE_PATHS = [
    "/doc/codewalk/",
    "/doc/tutorial/",
]
```
