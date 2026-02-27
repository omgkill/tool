import spacy
from collections import Counter


class Lemmatizer:
    def __init__(self, model_name='en_core_web_sm'):
        print(f"[Lemmatizer] 正在加载spaCy模型: {model_name}")
        self.nlp = spacy.load(model_name)
        print("[Lemmatizer] 模型加载完成")
        
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'we', 'they', 'what', 'which', 'who', 'whom', 'whose',
            'if', 'then', 'else', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
            'very', 'just', 'also', 'now', 'here', 'there', 'about', 'into',
            'through', 'during', 'before', 'after', 'above', 'below', 'between',
            'under', 'again', 'further', 'once', 'your', 'my', 'his', 'her',
            'our', 'their', 'me', 'him', 'us', 'them', 'any', 'much'
        }

    def process_paragraph(self, paragraph, para_index):
        doc = self.nlp(paragraph)
        sentences = []
        
        for sent in doc.sents:
            words = []
            for token in sent:
                if token.is_alpha and len(token.text) >= 2:
                    lemma = token.lemma_.lower()
                    if lemma not in self.stopwords:
                        words.append({
                            'original': token.text.lower(),
                            'lemma': lemma,
                            'pos': token.pos_
                        })
            
            if words:
                sentences.append({
                    'text': sent.text.strip(),
                    'words': words
                })
        
        return {
            'para_index': para_index,
            'text': paragraph,
            'sentences': sentences
        }

    def process_text(self, paragraphs):
        print(f"[Lemmatizer] 正在处理 {len(paragraphs)} 个段落...")
        results = []
        
        for idx, para in enumerate(paragraphs):
            result = self.process_paragraph(para, idx)
            if result['sentences']:
                results.append(result)
        
        print(f"[Lemmatizer] 处理完成，共 {len(results)} 个有效段落")
        return results

    def extract_unique_words(self, results):
        word_set = set()
        for para in results:
            for sent in para['sentences']:
                for word in sent['words']:
                    word_set.add(word['lemma'])
        return sorted(word_set)

    def get_word_frequency(self, results):
        word_counts = Counter()
        for para in results:
            for sent in para['sentences']:
                for word in sent['words']:
                    word_counts[word['lemma']] += 1
        return word_counts.most_common()
