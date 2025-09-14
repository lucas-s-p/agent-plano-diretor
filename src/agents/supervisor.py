from typing import Dict, Any
from langgraph.graph import StateGraph, END
from state import RAGState

class SupervisorAgent:
    def __init__(self, retriever, answerer, self_check, safety):
        self.retriever = retriever
        self.answerer = answerer
        self.self_check = self_check
        self.safety = safety
        self.workflow = self._create_workflow()

    def handle_query(self, query: str) -> str:
        initial_state = {
            "query": query,
            "enhanced_query": query,
            "retrieved_chunks": [],
            "raw_answer": "",
            "final_answer": "",
            "citations": [],
            "self_check_passed": False,
            "safety_applied": False,
            "agent_logs": [],
            "next_agent": ""
        }
        
        result = self.workflow.invoke(initial_state)
        
        return result.get("final_answer", "Desculpe, não consegui processar sua solicitação.")

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state["query"]
        log = f"[Supervisor] Processando query: '{query[:50]}...'"
        
        return {
            "agent_logs": state.get("agent_logs", []) + [log],
            "next_agent": "retriever"
        }
    
    def _create_workflow(self) -> StateGraph:
        workflow = StateGraph(RAGState)
        
        workflow.add_node("supervisor", self)
        workflow.add_node("retriever", self.retriever)
        workflow.add_node("answerer", self.answerer)
        workflow.add_node("self_check", self.self_check)
        workflow.add_node("safety", self.safety)
        
        workflow.set_entry_point("supervisor")
        
        def supervisor_router(state):
            return "retriever"
        
        def retriever_router(state):
            chunks = state.get("retrieved_chunks", [])
            return "answerer" if chunks else "end"
        
        def answerer_router(state):
            raw_answer = state.get("raw_answer", "")
            return "self_check" if raw_answer else "end"
        
        def self_check_router(state):
            passed = state.get("self_check_passed", False)
            return "safety" if passed else "end"
        
        workflow.add_conditional_edges(
            "supervisor",
            supervisor_router,
            {"retriever": "retriever"}
        )
        
        workflow.add_conditional_edges(
            "retriever",
            retriever_router,
            {"answerer": "answerer", "end": END}
        )
        
        workflow.add_conditional_edges(
            "answerer",
            answerer_router,
            {"self_check": "self_check", "end": END}
        )
        
        workflow.add_conditional_edges(
            "self_check",
            self_check_router,
            {"safety": "safety", "end": END}
        )
        
        workflow.add_edge("safety", END)
        
        return workflow.compile()