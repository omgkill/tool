from parser_service.nlp.lemmatizer import Lemmatizer
from parser_service.cleaner.text_cleaner import TextCleaner
from parser_service.nlp.splitter import Splitter


class Processor:
    def __init__(self, model_name='en_core_web_sm'):
        self.lemmatizer = Lemmatizer(model_name)
        self.cleaner = TextCleaner()
        self.splitter = Splitter()
    
    def process_text(self, text):
        """处理文本：清洗 → 分段 → 词形还原"""
        # 1. 清洗
        cleaned_text = self.cleaner.clean(text)
        
        # 2. 分段
        paragraphs = self.splitter.split_paragraphs(cleaned_text)
        
        # 3. 词形还原
        processed_paragraphs = self.lemmatizer.process_text(paragraphs)
        
        return processed_paragraphs
    
    def extract_unique_words(self, processed_paragraphs):
        """提取唯一单词"""
        return self.lemmatizer.extract_unique_words(processed_paragraphs)
    
    def get_word_frequency(self, processed_paragraphs):
        """获取词频统计"""
        return self.lemmatizer.get_word_frequency(processed_paragraphs)