from typing import Dict, Any, List, Tuple
from langchain_core.documents import Document

class AnswererAgent:
    def __init__(self, llm):
        self.llm = llm

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state["query"]
        chunks = state["retrieved_chunks"]
        
        if not chunks:
            return self._handle_no_chunks(state)
        
        context, citations = self._build_context_with_citations(chunks)
        raw_answer = self._generate_answer(query, context)
        
        log = f"[Answerer] Resposta gerada com {len(citations)} fontes disponíveis"
        
        return {
            "raw_answer": raw_answer,
            "citations": citations,
            "agent_logs": state.get("agent_logs", []) + [log],
            "next_agent": "self_check"
        }
    
    def _build_context_with_citations(self, chunks: List[Document]) -> Tuple[str, List[str]]:
        context_parts = []
        citations = []
        source_to_citation = {}  # Mapeia fonte para número da citação
        citation_counter = 1
        
        for i, doc in enumerate(chunks, 1):
            source = self._extract_source(doc.metadata, i)
            
            # Se ainda não viu essa fonte, cria nova citação
            if source not in source_to_citation:
                source_to_citation[source] = citation_counter
                
                # Adiciona informação de página se disponível
                page_info = ""
                if 'page' in doc.metadata:
                    page_info = f", p. {doc.metadata['page']}"
                
                citations.append(f"[{citation_counter}] {source}{page_info}")
                citation_counter += 1
            
            # Usa o número da citação já existente para essa fonte
            citation_num = source_to_citation[source]
            context_parts.append(f"[FONTE_{citation_num}] {doc.page_content}")
        
        return "\n\n".join(context_parts), citations
    
    def _extract_source(self, metadata: dict, index: int) -> str:
        source = metadata.get("source", f"Documento_{index}")
        
        if "/" in source:
            source = source.split("/")[-1]
        
        return source
    
    def _generate_answer(self, query: str, context: str) -> str:
        prompt = f"""
        Contexto com fontes numeradas:
        {context}

        Pergunta: {query}

        Instruções:
        - Responda exclusivamente baseado no contexto fornecido
        - Use citações [1], [2], [3] para cada afirmação importante
        - Se o contexto não contém informação suficiente, seja claro sobre isso
        - Mantenha a resposta objetiva e precisa
        - Se a mensagem for uma saudação ou pergunta geral, pode ser respondida sem citações

        ESTRUTURA OBRIGATÓRIA DA RESPOSTA:
        1. Desenvolva a resposta técnica completa com citações
        2. OBRIGATORIAMENTE finalize com EXATAMENTE as palavras "Em resumo:" (não use "Em síntese", "Para resumir", ou qualquer outra variação)
        3. Após "Em resumo:":
        - Explique o conceito em linguagem simples e acessível
        - Use termos do dia a dia que qualquer cidadão entenda
        - Destaque os pontos mais importantes de forma clara
        - Seja prático: como isso afeta a vida das pessoas

        Importante: Use apenas "Em resumo:" no final, nunca outras expressões similares.

        Resposta com citações:
        """

        return self.llm.generate(prompt)
    
    def _handle_no_chunks(self, state: Dict[str, Any]) -> Dict[str, Any]:
        log = "[Answerer] Nenhum chunk recuperado - impossível gerar resposta"
        
        return {
            "raw_answer": "Nenhum documento relevante encontrado para responder esta pergunta.",
            "citations": [],
            "agent_logs": state.get("agent_logs", []) + [log],
            "next_agent": "end"
        }