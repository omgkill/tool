class Splitter:
    def split_paragraphs(self, text):
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        print(f"[Splitter] 拆分为 {len(paragraphs)} 个段落")
        return paragraphs
