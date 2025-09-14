from typing import Dict, Any, List, Tuple, Optional
import re
from langchain_core.documents.base import Document


class RetrieverAgent:
    def __init__(self, vectorstore, k: int = 5, verbose: bool = False):
        self.vectorstore = vectorstore
        self.k = k
        self.verbose = verbose
        
        self.article_patterns = [
            r'\b(?:art\.?|artigo)\s*(\d+)(?:º|°)?\b',
            r'\bartigo\s+(\d+)\b',
            r'\bart\s+(\d+)\b'
        ]
        
        self.quality_thresholds = {
            'excellent': 0.3,
            'good': 0.6,
            'fair': 0.9
        }

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state["query"]
        
        try:
            article_number = self._detect_article_search(query)
            
            if article_number:
                return self._handle_article_search(state, query, article_number)
            else:
                return self._handle_semantic_search(state, query)
                
        except Exception as e:
            return {
                "retrieved_chunks": [],
                "agent_logs": state.get("agent_logs", []) + [f"[Retriever] Erro: {str(e)}"],
                "next_agent": "end"
            }

    def _detect_article_search(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        
        for pattern in self.article_patterns:
            match = re.search(pattern, query_lower)
            if match:
                return match.group(1)
        
        return None

    def _handle_article_search(self, state: Dict[str, Any], query: str, article_number: str) -> Dict[str, Any]:
        try:
            results = self.vectorstore.search(query, k=self.k * 3)
            classified_chunks = self._classify_article_chunks(results, article_number)
            final_chunks = self._select_best_chunks(classified_chunks)
            log = self._generate_article_search_log(classified_chunks, article_number)
            
            return {
                "retrieved_chunks": final_chunks,
                "agent_logs": state.get("agent_logs", []) + [log],
                "next_agent": "answerer" if final_chunks else "end"
            }
            
        except Exception as e:
            return {
                "retrieved_chunks": [],
                "agent_logs": state.get("agent_logs", []) + [f"[Retriever] Erro artigo {article_number}: {str(e)}"],
                "next_agent": "end"
            }

    def _handle_semantic_search(self, state: Dict[str, Any], query: str) -> Dict[str, Any]:
        try:
            results = self.vectorstore.search(query, k=self.k)
            
            chunks = []
            scores = []
            
            for doc, score in results:
                doc.metadata['similarity_score'] = score
                chunks.append(doc)
                scores.append(score)
            
            quality = self._evaluate_result_quality(scores)
            log = f"[Retriever] Busca semântica: {len(chunks)} chunks (qualidade: {quality})"
            
            return {
                "retrieved_chunks": chunks,
                "agent_logs": state.get("agent_logs", []) + [log],
                "next_agent": "answerer" if chunks else "end"
            }
            
        except Exception as e:
            return {
                "retrieved_chunks": [],
                "agent_logs": state.get("agent_logs", []) + [f"[Retriever] Erro semântica: {str(e)}"],
                "next_agent": "end"
            }

    def _classify_article_chunks(self, results: List[Tuple[Document, float]], article_number: str) -> Dict[str, List[Tuple[Document, float]]]:
        classified = {
            'direct_matches': [],
            'related_articles': [],
            'thematic_matches': [],
            'other_results': []
        }
        
        article_int = int(article_number) if article_number.isdigit() else 0
        
        for doc, score in results:
            content_lower = doc.page_content.lower()
            
            if self._contains_specific_article(content_lower, article_number):
                classified['direct_matches'].append((doc, score))
            elif self._is_related_article(content_lower, article_int):
                classified['related_articles'].append((doc, score))
            elif self._is_thematic_match(content_lower, article_number):
                classified['thematic_matches'].append((doc, score))
            else:
                classified['other_results'].append((doc, score))
        
        return classified

    def _contains_specific_article(self, content: str, article_number: str) -> bool:
        patterns = [
            rf'\bart\.?\s*{article_number}(?:º|°)?\b',
            rf'\bartigo\s*{article_number}(?:º|°)?\b'
        ]
        return any(re.search(pattern, content) for pattern in patterns)

    def _is_related_article(self, content: str, article_int: int) -> bool:
        if article_int == 0:
            return False
        
        nearby_range = range(max(1, article_int - 3), article_int + 4)
        found_articles = re.findall(r'art\.?\s*(\d+)', content)
        
        for found_art in found_articles:
            if found_art.isdigit() and int(found_art) in nearby_range:
                return True
        
        return False

    def _is_thematic_match(self, content: str, article_number: str) -> bool:
        return False

    def _select_best_chunks(self, classified_chunks: Dict[str, List[Tuple[Document, float]]]) -> List[Document]:
        final_chunks = []
        remaining_slots = self.k
        
        priorities = ['direct_matches', 'related_articles', 'thematic_matches', 'other_results']
        match_types = ['direct', 'related', 'thematic', 'other']
        
        for priority, match_type in zip(priorities, match_types):
            if remaining_slots <= 0:
                break
                
            candidates = classified_chunks[priority]
            if candidates:
                candidates.sort(key=lambda x: x[1])
                slots_to_use = min(len(candidates), remaining_slots)
                
                for doc, score in candidates[:slots_to_use]:
                    doc.metadata['match_type'] = match_type
                    doc.metadata['similarity_score'] = score
                    final_chunks.append(doc)
                
                remaining_slots -= slots_to_use
        
        return final_chunks

    def _generate_article_search_log(self, classified_chunks: Dict[str, List], article_number: str) -> str:
        direct_count = len(classified_chunks['direct_matches'])
        related_count = len(classified_chunks['related_articles'])
        thematic_count = len(classified_chunks['thematic_matches'])
        other_count = len(classified_chunks['other_results'])
        
        if direct_count > 0:
            status = f"✓ Art. {article_number} encontrado diretamente"
        elif related_count > 0:
            status = f"~ Art. {article_number} encontrado via artigos relacionados"
        elif thematic_count > 0:
            status = f"≈ Art. {article_number} encontrado via tema"
        else:
            status = f"✗ Art. {article_number} não encontrado"
        
        return f"[Retriever] {status} (d:{direct_count}, r:{related_count}, t:{thematic_count}, o:{other_count})"

    def _evaluate_result_quality(self, scores: List[float]) -> str:
        if not scores:
            return "nenhum"
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score <= self.quality_thresholds['excellent']:
            return "excelente"
        elif avg_score <= self.quality_thresholds['good']:
            return "boa"
        elif avg_score <= self.quality_thresholds['fair']:
            return "regular"
        else:
            return "baixa"