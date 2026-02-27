from .base_output import BaseOutput


class TxtOutput(BaseOutput):
    def __init__(self, include_headers: bool = False):
        self.include_headers = include_headers
    
    def save(self, data, output_path: str) -> None:
        print(f"[TxtOutput] 正在保存到: {output_path}")
        
        # 支持dict和对象两种格式
        global_words = data.get('global_unique_words', []) if isinstance(data, dict) else data.global_unique_words
        word_frequency = data.get('global_word_frequency', {}) if isinstance(data, dict) else data.global_word_frequency
        
        lines = []
        
        if self.include_headers:
            lines.append(f"# 唯一单词数: {len(global_words)}")
        
        sorted_words = self._sort_by_frequency(word_frequency)
        
        for word in sorted_words:
            lines.append(word)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"[TxtOutput] 保存成功: {len(sorted_words)} 个单词")
    
    def _sort_by_frequency(self, word_frequency: dict) -> list:
        if not word_frequency:
            return []
        sorted_items = sorted(word_frequency.items(), key=lambda x: (-x[1], x[0]))
        return [word for word, freq in sorted_items]
    
    def get_extension(self) -> str:
        return '.txt'