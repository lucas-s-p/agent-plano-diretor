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
    ),
     TestCase(
        question="Olá, como você pode me ajudar?",
        expected_topics=["saudação", "ajuda", "assistente"],
        difficulty="easy",
        question_type="procedural"
    ),
    TestCase(
        question="O que estabelece o Art. 90 sobre loteamentos?",
        expected_topics=["loteamentos", "acesso controlado", "condomínio"],
        difficulty="easy",
        question_type="factual"
    ),
    TestCase(
        question="Qual a área máxima para condomínios segundo o Art. 95?",
        expected_topics=["área máxima", "50 hectares", "condomínios"],
        difficulty="easy",
        question_type="factual"
    ),
    TestCase(
        question="O que diz o Art. 241 sobre educação?",
        expected_topics=["política educacional", "responsabilidades", "cidadania"],
        difficulty="easy",
        question_type="factual"
    ),
    TestCase(
        question="Quais os objetivos da Política de Saúde no Art. 245?",
        expected_topics=["acesso universal", "prevenção", "atenção primária"],
        difficulty="easy",
        question_type="factual"
    ),
    TestCase(
        question="O que estabelece o Art. 247 sobre assistência social?",
        expected_topics=["proteção social", "vulnerabilidade", "risco social"],
        difficulty="easy",
        question_type="factual"
    ),
    TestCase(
        question="O que são níveis de incômodos segundo o Art. 99?",
        expected_topics=["incomodidade", "uso", "vizinhança"],
        difficulty="easy",
        question_type="factual"
    ),
    
    # MEDIUM - Perguntas sobre procedimentos e diretrizes (12 perguntas)
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
    TestCase(
        question="Quais os requisitos para aprovação de loteamentos segundo o Art. 91?",
        expected_topics=["área construída", "drenagem", "águas pluviais"],
        difficulty="medium",
        question_type="procedural"
    ),
    TestCase(
        question="Como funciona a doação de áreas institucionais no Art. 93?",
        expected_topics=["áreas institucionais", "espaços livres", "acesso público"],
        difficulty="medium",
        question_type="procedural"
    ),
    TestCase(
        question="Quais os fatores considerados para análise de incomodidade no Art. 101?",
        expected_topics=["impacto urbanístico", "poluição sonora", "poluição atmosférica"],
        difficulty="medium",
        question_type="factual"
    ),
    TestCase(
        question="Como são classificados os níveis de incomodidade no Art. 102?",
        expected_topics=["não incômodos", "incômodos nível I", "incômodos nível II"],
        difficulty="medium",
        question_type="factual"
    ),
    TestCase(
        question="Quais as diretrizes da Política de Educação no Art. 243?",
        expected_topics=["cooperação", "consciência ambiental", "ODSs"],
        difficulty="medium",
        question_type="procedural"
    ),
    TestCase(
        question="Como a Política de Saúde aborda a saúde animal no Art. 246?",
        expected_topics=["saúde animal", "controle de zoonoses", "vigilância sanitária"],
        difficulty="medium",
        question_type="procedural"
    ),
    
    # HARD - Perguntas conceituais e de integração (6 perguntas)
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
    ),
    TestCase(
        question="Qual a relação entre políticas setoriais de educação, saúde e assistência social na promoção do desenvolvimento urbano sustentável?",
        expected_topics=["políticas integradas", "desenvolvimento sustentável", "intersetorialidade"],
        difficulty="hard",
        question_type="conceptual"
    )
]