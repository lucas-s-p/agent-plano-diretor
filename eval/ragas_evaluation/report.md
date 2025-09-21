# Relatório de Avaliação - Sistema RAG Educacional
## Plano Diretor de Campina Grande

**Data da Avaliação:** 21/09/2025 01:05  
**Método:** Métricas RAGAS com Gemini

---

## Resumo Executivo

### Performance Geral
- **Total de perguntas testadas:** 3
- **Respostas bem-sucedidas:** 3/3 (100.0%)
- **Latência média:** 2.654s
- **Uso médio de memória:** 36.77MB  
- **Chunks recuperados por pergunta:** 2.7

### Métricas de Qualidade (escala 0.0 - 1.0)
- **Faithfulness (Fidelidade):** 0.816
- **Answer Relevancy (Relevância):** 0.433
- **Context Precision (Precisão do Contexto):** 0.778
- **Context Recall (Recall do Contexto):** 0.333

---

## Interpretação das Métricas

### Benchmarks de Qualidade
- **Faithfulness > 0.7:** Respostas bem fundamentadas nos documentos
- **Answer Relevancy > 0.7:** Respostas pertinentes às perguntas  
- **Context Precision > 0.6:** Boa qualidade de recuperação
- **Context Recall > 0.6:** Cobertura adequada dos tópicos

### Avaliação dos Resultados
- **Faithfulness (0.816):** Excelente
- **Answer Relevancy (0.433):** Baixo
- **Context Precision (0.778):** Bom
- **Context Recall (0.333):** Baixo

---

## Análise Detalhada

### Por Dificuldade da Pergunta

**Easy** (3 perguntas):
- Fidelidade: 0.816
- Relevância: 0.433

### Por Tipo de Pergunta

**Factual** (3 perguntas):
- Fidelidade: 0.816  
- Relevância: 0.433

---

## Metodologia da Avaliação

### Métricas RAGAS

Esta avaliação utiliza o framework RAGAS oficial para calcular métricas de qualidade RAG:

**1. Faithfulness (Fidelidade)**
- Avaliada por LLM: verifica se a resposta é suportada pelo contexto recuperado
- Detecta alucinações e informações não fundamentadas

**2. Answer Relevancy (Relevância)**
- Avaliada por LLM: mede quão bem a resposta atende à pergunta
- Considera completude e pertinência da resposta

**3. Context Precision (Precisão)**
- Proporção de contextos recuperados que são relevantes para a pergunta
- Avalia qualidade da recuperação de documentos

**4. Context Recall (Recall)**  
- Proporção de informações relevantes no ground truth cobertas pelo contexto
- Avalia completude da recuperação

### Implementação

**Modelo Principal: Gemini 2.5 Flash (Google)**

**Embeddings:** HuggingFace sentence-transformers/all-MiniLM-L6-v2

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

## Conclusões

### Avaliação Geral
O sistema RAG educacional apresenta desempenho **inadequado** com pontuação média de **0.590**.

### Recomendação
Revisão completa do sistema é necessária.

### Pontos Fortes
- Taxa de sucesso de 100.0% nas consultas
- Latência média baixa (2.654s)
- Recuperação eficiente de contexto (2.7 chunks/pergunta)

### Áreas de Melhoria
- Monitoramento contínuo das métricas RAGAS
- Expansão do conjunto de perguntas teste
- Fine-tuning para domínio específico se necessário

---
### Arquivos Gerados
- `eval/report.md` - Este relatório
- `eval/results/ragas_evaluation_results.json` - Dados completos da avaliação
