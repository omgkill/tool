# 修改记录

## 2026-02-26 17:00
- **为什么修改**: 清理项目结构，删除无效代码和生成文件，优化输出文件管理
- **修改什么**:
  1. 删除 `main.py`：旧版入口文件，已不再使用
  2. 删除生成文件：
     - output.json
     - site_output.json
     - site_output.txt
     - test_final.pdf
     - words_output.txt
     - 修改记录.md
  3. 删除重复/过时代码：
     - parser_service/extractor/content_extract.py（已有新的extractor.py）
     - parser_service/storage/json_writer.py（已被output模块替代）
     - parser_service/crawler/url_manager.py（已不再使用）
     - parser_service/app.py（已有app_pipeline.py和main.py）
  4. 删除缓存文件：所有__pycache__目录
  5. 删除空目录：parser_service/storage/
  6. 修改 `parser_service/__init__.py`：移除对旧app的导入
  7. 修改 `parser_service/crawler/__init__.py`：移除对url_manager的导入
  8. 修改 `parser_service/pipeline/pipeline.py`：
     - 将输出路径改为output目录
     - 使用时间戳命名输出文件（格式：YYYYMMDD_HHMMSS_类型.扩展名）
  9. 修改 `app_pipeline.py`：简化参数，只保留max_pages
  10. 更新 `README.md`：添加output目录结构说明，更新使用方式
- **修改后的结果**:
  - 项目结构清晰，删除了所有无效代码和生成文件
  - 输出文件自动保存到output目录，文件名带时间戳，便于管理
  - 测试通过：成功爬取10个页面，生成了三个输出文件（JSON、TXT、PDF）
  - 处理了3005个唯一单词
  - 多线程并行工作正常

## 2026-02-26 16:45
- **为什么修改**: 修复Pipeline的max_pages参数未生效的问题，以及Output模块不支持dict格式的问题
- **修改什么**:
  1. 修改 `app_pipeline.py`：将max_pages和output_pdf参数正确传递给Pipeline配置
  2. 修改 `parser_service/output/json_output.py`：支持dict和对象两种数据格式
  3. 修改 `parser_service/output/txt_output.py`：支持dict和对象两种数据格式
  4. 修改 `parser_service/output/pdf_output.py`：支持dict和对象两种数据格式
- **修改后的结果**:
  - max_pages参数正确生效，只爬取指定数量的页面
  - Output模块同时支持dict和对象两种数据格式，兼容新旧两种架构
  - 测试通过：成功爬取2个页面，生成JSON、TXT、PDF三种输出文件

## 2026-02-26 16:30
- **为什么修改**: 将爬虫、解析、NLP处理、输出功能解耦，实现管道式架构，提高灵活性和可维护性
- **修改什么**:
  1. 创建 `parser_service/processor/` 模块：
     - 创建 `processor.py`：整合NLP处理功能（清洗、分段、词形还原）
     - 创建 `__init__.py`：模块导出
  2. 创建 `parser_service/extractor/` 模块：
     - 创建 `extractor.py`：HTML解析功能（提取文本、标题）
     - 创建 `__init__.py`：模块导出
  3. 创建 `parser_service/pipeline/` 模块：
     - 创建 `pipeline.py`：管道控制器，协调各模块工作
     - 创建 `__init__.py`：模块导出
  4. 创建 `app_pipeline.py`：使用管道架构的新入口文件
- **修改后的结果**:
  - 实现了管道式架构，各模块职责清晰
  - 支持配置化：可配置启用哪些处理步骤
  - 测试通过：多线程并行工作正常，爬取、解析、NLP处理都在正常工作
  - 架构更灵活：可以轻松跳过不需要的步骤

## 2026-02-26 16:15
- **为什么修改**: PDF中需要包含文档的原始内容，方便直接阅读
- **修改什么**:
  1. 修改 `parser_service/crawler/spider.py`：在 `DocumentData` 中添加 `html` 字段，保存原始HTML
  2. 修改 `parser_service/output/pdf_output.py`：
     - 移除原始HTML输出（太长导致PDF生成失败）
     - 改为输出文档的文本内容（从段落数据中提取）
     - PDF中包含每个文档的完整文本内容，方便阅读
- **修改后的结果**:
  - PDF文件包含文档的文本内容，适合阅读
  - 测试通过，成功生成包含2个文档、595个唯一单词的PDF文件

