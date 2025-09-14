import os
import json
import time
from typing import Dict, Any


class ReportGenerator:
    """Gerador de relatórios de avaliação"""

    def save_results(self, results: Dict[str, Any]):
        """Salva resultados completos da avaliação"""
        os.makedirs("eval/results", exist_ok=True)
        
        # Salvar JSON detalhado
        with open("eval/results/manual_evaluation_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Gerar relatório principal
        self._generate_main_report(results)

    def _generate_main_report(self, results: Dict[str, Any]):
        """Gera relatório principal em eval/report.md"""
        summary = results["evaluation_summary"]
        metrics = results["manual_ragas_metrics"]
        
        report = self._build_header()
        report += self._build_executive_summary(summary, metrics)
        report += self._build_metrics_interpretation(metrics)
        report += self._build_detailed_analysis(results)
        report += self._build_methodology()
        report += self._build_conclusions(summary, metrics)
        report += self._build_footer()
        
        with open("eval/report.md", "w", encoding="utf-8") as f:
            f.write(report)

    def _build_header(self) -> str:
        """Cabeçalho do relatório"""
        return f"""# Relatório de Avaliação - Sistema RAG Educacional
## Plano Diretor de Campina Grande

**Data da Avaliação:** {time.strftime("%d/%m/%Y %H:%M")}  
**Método:** Implementação manual de métricas estilo RAGAS/Giskard

---

"""

    def _build_executive_summary(self, summary: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Resumo executivo"""
        return f"""## Resumo Executivo

### Performance Geral
- **Total de perguntas testadas:** {summary['total_questions']}
- **Respostas bem-sucedidas:** {summary['successful_answers']}/{summary['total_questions']} ({summary['success_rate']:.1%})
- **Latência média:** {summary['avg_latency_seconds']}s
- **Uso médio de memória:** {summary['avg_memory_usage_mb']}MB  
- **Chunks recuperados por pergunta:** {summary['avg_chunks_retrieved']}

### Métricas de Qualidade (escala 0.0 - 1.0)
- **Faithfulness (Fidelidade):** {metrics['faithfulness']:.3f}
- **Answer Relevancy (Relevância):** {metrics['answer_relevancy']:.3f}
- **Context Precision (Precisão do Contexto):** {metrics['context_precision']:.3f}
- **Context Recall (Recall do Contexto):** {metrics['context_recall']:.3f}

---

"""

    def _build_metrics_interpretation(self, metrics: Dict[str, Any]) -> str:
        """Interpretação das métricas"""
        def evaluate_metric(value, thresholds):
            if value >= thresholds[0]:
                return "Excelente"
            elif value >= thresholds[1]:
                return "Bom"
            elif value >= thresholds[2]:
                return "Regular"
            else:
                return "Baixo"

        faith_eval = evaluate_metric(metrics['faithfulness'], [0.8, 0.7, 0.5])
        rel_eval = evaluate_metric(metrics['answer_relevancy'], [0.8, 0.7, 0.5])
        prec_eval = evaluate_metric(metrics['context_precision'], [0.8, 0.6, 0.4])
        rec_eval = evaluate_metric(metrics['context_recall'], [0.8, 0.6, 0.4])

        return f"""## Interpretação das Métricas

### Benchmarks de Qualidade
- **Faithfulness > 0.7:** Respostas bem fundamentadas nos documentos
- **Answer Relevancy > 0.7:** Respostas pertinentes às perguntas  
- **Context Precision > 0.6:** Boa qualidade de recuperação
- **Context Recall > 0.6:** Cobertura adequada dos tópicos

### Avaliação dos Resultados
- **Faithfulness ({metrics['faithfulness']:.3f}):** {faith_eval}
- **Answer Relevancy ({metrics['answer_relevancy']:.3f}):** {rel_eval}
- **Context Precision ({metrics['context_precision']:.3f}):** {prec_eval}
- **Context Recall ({metrics['context_recall']:.3f}):** {rec_eval}

---

"""

    def _build_detailed_analysis(self, results: Dict[str, Any]) -> str:
        """Análise detalhada por dificuldade e tipo"""
        analysis = "## Análise Detalhada\n\n### Por Dificuldade da Pergunta\n"
        
        for difficulty, data in results.get("performance_by_difficulty", {}).items():
            analysis += f"""
**{difficulty.title()}** ({data['count']} perguntas):
- Fidelidade: {data['avg_faithfulness']:.3f}
- Relevância: {data['avg_relevancy']:.3f}
"""

        analysis += "\n### Por Tipo de Pergunta\n"
        
        for qtype, data in results.get("performance_by_type", {}).items():
            analysis += f"""
**{qtype.title()}** ({data['count']} perguntas):
- Fidelidade: {data['avg_faithfulness']:.3f}  
- Relevância: {data['avg_relevancy']:.3f}
"""

        analysis += "\n---\n\n"
        return analysis

    def _build_methodology(self) -> str:
        """Metodologia da avaliação"""
        return """## Metodologia da Avaliação

### Implementação Manual das Métricas

Esta avaliação implementa manualmente as principais métricas do RAGAS/Giskard:

**1. Faithfulness (Fidelidade)**
- Presença de citações e referências
- Sobreposição semântica com contexto recuperado  
- Ausência de especulação excessiva
- Conteúdo substantivo

**2. Answer Relevancy (Relevância)**
- Palavras-chave da pergunta na resposta
- Evita respostas genéricas de recusa
- Estrutura e completude da resposta

**3. Context Precision (Precisão)**
- Proporção de chunks recuperados relevantes aos tópicos esperados

**4. Context Recall (Recall)**  
- Cobertura dos tópicos esperados no contexto recuperado

### Critérios de Avaliação

#### Escala de Pontuação
Cada métrica é avaliada em uma escala de 0.0 a 1.0:

- **0.8-1.0:** Excelente desempenho
- **0.7-0.8:** Bom desempenho  
- **0.5-0.7:** Desempenho regular
- **0.0-0.5:** Baixo desempenho

#### Categorização das Perguntas

**Por Dificuldade:**
- **Easy:** Perguntas diretas sobre artigos específicos
- **Medium:** Perguntas que requerem interpretação
- **Hard:** Perguntas conceituais complexas

**Por Tipo:**
- **Factual:** Busca informações específicas
- **Procedural:** Como fazer algo
- **Conceptual:** Entendimento de conceitos

---

"""

    def _build_conclusions(self, summary: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """Conclusões e recomendações"""
        # Análise geral do desempenho
        overall_performance = (
            metrics['faithfulness'] + 
            metrics['answer_relevancy'] + 
            metrics['context_precision'] + 
            metrics['context_recall']
        ) / 4

        if overall_performance >= 0.8:
            performance_level = "excelente"
            recommendation = "O sistema está pronto para produção com monitoramento contínuo."
        elif overall_performance >= 0.7:
            performance_level = "bom"
            recommendation = "O sistema apresenta boa qualidade, recomenda-se ajustes pontuais."
        elif overall_performance >= 0.6:
            performance_level = "satisfatório"
            recommendation = "O sistema necessita melhorias antes do deployment."
        else:
            performance_level = "inadequado"
            recommendation = "Revisão completa do sistema é necessária."

        return f"""## Conclusões

### Avaliação Geral
O sistema RAG educacional apresenta desempenho **{performance_level}** com pontuação média de **{overall_performance:.3f}**.

### Pontos Fortes
- Taxa de sucesso de {summary['success_rate']:.1%} nas consultas
- Latência média baixa ({summary['avg_latency_seconds']}s)
- Recuperação eficiente de contexto ({summary['avg_chunks_retrieved']:.1f} chunks/pergunta)

### Áreas de Melhoria
"""

    def _build_footer(self) -> str:
        """Rodapé do relatório"""
        return f"""---
### Arquivos Gerados
- `eval/report.md` - Este relatório
- `eval/results/manual_evaluation_results.json` - Dados completos da avaliação
"""