import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_dir = os.path.join(project_root, 'src')

sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)

from agent_educacional import AgentEducacional
from ragas_evaluator import RAGASEvaluator

def find_vectorstore():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    possible_paths = [
        os.path.join(project_root, "vectorstore"),
        os.path.join(project_root, "data", "vectorstore"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    print("Erro: vectorstore não encontrado")
    return None

def main():
    print("=" * 70)
    print("AVALIAÇÃO RAGAS - PLANO DIRETOR CAMPINA GRANDE")
    print("=" * 70)
    
    vectorstore_path = find_vectorstore()
    if not vectorstore_path:
        return
    
    try:
        agent = AgentEducacional(vectorstore_path)
        evaluator = RAGASEvaluator(agent)
        results = evaluator.run_evaluation()
        
        print("Avaliação concluída")
        print(f"Relatório: eval/ragas_evaluation/report.md")
        print(f"Dados: eval/results/ragas_evaluation_results.json")
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()