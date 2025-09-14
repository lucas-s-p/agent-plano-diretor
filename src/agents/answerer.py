from typing import Dict, Any, List
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
    
    def _build_context_with_citations(self, chunks: List[Document]) -> tuple[str, List[str]]:
        context_parts = []
        citations = []
        
        for i, doc in enumerate(chunks, 1):
            source = self._extract_source(doc.metadata, i)
            context_parts.append(f"[FONTE_{i}] {doc.page_content}")
            citations.append(f"[{i}] {source}")
        
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
        - Se a mensagem estiver relacionada a uma saudação pode ser respondida

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
