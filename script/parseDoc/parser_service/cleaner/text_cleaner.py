import re


class TextCleaner:
    def clean(self, text):
        print("[Cleaner] 正在清洗文本...")
        
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                line = re.sub(r'\s+', ' ', line)
                cleaned_lines.append(line)
        
        result = '\n'.join(cleaned_lines)
        print(f"[Cleaner] 清洗后文本长度: {len(result)} 字符")
        return result
