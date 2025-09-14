import os
import sys
import time

# Adicionar paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

try:
    from src.agent_educacional import AgentEducacional
except ImportError:
    try:
        from agent_educacional import AgentEducacional
    except ImportError:
        sys.path.append('../src')
        from agent_educacional import AgentEducacional

from evaluator import ManualRAGEvaluator

def find_vectorstore():
    """Encontra o vectorstore nos caminhos possíveis"""
    possible_paths = ["vectorstore", "../vectorstore"]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Vectorstore encontrado em: {path}")
            return path
    
    print("Erro: vectorstore não encontrado")
    print("Execute primeiro: python ingest/ingest.py ingest/docs")
    return None

def main():
    """Script principal de avaliação"""
    print("=" * 60)
    print("AVALIAÇÃO DO SISTEMA RAG - PLANO DIRETOR CAMPINA GRANDE")
    print("=" * 60)
    
    # Encontrar vectorstore
    vectorstore_path = find_vectorstore()
    if not vectorstore_path:
        return
    
    # Carregar sistema
    print("\nCarregando sistema RAG...")
    try:
        agent = AgentEducacional(vectorstore_path)
        print(f"✓ Sistema carregado com {len(agent.vectorstore.chunks)} chunks")
    except Exception as e:
        print(f"✗ Erro ao carregar sistema: {e}")
        return
    
    # Executar avaliação
    print("\nIniciando avaliação...")
    evaluator = ManualRAGEvaluator(agent)
    
    start_time = time.time()
    results = evaluator.run_evaluation()
    total_time = time.time() - start_time
    
    # Mostrar resumo
    print("\n" + "=" * 60)
    print("RESULTADOS DA AVALIAÇÃO")
    print("=" * 60)
    
    summary = results['evaluation_summary']
    metrics = results['manual_ragas_metrics']
    
    print(f"Taxa de sucesso: {summary['success_rate']:.1%}")
    print(f"Latência média: {summary['avg_latency_seconds']:.3f}s")
    print(f"Tempo total: {total_time:.1f}s")
    print()
    print("Métricas de Qualidade:")
    print(f"  Faithfulness: {metrics['faithfulness']:.3f}")
    print(f"  Answer Relevancy: {metrics['answer_relevancy']:.3f}")
    print(f"  Context Precision: {metrics['context_precision']:.3f}")
    print(f"  Context Recall: {metrics['context_recall']:.3f}")
    
    print(f"\n✓ Relatório principal: eval/report.md")
    print(f"✓ Resultados detalhados: eval/results/manual_evaluation_results.json")

if __name__ == "__main__":
    main()