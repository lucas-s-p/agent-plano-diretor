from langchain_core.documents import Document
import re
from typing import List, Dict, Tuple


class LegalSplitter:
    """Splitter que combina busca literal e semântica"""
    
    def __init__(self, max_chunk_size: int = 1600, chunk_overlap: int = 180):
        self.max_chunk_size = max_chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Padrões para identificar artigos
        self.article_pattern = re.compile(
            r'(?:^|\n)\s*(?:Art|Artigo)\.?\s*(\d+)(?:º|°)?\s*[-.]?\s*', 
            re.MULTILINE | re.IGNORECASE
        )
    
    def split_text(self, text: str, metadata: Dict) -> Tuple[List[Document], Dict]:
        """Divide texto e retorna chunks + índice literal"""
        
        # Limpar texto
        text = self._clean_text(text)
        
        # Extrair artigos
        article_chunks = self._extract_articles(text, metadata)
        
        # Criar chunks temáticos
        thematic_chunks = self._create_thematic_chunks(text, metadata)
        
        # Combinar chunks
        all_chunks = article_chunks + thematic_chunks
        
        # Criar índice literal
        literal_index = self._create_literal_index(all_chunks)
        
        # Filtrar chunks válidos
        valid_chunks = [c for c in all_chunks if len(c.page_content.strip()) >= 80]
        
        return valid_chunks, literal_index
    
    def _clean_text(self, text: str) -> str:
        """Limpeza básica do texto"""
        
        patterns = [
            r'Assinado por.*?(?=\n|$)',
            r'Para verificar.*?(?=\n|$)',
            r'https?://[^\s]+',
            r'ESTADO DA PARA[ÍI]BA.*?GABINETE DO PREFEITO(?:\n|$)',
        ]
        
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE | re.DOTALL)
        
        # Normalizar
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\b(?:Art|Artigo)\.?\s*(\d+)(?:º|°)?\s*[-.]?', 
                     r'Art. \1.', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _extract_articles(self, text: str, metadata: Dict) -> List[Document]:
        """Extrai artigos com contexto preservado"""
        
        chunks = []
        article_matches = list(self.article_pattern.finditer(text))
        
        for i, match in enumerate(article_matches):
            article_num = match.group(1)
            start_pos = match.start()
            
            # Determinar fim do artigo
            if i + 1 < len(article_matches):
                end_pos = article_matches[i + 1].start()
            else:
                end_pos = len(text)
            
            article_text = text[start_pos:end_pos].strip()
            
            if len(article_text) < 50:
                continue
            
            # Criar chunks do artigo
            if len(article_text) <= self.max_chunk_size:
                chunk = self._create_article_chunk(article_text, article_num, metadata)
                chunks.append(chunk)
            else:
                # Dividir artigo grande
                article_parts = self._split_large_article(article_text, article_num, metadata)
                chunks.extend(article_parts)
        
        return chunks
    
    def _create_article_chunk(self, text: str, article_num: str, metadata: Dict) -> Document:
        """Cria chunk para um artigo com metadados otimizados"""
        
        chunk_metadata = metadata.copy()
        chunk_metadata.update({
            'article_number': article_num,
            'chunk_type': 'article',
            'contains_article': article_num,
            'search_terms': f"Art.{article_num} Artigo{article_num} Art.{article_num}. Artigo{article_num}.",
            'topic_tags': self._get_topic_tags(article_num)
        })
        
        return Document(
            page_content=text,
            metadata=chunk_metadata
        )
    
    def _split_large_article(self, text: str, article_num: str, metadata: Dict) -> List[Document]:
        """Divide artigos grandes preservando estrutura"""
        
        chunks = []
        
        # Dividir por incisos
        inciso_pattern = r'\n\s*([IVX]+\s*[-–]\s*)'
        parts = re.split(inciso_pattern, text)
        
        if len(parts) > 3:
            current_chunk = parts[0] 
            
            for i in range(1, len(parts), 2):
                if i + 1 < len(parts):
                    inciso_marker = parts[i]
                    inciso_content = parts[i + 1]
                    inciso_full = inciso_marker + inciso_content
                    
                    if len(current_chunk) + len(inciso_full) <= self.max_chunk_size:
                        current_chunk += inciso_full
                    else:
                        if current_chunk.strip():
                            chunk = self._create_article_part_chunk(
                                current_chunk, article_num, metadata, len(chunks)
                            )
                            chunks.append(chunk)
                        
                        current_chunk = f"Art. {article_num}. (continuação {len(chunks)})\n" + inciso_full
            
            if current_chunk.strip():
                chunk = self._create_article_part_chunk(
                    current_chunk, article_num, metadata, len(chunks)
                )
                chunks.append(chunk)
        else:
            # Dividir por parágrafos
            paragraphs = text.split('\n\n')
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk) + len(para) <= self.max_chunk_size:
                    current_chunk += para + '\n\n'
                else:
                    if current_chunk.strip():
                        chunk = self._create_article_part_chunk(
                            current_chunk, article_num, metadata, len(chunks)
                        )
                        chunks.append(chunk)
                    
                    current_chunk = para + '\n\n'
            
            if current_chunk.strip():
                chunk = self._create_article_part_chunk(
                    current_chunk, article_num, metadata, len(chunks)
                )
                chunks.append(chunk)
        
        return chunks
    
    def _create_article_part_chunk(self, text: str, article_num: str, 
                                 metadata: Dict, part_index: int) -> Document:
        """Cria chunk para parte de um artigo"""
        
        chunk_metadata = metadata.copy()
        chunk_metadata.update({
            'article_number': article_num,
            'chunk_type': 'article_part',
            'contains_article': article_num,
            'part_index': part_index,
            'search_terms': f"Art.{article_num} Artigo{article_num} Art.{article_num}. Artigo{article_num}.",
            'topic_tags': self._get_topic_tags(article_num)
        })
        
        return Document(
            page_content=text.strip(),
            metadata=chunk_metadata
        )
    
    def _get_topic_tags(self, article_num: str) -> List[str]:
        """Tags temáticas por artigo"""
        
        article_int = int(article_num) if article_num.isdigit() else 0
        tags = []
        
        if 170 <= article_int <= 180:
            tags.extend(['cidade_inteligente', 'tecnologia', 'inovacao'])
        
        if article_num == '175':
            tags.extend(['diretrizes', 'politica_cidade_inteligente', 'governo_aberto'])
        elif article_num == '178':
            tags.extend(['participacao', 'controle_social', 'participacao_cidada'])
        
        return tags
    
    def _create_thematic_chunks(self, text: str, metadata: Dict) -> List[Document]:
        """Cria chunks temáticos para melhor cobertura"""
        
        chunks = []
        
        themes = {
            'cidade_inteligente': [
                'cidade inteligente', 'governo aberto', 'tecnologia urbana',
                'inovação', 'digitalização', 'smart city'
            ],
            'participacao_social': [
                'participação social', 'controle social', 'participação cidadã',
                'democracia participativa'
            ]
        }
        
        for theme_name, keywords in themes.items():
            theme_content = self._extract_thematic_content(text, keywords)
            
            if theme_content and len(theme_content) >= 200:
                theme_metadata = metadata.copy()
                theme_metadata.update({
                    'chunk_type': 'thematic',
                    'theme': theme_name,
                    'keywords': keywords
                })
                
                chunks.append(Document(
                    page_content=theme_content,
                    metadata=theme_metadata
                ))
        
        return chunks
    
    def _extract_thematic_content(self, text: str, keywords: List[str]) -> str:
        """Extrai conteúdo relacionado a tema específico"""
        
        sentences = re.split(r'[.!?]+', text)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue
            
            sentence_lower = sentence.lower()
            if any(keyword.lower() in sentence_lower for keyword in keywords):
                relevant_sentences.append(sentence)
        
        return '. '.join(relevant_sentences[:8]) if relevant_sentences else ""
    
    def _create_literal_index(self, chunks: List[Document]) -> Dict:
        """Cria índice literal para busca direta"""
        
        literal_index = {}
        
        for i, chunk in enumerate(chunks):
            # Indexar por número de artigo
            article_num = chunk.metadata.get('article_number')
            if article_num:
                if article_num not in literal_index:
                    literal_index[article_num] = []
                literal_index[article_num].append(i)
            
            # Indexar por artigos mencionados no texto
            article_matches = re.findall(r'\bArt\.?\s*(\d+)', chunk.page_content, re.IGNORECASE)
            for art in article_matches:
                if art not in literal_index:
                    literal_index[art] = []
                if i not in literal_index[art]:
                    literal_index[art].append(i)
        
        return literal_index