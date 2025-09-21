import os
import sys
import time
from typing import List, Dict, Any
from datetime import datetime

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')

sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

from agent_educacional import AgentEducacional

from ragas import evaluate
from ragas.metrics import faithfulness, context_precision, context_recall, answer_relevancy

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from langchain_google_genai import GoogleGenerativeAI
from datasets import Dataset
import psutil
import pandas as pd
import numpy as np

from tests.test_cases import TEST_CASES
from report_generator import ReportGenerator


class RAGASModelManager:
    def __init__(self):
        self.llm = None
        self.embeddings = None
        self._setup_models()
    
    def _setup_models(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY necessária")
        
        self.llm = GoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1,
            max_retries=3,
            request_timeout=60
        )


class RAGASMetricsCalculator:
    def __init__(self, model_manager: RAGASModelManager):
        self.model_manager = model_manager
        self.metrics = self._setup_ragas_metrics()
    
    def _setup_ragas_metrics(self):
        import ragas
        ragas.llm = self.model_manager.llm
        ragas.embeddings = self.model_manager.embeddings
        
        return [faithfulness, context_precision, context_recall]
    
    def evaluate_with_ragas(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        eval_data = {
            "question": [r["question"] for r in responses],
            "answer": [r["answer"] for r in responses],
            "contexts": [r["contexts"] for r in responses],
            "ground_truth": [r["ground_truth"] for r in responses]
        }
        
        dataset = Dataset.from_dict(eval_data)
        
        result = evaluate(
            dataset, 
            metrics=self.metrics,
            llm=self.model_manager.llm,
            embeddings=self.model_manager.embeddings,
            raise_exceptions=True
        )
        
        scores_df = result.to_pandas()
        scores_dict = {}
        
        for column in scores_df.columns:
            col_data = scores_df[column]
            if col_data.dtype in ['float64', 'float32', 'int64', 'int32']:
                mean_val = col_data.mean()
                std_val = col_data.std()
                values = col_data.tolist()
                
                scores_dict[column] = {
                    'mean': float(mean_val) if not pd.isna(mean_val) else None,
                    'std': float(std_val) if not pd.isna(std_val) else None,
                    'values': values
                }
        
        relevancy_scores = []
        for q, a in zip(eval_data["question"], eval_data["answer"]):
            q_embedding = self.model_manager.embeddings.embed_query(q)
            a_embedding = self.model_manager.embeddings.embed_query(a)
            
            similarity = np.dot(q_embedding, a_embedding) / (
                np.linalg.norm(q_embedding) * np.linalg.norm(a_embedding)
            )
            relevancy_scores.append(float(similarity))
        
        scores_dict['answer_relevancy'] = {
            'mean': sum(relevancy_scores) / len(relevancy_scores) if relevancy_scores else None,
            'std': float(np.std(relevancy_scores)) if relevancy_scores else None,
            'values': relevancy_scores
        }
        
        return {
            "ragas_scores": scores_dict,
            "success": True,
            "error": None
        }


class RAGDataCollector:
    def __init__(self, agent: AgentEducacional):
        self.agent = agent
    
    def collect_rag_responses(self, test_cases: List[Any]) -> List[Dict[str, Any]]:
        responses = []
        
        for test_case in test_cases:
            start_time = time.time()
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024
            
            answer = self.agent.ask(test_case.question)
            latency = time.time() - start_time
            mem_after = process.memory_info().rss / 1024 / 1024
            
            search_results = self.agent.vectorstore.search(test_case.question, k=5)
            contexts = [doc.page_content for doc, score in search_results]
            
            ground_truth = " ".join(test_case.expected_topics)
            
            responses.append({
                "question": test_case.question,
                "answer": answer,
                "contexts": contexts,
                "ground_truth": ground_truth,
                "latency": latency,
                "memory_usage": mem_after - mem_before,
                "context_chunks_count": len(contexts),
                "difficulty": test_case.difficulty,
                "question_type": test_case.question_type,
                "expected_topics": test_case.expected_topics,
                "success": True
            })
        
        return responses


class RAGASEvaluator:
    def __init__(self, agent: AgentEducacional):
        self.agent = agent
        self.model_manager = RAGASModelManager()
        self.metrics_calculator = RAGASMetricsCalculator(self.model_manager)
        self.data_collector = RAGDataCollector(agent)
        self.report_generator = ReportGenerator()
        self.test_cases = TEST_CASES
    
    def run_evaluation(self) -> Dict[str, Any]:
        start_time = time.time()
        
        responses = self.data_collector.collect_rag_responses(self.test_cases)
        ragas_result = self.metrics_calculator.evaluate_with_ragas(responses)
        result = self._compile_results(responses, ragas_result, start_time)
        
        self.report_generator.save_results(result)
        
        return result
    
    def _calculate_metric_mean(self, ragas_scores: Dict[str, Any], metric_name: str, indices: List[int]) -> float:
        metric_data = ragas_scores.get(metric_name, {})
        values = metric_data.get("values", [])
        
        if not values or not indices:
            return 0.0
        
        selected_values = [values[i] for i in indices if i < len(values)]
        return sum(selected_values) / len(selected_values) if selected_values else 0.0
    
    def _compile_results(self, responses: List[Dict[str, Any]], ragas_result: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        successful_results = [r for r in responses if r["success"]]
        ragas_scores = ragas_result["ragas_scores"]
        
        metrics = {}
        for metric_name in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
            metric_data = ragas_scores.get(metric_name, {})
            mean_val = metric_data.get("mean")
            if mean_val is not None and pd.isna(mean_val):
                mean_val = None
            metrics[metric_name] = mean_val
        
        difficulty_analysis = {}
        for difficulty in ["easy", "medium", "hard"]:
            difficulty_results = [r for r in successful_results if r["difficulty"] == difficulty]
            if difficulty_results:
                difficulty_indices = [i for i, r in enumerate(successful_results) if r["difficulty"] == difficulty]
                
                difficulty_analysis[difficulty] = {
                    "count": len(difficulty_results),
                    "avg_faithfulness": self._calculate_metric_mean(ragas_scores, "faithfulness", difficulty_indices),
                    "avg_relevancy": self._calculate_metric_mean(ragas_scores, "answer_relevancy", difficulty_indices)
                }
        
        type_analysis = {}
        for qtype in ["factual", "procedural", "conceptual"]:
            type_results = [r for r in successful_results if r["question_type"] == qtype]
            if type_results:
                type_indices = [i for i, r in enumerate(successful_results) if r["question_type"] == qtype]
                
                type_analysis[qtype] = {
                    "count": len(type_results),
                    "avg_faithfulness": self._calculate_metric_mean(ragas_scores, "faithfulness", type_indices),
                    "avg_relevancy": self._calculate_metric_mean(ragas_scores, "answer_relevancy", type_indices)
                }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "evaluation_summary": {
                "total_questions": len(self.test_cases),
                "successful_answers": len(successful_results),
                "success_rate": len(successful_results) / len(self.test_cases),
                "avg_latency_seconds": round(sum(r["latency"] for r in responses) / len(responses), 3),
                "avg_memory_usage_mb": round(sum(r.get("memory_usage", 0) for r in responses) / len(responses), 2),
                "avg_chunks_retrieved": round(sum(r.get("context_chunks_count", 0) for r in responses) / len(responses), 1),
                "evaluation_method": "RAGAS oficial"
            },
            "ragas_metrics": metrics,
            "ragas_evaluation": ragas_result,
            "performance_by_difficulty": difficulty_analysis,
            "performance_by_type": type_analysis,
            "detailed_results": responses,
            "model_config": {
                "llm": "Gemini",
                "embeddings": "HuggingFace all-MiniLM-L6-v2"
            },
            "total_evaluation_time": time.time() - start_time
        }