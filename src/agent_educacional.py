import os
import sys
import re
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Adicionar diretório pai para importar ingest
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ingest.vector_store import VectorStore
from agents.retriever import RetrieverAgent
from agents.answerer import AnswererAgent
from agents.self_check import SelfCheckAgent
from agents.safety import SafetyAgent
from agents.supervisor import SupervisorAgent
from GroqLLM import GroqLLM


class AgentEducacional:
    def __init__(
        self, 
        vectorstore_path: str,
        model: str = "openai/gpt-oss-120b",
        retrieval_k: int = 3,
        similarity_threshold: float = 0.35,
        verbose: bool = True
    ):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = model
        self.retrieval_k = retrieval_k
        self.similarity_threshold = similarity_threshold
        self.verbose = verbose
             
        if not self.api_key:
            raise ValueError("API key não encontrada no .env")
        
        self._initialize_components(vectorstore_path)

    def _initialize_components(self, vectorstore_path: str) -> None:   
        self.vectorstore = self._load_vectorstore(vectorstore_path)
        self.llm = GroqLLM(self.api_key, self.model)
        
        self.retriever = RetrieverAgent(self.vectorstore, k=self.retrieval_k)
        self.answerer = AnswererAgent(self.llm)
        self.self_check = SelfCheckAgent(similarity_threshold=self.similarity_threshold)
        self.safety = SafetyAgent()
        
        self.supervisor = SupervisorAgent(
            self.retriever, 
            self.answerer,
            self.self_check, 
            self.safety
        )

    def _load_vectorstore(self, vectorstore_path: str):
        if not os.path.exists(vectorstore_path):
            raise FileNotFoundError(f"Vectorstore não encontrado em: {vectorstore_path}")
        
        required_files = ["index.faiss", "index.pkl", "literal_index.pkl", "chunks.pkl"]
        missing_files = [f for f in required_files if not os.path.exists(os.path.join(vectorstore_path, f))]
        
        if missing_files:
            raise FileNotFoundError(f"Arquivos faltando: {missing_files}. Execute: python ingest/ingest.py ingest/docs")
        
        store = VectorStore(vectorstore_path)
        store.load()
        
        return store

    def ask(self, query: str) -> str:
        if not query or not query.strip():
            return "Por favor, faça uma pergunta válida."
        
        query = query.strip()
        
        return self.supervisor.handle_query(query)

    def get_system_info(self) -> dict:
        return {
            "retriever_type": "combined_search",
            "model": self.model,
            "retrieval_k": self.retrieval_k,
            "similarity_threshold": self.similarity_threshold,
            "total_chunks": len(self.vectorstore.chunks),
            "indexed_articles": len(self.vectorstore.literal_index),
            "available_articles": sorted(self.vectorstore.literal_index.keys(), key=int)[:20]
        }

    def test_article_search(self, article_number: str) -> dict:
        query = f"Art. {article_number}"
        
        try:
            results = self.vectorstore.search(query, k=5)
            
            test_result = {
                "query": query,
                "article_number": article_number,
                "found_chunks": len(results),
                "chunks": []
            }
            
            for doc, score in results:
                contains_target = bool(re.search(rf'\bArt\.?\s*{article_number}\b', doc.page_content, re.IGNORECASE))
                
                chunk_info = {
                    "score": round(score, 4),
                    "contains_target_article": contains_target,
                    "preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": {
                        "article_number": doc.metadata.get("article_number"),
                        "chunk_type": doc.metadata.get("chunk_type"),
                        "source": doc.metadata.get("source")
                    }
                }
                test_result["chunks"].append(chunk_info)
            
            direct_matches = sum(1 for c in test_result["chunks"] if c["contains_target_article"])
            test_result["summary"] = {
                "direct_matches": direct_matches,
                "success": direct_matches > 0,
                "quality": "excelente" if direct_matches >= 2 else "boa" if direct_matches == 1 else "ruim"
            }
            
            return test_result
            
        except Exception as e:
            return {"error": f"Erro no teste: {str(e)}"}

    def batch_test_articles(self, article_numbers: list) -> dict:
        results = {
            "articles_tested": len(article_numbers),
            "successful": 0,
            "failed": 0,
            "details": {}
        }
        
        for article_num in article_numbers:
            test_result = self.test_article_search(str(article_num))
            
            if "error" in test_result:
                results["failed"] += 1
                results["details"][article_num] = {"status": "error", "message": test_result["error"]}
            else:
                success = test_result["summary"]["success"]
                if success:
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                
                results["details"][article_num] = {
                    "status": "success" if success else "failed",
                    "direct_matches": test_result["summary"]["direct_matches"],
                    "total_chunks": test_result["found_chunks"],
                    "quality": test_result["summary"]["quality"]
                }
        
        results["success_rate"] = f"{results['successful']}/{len(article_numbers)} ({results['successful']/len(article_numbers)*100:.1f}%)"
        
        return results

    def set_verbose(self, verbose: bool):
        self.verbose = verbose