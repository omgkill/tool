import json
from .base_output import BaseOutput


class JsonOutput(BaseOutput):
    def save(self, data, output_path: str) -> None:
        print(f"[JsonOutput] 正在保存到: {output_path}")
        
        result = self._build_relational_data(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"[JsonOutput] 保存成功: {len(result['documents'])} 个文档, {len(result['words'])} 个单词")
    
    def _build_relational_data(self, data) -> dict:
        word_map = {}
        word_list = []
        word_id_counter = 0
        
        documents = []
        paragraphs = []
        sentences = []
        word_occurrences = []
        
        para_id_counter = 0
        sent_id_counter = 0
        occ_id_counter = 0
        
        # 支持dict和对象两种格式
        docs = data.get('documents', []) if isinstance(data, dict) else data.documents
        metadata = data.get('metadata', {}) if isinstance(data, dict) else data.metadata
        
        for doc in docs:
            # 支持dict和对象两种格式
            doc_id = doc.get('doc_id', 0) if isinstance(doc, dict) else doc.doc_id
            doc_url = doc.get('url', '') if isinstance(doc, dict) else doc.url
            doc_title = doc.get('title', '') if isinstance(doc, dict) else doc.title
            doc_depth = doc.get('depth', 0) if isinstance(doc, dict) else doc.depth
            doc_paragraphs = doc.get('paragraphs', []) if isinstance(doc, dict) else doc.paragraphs
            
            documents.append({
                'id': doc_id,
                'url': doc_url,
                'title': doc_title,
                'depth': doc_depth
            })
            
            for para in doc_paragraphs:
                para_id = para_id_counter
                para_id_counter += 1
                
                paragraphs.append({
                    'id': para_id,
                    'doc_id': doc_id,
                    'text': para.get('text', ''),
                    'para_index': para.get('para_index', 0)
                })
                
                for sent in para.get('sentences', []):
                    sent_id = sent_id_counter
                    sent_id_counter += 1
                    
                    sentences.append({
                        'id': sent_id,
                        'para_id': para_id,
                        'text': sent.get('text', '')
                    })
                    
                    for word in sent.get('words', []):
                        lemma = word.get('lemma', '')
                        if not lemma:
                            continue
                        
                        if lemma not in word_map:
                            word_map[lemma] = word_id_counter
                            word_list.append({
                                'id': word_id_counter,
                                'lemma': lemma
                            })
                            word_id_counter += 1
                        
                        occ_id = occ_id_counter
                        occ_id_counter += 1
                        
                        word_occurrences.append({
                            'id': occ_id,
                            'sent_id': sent_id,
                            'word_id': word_map[lemma],
                            'original': word.get('original', ''),
                            'pos': word.get('pos', '')
                        })
        
        return {
            'metadata': metadata,
            'words': word_list,
            'documents': documents,
            'paragraphs': paragraphs,
            'sentences': sentences,
            'word_occurrences': word_occurrences
        }
    
    def get_extension(self) -> str:
        return '.json'