from sentence_transformers import SentenceTransformer, util
from typing import Dict, Any, List
import re

class SelfCheckAgent:   
    def __init__(self, similarity_threshold: float = 0.35, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        answer = state["raw_answer"]
        chunks = state["retrieved_chunks"]
        
        if not chunks or not answer:
            return self._reject_response(state, "Resposta ou chunks vazios")
        
        # Executar todas as validações
        similarity_score = self._calculate_similarity(answer, chunks)
        has_citations = self._check_citations_flexible(answer)
        is_too_generic = self._check_generic_response(answer)
        has_sufficient_content = self._check_content_length(answer)
        
        # Critério de aprovação: similaridade + (possui citações ou alta similaridade) + não genérica + conteúdo suficiente
        passed = (
            similarity_score > self.similarity_threshold and
            (has_citations or similarity_score > 0.7) and
            not is_too_generic and
            has_sufficient_content
        )
        
        log = self._create_validation_log(similarity_score, has_citations, is_too_generic, has_sufficient_content, passed)
        
        return {
            "final_answer": answer if passed else self._generate_rejection_message(similarity_score, has_citations),
            "self_check_passed": passed,
            "agent_logs": state.get("agent_logs", []) + [log],
            "next_agent": "safety" if passed else "end"
        }
    
    def _calculate_similarity(self, answer: str, chunks: List) -> float:
        if not chunks:
            return 0.0
        
        context_text = " ".join([doc.page_content for doc in chunks])
        
        answer_emb = self.model.encode(answer, convert_to_tensor=True)
        context_emb = self.model.encode(context_text, convert_to_tensor=True)
        
        return util.cos_sim(answer_emb, context_emb).item()
    
    def _check_citations_flexible(self, answer: str) -> bool:
        # Formato padrão: [1], [2], etc.
        if re.search(r'\[\d+\]', answer):
            return True
        
        # Formato alternativo: (1), (2), etc.
        if re.search(r'\(\d+\)', answer):
            return True
        
        # Referências por palavra-chave
        if re.search(r'(fonte|art\.|artigo|página)', answer.lower()):
            return True
        
        # Menção a documentos específicos
        if re.search(r'(plano diretor|lei|documento)', answer.lower()):
            return True
            
        return False
    
    def _check_generic_response(self, answer: str) -> bool:
        generic_phrases = [
            "é importante", "geralmente", "normalmente", "pode ser",
            "em geral", "tipicamente", "costuma ser", "é comum"
        ]
        generic_count = sum(1 for phrase in generic_phrases if phrase in answer.lower())
        return generic_count > 3
    
    def _check_content_length(self, answer: str) -> bool:
        return len(answer.strip()) > 10
    
    def _create_validation_log(self, similarity: float, has_citations: bool, is_generic: bool, 
                             has_content: bool, passed: bool) -> str:
        return (
            f"[SelfCheck] Similaridade: {similarity:.3f} (>{self.similarity_threshold}), "
            f"Citações flexíveis: {has_citations}, Genérica: {is_generic}, "
            f"Conteúdo suficiente: {has_content} → {'APROVADO' if passed else 'REJEITADO'}"
        )
    
    def _generate_rejection_message(self, similarity: float, has_citations: bool) -> str:
        if similarity <= self.similarity_threshold:
            return "A resposta não está suficientemente baseada nos documentos fornecidos. Por favor, reformule sua pergunta de forma mais específica."
        elif not has_citations:
            return "Não foi possível gerar uma resposta adequadamente referenciada para esta pergunta. Tente ser mais específico sobre o que deseja saber."
        else:
            return "Não foi possível encontrar informações suficientes nos documentos para responder adequadamente a esta pergunta."

    def _reject_response(self, state: Dict[str, Any], reason: str) -> Dict[str, Any]:
        log = f"[SelfCheck] Rejeitado: {reason}"
        
        return {
            "final_answer": "Não foi possível processar adequadamente esta solicitação.",
            "self_check_passed": False,
            "agent_logs": state.get("agent_logs", []) + [log],
            "next_agent": "end"
        }