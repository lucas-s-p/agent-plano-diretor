import time
import psutil
from typing import List, Dict, Any

from test_cases import TEST_CASES
from metrics import RAGMetrics
from report_generator import ReportGenerator


class ManualRAGEvaluator:
    """Avaliador manual do sistema RAG"""
    
    def __init__(self, agent):
        self.agent = agent
        self.test_cases = TEST_CASES
        self.metrics_calculator = RAGMetrics()
        self.report_generator = ReportGenerator()

    def run_evaluation(self) -> Dict[str, Any]:
        """Executa avaliação completa do sistema RAG"""
        print("Iniciando avaliação manual do sistema RAG...")
        
        results = []
        performance_metrics = []
        
        for i, test_case in enumerate(self.test_cases):
            print(f"Processando {i+1}/{len(self.test_cases)}: {test_case.question}")
            
            # Executar pergunta e medir performance
            result = self._evaluate_single_question(test_case)
            results.append(result)
            
            if "error" not in result:
                performance_metrics.append({
                    "question": test_case.question,
                    "latency": result["latency"],
                    "memory_usage": result.get("memory_usage", 0),
                    "context_retrieved": result["context_chunks_count"],
                    "difficulty": test_case.difficulty,
                    "type": test_case.question_type
                })
        
        # Compilar e salvar resultados
        compiled_results = self._compile_results(performance_metrics, results)
        self.report_generator.save_results(compiled_results)
        
        return compiled_results

    def _evaluate_single_question(self, test_case) -> Dict[str, Any]:
        """Avalia uma única pergunta"""
        start_time = time.time()
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024
        
        try:
            # Obter resposta do sistema
            answer = self.agent.ask(test_case.question)
            
            # Obter contexto recuperado
            initial_state = {
                "query": test_case.question,
                "retrieved_chunks": [],
                "agent_logs": []
            }
            
            retriever_result = self.agent.retriever(initial_state)
            context_chunks = retriever_result.get("retrieved_chunks", [])
            
            # Métricas de performance
            end_time = time.time()
            mem_after = process.memory_info().rss / 1024 / 1024
            
            # Calcular métricas de qualidade
            metrics = self.metrics_calculator.calculate_all_metrics(
                answer, test_case.question, context_chunks, test_case.expected_topics
            )
            
            return {
                "question": test_case.question,
                "answer": answer,
                "expected_topics": test_case.expected_topics,
                "difficulty": test_case.difficulty,
                "question_type": test_case.question_type,
                "context_chunks_count": len(context_chunks),
                "latency": round(end_time - start_time, 3),
                "memory_usage": mem_after - mem_before,
                "metrics": metrics
            }
            
        except Exception as e:
            print(f"  Erro: {str(e)}")
            return {
                "question": test_case.question,
                "error": str(e),
                "difficulty": test_case.difficulty,
                "question_type": test_case.question_type,
                "metrics": {
                    "faithfulness": 0.0,
                    "answer_relevancy": 0.0,
                    "context_precision": 0.0,
                    "context_recall": 0.0
                }
            }

    def _compile_results(self, performance_metrics: List[Dict], detailed_results: List[Dict]) -> Dict[str, Any]:
        """Compila todos os resultados da avaliação"""
        successful_results = [r for r in detailed_results if "error" not in r]
        
        # Métricas de performance
        avg_latency = sum(m["latency"] for m in performance_metrics) / len(performance_metrics) if performance_metrics else 0
        avg_memory = sum(m["memory_usage"] for m in performance_metrics) / len(performance_metrics) if performance_metrics else 0
        avg_chunks = sum(m["context_retrieved"] for m in performance_metrics) / len(performance_metrics) if performance_metrics else 0
        
        # Métricas de qualidade
        if successful_results:
            avg_faithfulness = sum(r["metrics"]["faithfulness"] for r in successful_results) / len(successful_results)
            avg_relevancy = sum(r["metrics"]["answer_relevancy"] for r in successful_results) / len(successful_results)
            avg_precision = sum(r["metrics"]["context_precision"] for r in successful_results) / len(successful_results)
            avg_recall = sum(r["metrics"]["context_recall"] for r in successful_results) / len(successful_results)
        else:
            avg_faithfulness = avg_relevancy = avg_precision = avg_recall = 0.0
        
        # Análise por dificuldade
        difficulty_analysis = {}
        for difficulty in ["easy", "medium", "hard"]:
            difficulty_results = [r for r in successful_results if r["difficulty"] == difficulty]
            if difficulty_results:
                difficulty_analysis[difficulty] = {
                    "count": len(difficulty_results),
                    "avg_faithfulness": round(sum(r["metrics"]["faithfulness"] for r in difficulty_results) / len(difficulty_results), 3),
                    "avg_relevancy": round(sum(r["metrics"]["answer_relevancy"] for r in difficulty_results) / len(difficulty_results), 3)
                }
        
        # Análise por tipo
        type_analysis = {}
        for qtype in ["factual", "procedural", "conceptual"]:
            type_results = [r for r in successful_results if r["question_type"] == qtype]
            if type_results:
                type_analysis[qtype] = {
                    "count": len(type_results),
                    "avg_faithfulness": round(sum(r["metrics"]["faithfulness"] for r in type_results) / len(type_results), 3),
                    "avg_relevancy": round(sum(r["metrics"]["answer_relevancy"] for r in type_results) / len(type_results), 3)
                }
        
        return {
            "evaluation_summary": {
                "total_questions": len(self.test_cases),
                "successful_answers": len(successful_results),
                "success_rate": len(successful_results) / len(self.test_cases),
                "avg_latency_seconds": round(avg_latency, 3),
                "avg_memory_usage_mb": round(avg_memory, 2),
                "avg_chunks_retrieved": round(avg_chunks, 1),
                "evaluation_method": "Manual (RAGAS-style metrics)"
            },
            "manual_ragas_metrics": {
                "faithfulness": round(avg_faithfulness, 3),
                "answer_relevancy": round(avg_relevancy, 3),
                "context_precision": round(avg_precision, 3),
                "context_recall": round(avg_recall, 3)
            },
            "performance_by_difficulty": difficulty_analysis,
            "performance_by_type": type_analysis,
            "detailed_results": detailed_results
        }