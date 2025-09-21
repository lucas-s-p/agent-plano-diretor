from dataclasses import dataclass
from typing import List

@dataclass
class TestCase:
    question: str
    expected_topics: List[str]
    difficulty: str  
    question_type: str 

# Conjunto de 28 perguntas teste
TEST_CASES = [
    # EASY - Perguntas diretas sobre artigos específicos (10 perguntas)
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
    )
]