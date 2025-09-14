from agent_educacional import AgentEducacional
import sys
import traceback


class InteractiveRAGSystem:
    
    def __init__(self, vectorstore_path: str = "vectorstore"):
        self.vectorstore_path = vectorstore_path
        self.rag_system = None
        self.session_queries = []
        
    def initialize(self):
        
        print("Inicializando Sistema Educacional...")
        print(f"Vectorstore: {self.vectorstore_path}")
        
        try:
            self.rag_system = AgentEducacional(
                vectorstore_path=self.vectorstore_path,
                verbose=True
            )
            
            return True
            
        except FileNotFoundError as e:
            print(f"\nErro: {e}")
            print(f"\nSoluções:")
            print(f"   1. Certifique-se que o vectorstore existe: {self.vectorstore_path}")
            print(f"   2. Execute a ingestão: python ingest/ingest.py ingest/docs")
            print(f"   3. Verifique se os PDFs estão em ingest/docs/")
            return False
            
        except Exception as e:
            print(f"\nErro na inicialização: {e}")
            print("\nDetalhes do erro:")
            traceback.print_exc()
            return False
    
    def show_welcome(self):
        print("="*70)
        print("ASSISTENTE EDUCACIONAL - SISTEMA RAG HÍBRIDO")
        print("="*70)
    
    def show_system_info(self):
        
        info = self.rag_system.get_system_info()
        
        print("\n" + "="*50)
        print("INFORMAÇÕES DO SISTEMA")
        print("="*50)
        
        hybrid_status = "ATIVO" if info['hybrid_enabled'] else "INATIVO"
        print(f"Sistema Híbrido: {hybrid_status}")
        
        if not info['hybrid_available']:
            print("Sistema híbrido não disponível - usando sistema padrão")
        
        print(f"Tipo de Retriever: {info['retriever_type'].upper()}")
        print(f"Modelo LLM: {info['model']}")
        print(f"Modelo Embeddings: {info['embedding_model']}")
        print(f"Chunks por busca: {info['retrieval_k']}")
        
        if info.get('total_chunks'):
            print(f"Total de Chunks: {info['total_chunks']:,}")
            print(f"Artigos Indexados: {info['indexed_articles']:,}")
            
            if info.get('available_articles'):
                articles_preview = ', '.join(info['available_articles'][:15])
                if len(info['available_articles']) > 15:
                    articles_preview += f"... (+{len(info['available_articles']) - 15} mais)"
                print(f"Artigos Disponíveis: {articles_preview}")
        
        print("="*50)
    
    def test_specific_article(self, article_number: str):
        
        if not article_number.isdigit():
            print("Número de artigo inválido. Use apenas números.")
            return
        
        print(f"\nTestando busca por Art. {article_number}...")
        
        try:
            result = self.rag_system.test_article_search(article_number)
            
            if 'error' in result:
                print(f"Erro: {result['error']}")
                return
            
            summary = result['summary']
            chunks = result['chunks']
            
            print(f"\nResultado do teste:")
            print(f"   Chunks encontrados: {result['found_chunks']}")
            print(f"   Matches diretos: {summary['direct_matches']}")
            print(f"   Qualidade: {summary['quality'].upper()}")
            print(f"   Status: {'SUCESSO' if summary['success'] else 'FALHA'}")
            
            if chunks:
                print(f"\nPrévia dos chunks (top 3):")
                for i, chunk in enumerate(chunks[:3], 1):
                    target_status = "ALVO" if chunk['contains_target_article'] else "GENERICO"
                    print(f"\n   {i}. {target_status} Score: {chunk['score']}")
                    print(f"      {chunk['preview'][:100]}...")
                    
                    if chunk['metadata'].get('article_number'):
                        print(f"      Artigo: {chunk['metadata']['article_number']}")
            
        except Exception as e:
            print(f"Erro no teste: {str(e)}")
    
    def run_batch_test(self):
        
        print("\nExecutando teste em lote...")
        
        test_articles = ['175', '178', '200', '25', '47', '106']
        
        try:
            results = self.rag_system.batch_test_articles(test_articles)
            
            print(f"\nResultado do Teste em Lote:")
            print(f"   Artigos testados: {results['articles_tested']}")
            print(f"   Taxa de sucesso: {results['success_rate']}")
            print(f"   Sucessos: {results['successful']}")
            print(f"   Falhas: {results['failed']}")
            
            print(f"\nDetalhes por artigo:")
            for article, details in results['details'].items():
                status_icon = "SUCESSO" if details['status'] == 'success' else "FALHA"
                
                if details['status'] == 'error':
                    print(f"   Art. {article}: {status_icon} {details['message']}")
                else:
                    quality = details.get('quality', 'N/A')
                    matches = details.get('direct_matches', 0)
                    total = details.get('total_chunks', 0)
                    
                    print(f"   Art. {article}: {status_icon} {matches}/{total} matches diretos (qualidade: {quality})")
            
        except Exception as e:
            print(f"Erro no teste em lote: {str(e)}")
    
    def debug_query(self, query: str):
        
        print(f"\nAnálise detalhada para: '{query}'")
        print("-" * 50)
        
        try:
            debug_result = self.rag_system.debug_query(query)
            
            print(f"Sistema: {debug_result['system_type'].upper()}")
            print(f"Timestamp: {debug_result['timestamp']}")
            
            if 'error' in debug_result:
                print(f"Erro: {debug_result['error']}")
                return
            
            for step in debug_result['steps']:
                agent_name = step['agent'].upper()
                print(f"\n{agent_name}:")
                
                if 'chunks_found' in step:
                    chunks = step['chunks_found']
                    icon = "OK" if chunks > 0 else "AVISO"
                    print(f"   {icon} Chunks encontrados: {chunks}")
                
                if 'answer_generated' in step:
                    generated = step['answer_generated']
                    icon = "OK" if generated else "ERRO"
                    print(f"   {icon} Resposta gerada: {generated}")
                
                if 'next_agent' in step:
                    print(f"   Próximo: {step['next_agent']}")
                
                for log in step.get('logs', []):
                    print(f"   Log: {log}")
            
        except Exception as e:
            print(f"Erro na análise: {str(e)}")
    
    def show_session_stats(self):
        
        total_queries = len(self.session_queries)
        
        if total_queries == 0:
            print("\nNenhuma pergunta feita nesta sessão.")
            return
        
        print(f"\nESTATÍSTICAS DA SESSÃO")
        print("-" * 30)
        print(f"Total de perguntas: {total_queries}")
        
        article_queries = 0
        semantic_queries = 0
        
        for query in self.session_queries:
            import re
            if re.search(r'\b(?:art\.?|artigo)\s*(\d+)', query.lower()):
                article_queries += 1
            else:
                semantic_queries += 1
        
        print(f"Buscas por artigos: {article_queries}")
        print(f"Buscas semânticas: {semantic_queries}")
        
        if total_queries > 0:
            print(f"\nÚltimas queries:")
            for i, query in enumerate(self.session_queries[-5:], 1):
                preview = query[:50] + "..." if len(query) > 50 else query
                print(f"   {i}. {preview}")
    
    def process_user_input(self, user_input: str) -> bool:
        
        user_input = user_input.strip()
        
        if not user_input:
            return True
        
        if user_input.lower() == "sair":
            print("\nAté logo! Continue seus estudos!")
            return False
        
        elif user_input.lower() == "info":
            self.show_system_info()
            return True
        
        elif user_input.lower().startswith("test "):
            article_num = user_input[5:].strip()
            self.test_specific_article(article_num)
            return True
        
        elif user_input.lower().startswith("debug "):
            query = user_input[6:].strip()
            if query:
                self.debug_query(query)
            else:
                print("Forneça uma query para debug. Ex: 'debug o que é cidade inteligente'")
            return True
        
        elif user_input.lower() == "batch-test":
            self.run_batch_test()
            return True
        
        elif user_input.lower().startswith("verbose "):
            setting = user_input[8:].strip().lower()
            if setting == "on":
                self.rag_system.set_verbose(True)
                print("Logs detalhados ativados")
            elif setting == "off":
                self.rag_system.set_verbose(False)
                print("Logs detalhados desativados")
            else:
                print("Use 'verbose on' ou 'verbose off'")
            return True
        
        elif user_input.lower() == "stats":
            self.show_session_stats()
            return True
        
        else:
            try:
                print(f"\nProcessando: '{user_input[:60]}{'...' if len(user_input) > 60 else ''}'")
                
                self.session_queries.append(user_input)
                
                answer = self.rag_system.ask(user_input)
                print(f"\nResposta:")
                print(f"{answer}")
                
            except Exception as e:
                print(f"\nErro ao processar pergunta: {str(e)}")
                print("Detalhes técnicos:")
                traceback.print_exc()
        
        return True
    
    def run(self):
        
        if not self.initialize():
            return
        
        self.show_welcome()
        
        try:
            while True:
                try:
                    user_input = input("\nVocê: ")
                    
                    if not self.process_user_input(user_input):
                        break
                        
                except KeyboardInterrupt:
                    print("\n\nInterrompido pelo usuário!")
                    break
                    
                except EOFError:
                    print("\n\nSessão encerrada!")
                    break
                    
        except Exception as e:
            print(f"\nErro crítico: {e}")
            traceback.print_exc()
        
        if len(self.session_queries) > 0:
            print(f"\nSessão encerrada. {len(self.session_queries)} pergunta(s) processada(s).")


def main():
    
    vectorstore_path = "vectorstore"
    
    if len(sys.argv) > 1:
        vectorstore_path = sys.argv[1]
    
    system = InteractiveRAGSystem(vectorstore_path)
    system.run()


if __name__ == "__main__":
    main()