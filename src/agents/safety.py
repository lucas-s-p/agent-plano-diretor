from typing import Any, Dict, List


class SafetyAgent:
    def __init__(self):
        self.disclaimer = "⚠️ Esta resposta é apenas informativa e educacional, consulte sempre os materiais oficiais."

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        answer = state["final_answer"]
        citations = state.get("citations", [])
        
        final_answer = self._format_final_answer(answer, citations)
        
        log = f"[Safety] Formatação aplicada: {len(citations)} citações, disclaimer de educação"
        
        return {
            "final_answer": final_answer,
            "safety_applied": True,
            "agent_logs": state.get("agent_logs", []) + [log],
            "next_agent": "end"
        }
    
    def _format_final_answer(self, answer: str, citations: List[str]) -> str:
        formatted_answer = answer.strip()
        
        if citations and "📚 Fontes:" not in formatted_answer:
            formatted_answer += f"\n\n📚 Fontes:\n" + "\n".join(citations)
        
        formatted_answer += f"\n\n{self.disclaimer}"
        
        return formatted_answer