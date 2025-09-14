from typing import Dict, TypedDict, List
from langchain_core.documents import Document

class RAGState(TypedDict, total=False):
    query: str
    enhanced_query: str  
    user_profile: Dict[str, str]  
    conversation_history: List[Dict]  
    awaiting_user_input: bool  
    retrieved_chunks: List[Document]
    raw_answer: str
    final_answer: str
    citations: List[str]
    self_check_passed: bool
    safety_applied: bool
    agent_logs: List[str]
    next_agent: str