## 2026-02-26 16:00
- **为什么修改**: 实现网站文档转PDF功能
- **修改什么**:
  1. 创建 `parser_service/output/pdf_output.py`：使用reportlab库生成PDF文件
     - 包含文档标题、URL、深度、单词数等元数据
     - 包含每个文档的完整段落内容
     - 包含全局唯一单词列表（按词频排序）
  2. 修改 `parser_service/app.py`：
     - 添加 `PdfOutput` 导入
     - 在 `crawl_site()` 方法中添加 `output_pdf` 参数
     - 调用PDF输出功能
     - 在 `main()` 函数中添加PDF文件名命令行参数
  3. 修改 `requirements.txt`：添加 `reportlab>=4.0.0` 依赖
- **修改后的结果**:
  - 成功实现PDF输出功能
  - PDF文件包含完整的文档内容和单词统计
  - 测试通过，成功生成包含3个文档、597个唯一单词的PDF文件

## 2026-02-26 15:50
- **为什么修改**: 把线程池大小从默认的5个增加到100个，提高并发处理能力
- **修改什么**:
  1. 修改 `parser_service/crawler/spider.py`：把 `SpiderConfig` 中 `max_workers` 默认值从 5 改为 100
  2. 修改 `parser_service/app.py`：把 `crawl_site()` 方法中 `max_workers` 默认值从 5 改为 100
- **修改后的结果**:
  - 线程池默认大小为100，可以同时处理更多URL
  - 进一步提高爬取速度

## 2026-02-26 15:45
- **为什么修改**: 之前的多线程实现实际上是串行的，没有真正并行执行
- **修改什么**:
  1. 修改 `parser_service/crawler/spider.py`：
     - 完全重写 `crawl()` 方法，分为4个清晰步骤
     - 步骤1：先爬取根页面，提取所有文档链接
     - 步骤2：准备所有待处理URL列表
     - 步骤3：一次性提交所有任务到线程池，真正并行处理
     - 步骤4：聚合所有结果
     - 每个线程独立完成：抓取 -> 解析 -> 生成文档
     - 删除对 `UrlManager` 的依赖
  2. 修改 `parser_service/app.py`：在 `main()` 函数中添加 `max_pages` 命令行参数
  3. 创建 `PARALLEL_CRAWLER_FLOWCHART.md`：详细的逻辑流程图文档
- **修改后的结果**:
  - 真正的并行处理：多个线程同时工作
  - 从日志可以看出多个URL的抓取、解析是交错进行的
  - 显著提高爬取速度
  - 清晰的4步处理流程
  - 根页面只用于提取链接，不当作文档处理

## 2025-07-27 15:30
- **为什么修改**: 爬虫抓取速度慢，需要提高性能
- **修改什么**:
  1. 修改 `parser_service/crawler/url_manager.py`：添加线程安全锁，确保多线程环境下的安全操作
  2. 修改 `parser_service/crawler/spider.py`：
     - 添加 `max_workers` 参数到 `SpiderConfig`
     - 使用 `ThreadPoolExecutor` 实现多线程并行处理
     - 优化爬取流程，先处理根页面提取链接
  3. 修改 `parser_service/app.py`：添加 `max_workers` 参数到 `crawl_site` 方法
- **修改后的结果**:
  - 爬虫能够并行处理多个URL，显著提高爬取速度
  - 线程安全的URL管理，避免并发冲突
  - 保持原有功能不变，仅提升性能

## 2025-07-26 14:20
- **为什么修改**: 输出txt文件没有按照词频排序
- **修改什么**:
  1. 修改 `parser_service/output/txt_output.py`：添加词频排序功能
  2. 修改 `parser_service/storage/json_writer.py`：更新 `save_words_txt` 方法支持词频排序
- **修改后的结果**:
  - TXT输出文件中的单词按照出现次数从大到小排序
  - 保持JSON输出格式不变

## 2025-07-25 10:15
- **为什么修改**: 网络请求失败，需要添加代理支持
- **修改什么**:
  1. 修改 `parser_service/fetcher/web_fetcher.py`：添加代理配置和重试机制
  2. 配置本地代理端口为10809
- **修改后的结果**:
  - 能够通过代理正常访问目标网站
  - 增加了网络错误的重试机制，提高稳定性