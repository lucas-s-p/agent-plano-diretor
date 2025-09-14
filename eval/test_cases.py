from dataclasses import dataclass
from typing import List

@dataclass
class TestCase:
    question: str
    expected_topics: List[str]
    difficulty: str  
    question_type: str 

# Conjunto de 15 perguntas teste
TEST_CASES = [
    # EASY - Perguntas diretas sobre artigos específicos
    TestCase(
        question="O que diz o Art. 175 sobre cidades inteligentes?",
        expected_topics=["cidade inteligente", "tecnologia", "inovação"],
        difficulty="easy",
        question_type="factual"
    ),
    TestCase(
        question="O que são Zonas Especiais de Interesse Social (ZEIS)?",
        expected_topics=["ZEIS", "habitação", "interesse social"],
        difficulty="easy",
        question_type="factual"
    ),
    TestCase(
        question="Art. 180",
        expected_topics=["artigo", "legislação"],
        difficulty="easy",
        question_type="factual"
    ),
    TestCase(
        question="Olá, como você pode me ajudar?",
        expected_topics=["saudação", "ajuda", "assistente"],
        difficulty="easy",
        question_type="procedural"
    ),
    
    # MEDIUM - Perguntas sobre procedimentos e diretrizes
    TestCase(
        question="Quais são as diretrizes para participação social mencionadas no Art. 178?",
        expected_topics=["participação social", "controle social", "transparência"],
        difficulty="medium",
        question_type="procedural"
    ),
    TestCase(
        question="Quais são os instrumentos de política urbana previstos?",
        expected_topics=["instrumentos", "política urbana", "gestão"],
        difficulty="medium",
        question_type="procedural"
    ),
    TestCase(
        question="Quais são as competências do Conselho da Cidade?",
        expected_topics=["conselho", "competências", "participação"],
        difficulty="medium",
        question_type="factual"
    ),
    TestCase(
        question="Quais são as diretrizes para áreas verdes urbanas?",
        expected_topics=["áreas verdes", "meio ambiente", "qualidade de vida"],
        difficulty="medium",
        question_type="procedural"
    ),
    TestCase(
        question="O que estabelece o plano sobre densidade populacional?",
        expected_topics=["densidade", "população", "ocupação"],
        difficulty="medium",
        question_type="factual"
    ),
    TestCase(
        question="Quais são as penalidades por descumprimento das normas urbanísticas?",
        expected_topics=["penalidades", "normas", "fiscalização"],
        difficulty="medium",
        question_type="procedural"
    ),
    
    # HARD - Perguntas conceituais e de integração
    TestCase(
        question="Como o plano diretor integra sustentabilidade e desenvolvimento urbano?",
        expected_topics=["sustentabilidade", "desenvolvimento urbano", "meio ambiente"],
        difficulty="hard",
        question_type="conceptual"
    ),
    TestCase(
        question="Como funciona o licenciamento ambiental no contexto urbano?",
        expected_topics=["licenciamento", "meio ambiente", "urbano"],
        difficulty="hard",
        question_type="procedural"
    ),
    TestCase(
        question="Como o transporte público se integra ao planejamento urbano?",
        expected_topics=["transporte", "mobilidade", "planejamento"],
        difficulty="hard",
        question_type="conceptual"
    ),
    TestCase(
        question="Como são definidos os corredores de desenvolvimento?",
        expected_topics=["corredores", "desenvolvimento", "estruturação"],
        difficulty="hard",
        question_type="conceptual"
    ),
    TestCase(
        question="Como o plano diretor aborda a questão da gentrificação?",
        expected_topics=["gentrificação", "habitação", "direito à cidade"],
        difficulty="hard",
        question_type="conceptual"
    )
]