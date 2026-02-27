from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from parser_service.output.base_output import BaseOutput


class PdfOutput(BaseOutput):
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """设置PDF样式"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            textColor='#000000',
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor='#333333'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomURL',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor='#0066cc',
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomContent',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leading=14
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomWordList',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leftIndent=20
        ))
    
    def save(self, site_data, output_path: str = 'site_output.pdf'):
        """保存为PDF文件"""
        # 支持dict和对象两种格式
        source_url = site_data.get('source_url', '') if isinstance(site_data, dict) else site_data.source_url
        metadata = site_data.get('metadata', {}) if isinstance(site_data, dict) else site_data.metadata
        documents = site_data.get('documents', []) if isinstance(site_data, dict) else site_data.documents
        global_words = site_data.get('global_unique_words', []) if isinstance(site_data, dict) else site_data.global_unique_words
        word_freq = site_data.get('global_word_frequency', {}) if isinstance(site_data, dict) else site_data.global_word_frequency
        
        pdf_doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        story = []
        
        # 添加标题
        story.append(Paragraph("网站文档爬取结果", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # 添加元数据
        story.append(Paragraph(f"源URL: {source_url}", self.styles['CustomURL']))
        story.append(Paragraph(f"爬取时间: {metadata.get('crawled_at', 'N/A')}", self.styles['CustomURL']))
        story.append(Paragraph(f"总文档数: {len(documents)}", self.styles['CustomURL']))
        story.append(Paragraph(f"总唯一单词数: {len(global_words)}", self.styles['CustomURL']))
        story.append(Spacer(1, 24))
        
        # 添加每个文档的内容
        for doc in documents:
            # 支持dict和对象两种格式
            doc_id = doc.get('doc_id', 0) if isinstance(doc, dict) else doc.doc_id
            doc_title = doc.get('title', '') if isinstance(doc, dict) else doc.title
            doc_url = doc.get('url', '') if isinstance(doc, dict) else doc.url
            doc_depth = doc.get('depth', 0) if isinstance(doc, dict) else doc.depth
            doc_word_count = doc.get('word_count', 0) if isinstance(doc, dict) else doc.word_count
            doc_paragraphs = doc.get('paragraphs', []) if isinstance(doc, dict) else doc.paragraphs
            
            story.append(Paragraph(f"文档 {doc_id}: {doc_title}", self.styles['CustomSubtitle']))
            story.append(Paragraph(f"URL: {doc_url}", self.styles['CustomURL']))
            story.append(Paragraph(f"深度: {doc_depth}", self.styles['CustomURL']))
            story.append(Paragraph(f"单词数: {doc_word_count}", self.styles['CustomURL']))
            story.append(Spacer(1, 6))
            
            # 添加文档内容（从段落数据中提取文本）
            if doc_paragraphs:
                for para in doc_paragraphs:
                    para_text = self._format_paragraph(para)
                    if para_text.strip():
                        story.append(Paragraph(para_text, self.styles['CustomContent']))
            
            story.append(Spacer(1, 12))
            story.append(PageBreak())
        
        # 添加全局单词列表
        story.append(Paragraph("全局唯一单词列表", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # 按词频排序
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        for word, count in sorted_words:
            story.append(Paragraph(f"{word}: {count}", self.styles['CustomWordList']))
        
        # 构建PDF
        pdf_doc.build(story)
        print(f"[PdfOutput] PDF保存成功: {output_path}")
        print(f"[PdfOutput] 包含 {len(documents)} 个文档, {len(global_words)} 个唯一单词")
    
    def _format_paragraph(self, para_data: dict) -> str:
        """格式化段落数据为文本"""
        if not para_data:
            return ""
        
        sentences = para_data.get('sentences', [])
        if not sentences:
            return ""
        
        text_parts = []
        for sent in sentences:
            words = sent.get('words', [])
            if words:
                word_texts = [w.get('text', '') for w in words]
                text_parts.append(' '.join(word_texts))
        
        return ' '.join(text_parts)
    
    def get_extension(self) -> str:
        return '.pdf'