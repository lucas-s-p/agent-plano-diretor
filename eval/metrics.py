from typing import List, Dict


class RAGMetrics:
    """Calculadora de métricas manuais para avaliação RAG"""
    
    def calculate_all_metrics(self, answer: str, question: str, context_chunks, expected_topics: List[str]) -> Dict[str, float]:
        """Calcula todas as métricas para uma pergunta"""
        return {
            "faithfulness": self.calculate_faithfulness(answer, context_chunks),
            "answer_relevancy": self.calculate_answer_relevancy(answer, question),
            "context_precision": self.calculate_context_precision(context_chunks, expected_topics),
            "context_recall": self.calculate_context_recall(context_chunks, expected_topics)
        }

    def calculate_faithfulness(self, answer: str, context_chunks) -> float:
        """
        Calcula fidelidade da resposta ao contexto recuperado
        """
        if not context_chunks or not answer:
            return 0.0
        
        score = 0.0
        
        # 1. Presença de citações (0-0.3)
        if any(citation in answer for citation in ["[1]", "[2]", "[3]", "(1)", "(2)"]):
            score += 0.3
        elif "Fontes:" in answer or any(ref in answer for ref in ["Art.", "Artigo"]):
            score += 0.2
        
        # 2. Sobreposição semântica com contexto (0-0.3)
        context_text = " ".join([chunk.page_content for chunk in context_chunks])
        context_words = set(context_text.lower().split())
        answer_words = set(answer.lower().split())
        overlap = len(context_words.intersection(answer_words))
        
        if overlap >= 10:
            score += 0.3
        elif overlap >= 5:
            score += 0.2
        elif overlap >= 2:
            score += 0.1
        
        # 3. Não é especulativo (0-0.2)
        speculative_phrases = ["talvez", "possivelmente", "provavelmente", "pode ser que"]
        if not any(phrase in answer.lower() for phrase in speculative_phrases):
            score += 0.2
        
        # 4. Tem conteúdo substantivo (0-0.2)
        if len(answer.split()) >= 15:
            score += 0.2
        elif len(answer.split()) >= 8:
            score += 0.1
        
        return min(1.0, score)

    def calculate_answer_relevancy(self, answer: str, question: str) -> float:
        """
        Calcula relevância da resposta à pergunta 
        Avalia se a resposta é pertinente e direta
        """
        if not answer or not question:
            return 0.0
        
        score = 0.0
        question_lower = question.lower()
        answer_lower = answer.lower()
        
        # 1. Palavras-chave da pergunta na resposta (0-0.4)
        question_words = set([w for w in question_lower.split() if len(w) > 3])
        answer_words = set(answer_lower.split())
        common_words = question_words.intersection(answer_words)
        
        overlap_ratio = len(common_words) / max(len(question_words), 1)
        score += min(0.4, overlap_ratio * 0.8)
        
        # 2. Não é uma recusa genérica (0-0.3)
        rejection_phrases = ["não foi possível", "não consegui", "desculpe", "não tenho informações"]
        if not any(phrase in answer_lower for phrase in rejection_phrases):
            score += 0.3
        elif "mas" in answer_lower:  # Recusa parcial
            score += 0.15
        
        # 3. Resposta estruturada e completa (0-0.3)
        if len(answer.split()) >= 10:
            score += 0.2
            # Bonus para respostas bem estruturadas
            if any(marker in answer for marker in ["•", "-", "1.", "2.", ":"]):
                score += 0.1
        elif len(answer.split()) >= 5:
            score += 0.1
        
        return min(1.0, score)

    def calculate_context_precision(self, context_chunks, expected_topics: List[str]) -> float:
        """
        Calcula precisão do contexto recuperado (simula RAGAS)
        Proporção de chunks relevantes entre os recuperados
        """
        if not context_chunks:
            return 0.0
        
        if not expected_topics:
            return 0.5 
        
        relevant_chunks = 0
        
        for chunk in context_chunks:
            chunk_text = chunk.page_content.lower()
            # Chunk é relevante se contém pelo menos um tópico esperado
            if any(topic.lower() in chunk_text for topic in expected_topics):
                relevant_chunks += 1
        
        return relevant_chunks / len(context_chunks)

    def calculate_context_recall(self, context_chunks, expected_topics: List[str]) -> float:
        """
        Calcula recall do contexto recuperado (simula RAGAS)
        Proporção de tópicos esperados cobertos pelo contexto
        """
        if not expected_topics:
            return 1.0 
        
        if not context_chunks:
            return 0.0
        
        covered_topics = 0
        context_text = " ".join([chunk.page_content.lower() for chunk in context_chunks])
        
        for topic in expected_topics:
            if topic.lower() in context_text:
                covered_topics += 1
        
        return covered_topics / len(expected_topics)