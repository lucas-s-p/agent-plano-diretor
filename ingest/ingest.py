from langchain_community.document_loaders import PyPDFLoader
import os
import re
import shutil
from legal_splitter import LegalSplitter
from vector_store import VectorStore


def ingest_pdfs(docs_dir: str = "ingest/docs", 
                vectorstore_path: str = "vectorstore") -> bool:
    """Sistema de ingestão com busca literal + semântica"""
    
    if not os.path.exists(docs_dir):
        print(f"Erro: Diretório {docs_dir} não encontrado")
        return False
    
    pdf_files = [f for f in os.listdir(docs_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"Erro: Nenhum PDF encontrado em {docs_dir}")
        return False
    
    print(f"Processando {len(pdf_files)} PDFs...")
    
    # Inicializar splitter
    splitter = LegalSplitter(max_chunk_size=1600, chunk_overlap=180)
    all_chunks = []
    combined_literal_index = {}
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(docs_dir, pdf_file)
        print(f"\nProcessando: {pdf_file}")
        
        try:
            # Carregar PDF
            loader = PyPDFLoader(pdf_path)
            pages = loader.load()
            
            # Consolidar texto
            full_text = '\n'.join([page.page_content for page in pages])
            
            # Metadados
            base_metadata = {
                'source': pdf_file.replace('.pdf', ''),
                'filename': pdf_file,
                'total_pages': len(pages)
            }
            
            # Dividir texto
            chunks, literal_index = splitter.split_text(full_text, base_metadata)
            
            print(f"  Gerados: {len(chunks)} chunks")
            
            # Análise de artigos críticos
            for art_num in ['175', '178']:
                art_chunks = [c for c in chunks 
                             if c.metadata.get('article_number') == art_num or
                                re.search(rf'\bArt\.?\s*{art_num}\b', c.page_content, re.IGNORECASE)]
                
                if art_chunks:
                    print(f"  ✓ Art. {art_num}: {len(art_chunks)} chunk(s)")
                else:
                    print(f"  ⚠ Art. {art_num}: NÃO encontrado")
            
            # Combinar índices literais
            base_idx = len(all_chunks)
            for art_num, indices in literal_index.items():
                if art_num not in combined_literal_index:
                    combined_literal_index[art_num] = []
                combined_literal_index[art_num].extend([idx + base_idx for idx in indices])
            
            all_chunks.extend(chunks)
            
        except Exception as e:
            print(f"  Erro ao processar {pdf_file}: {str(e)}")
            continue
    
    if not all_chunks:
        print("Erro: Nenhum chunk foi gerado")
        return False
    
    print(f"\nTotal de chunks: {len(all_chunks)}")
    
    # Análise do índice literal
    print(f"\nÍndice literal criado para {len(combined_literal_index)} artigos")
    for art in ['175', '178']:
        if art in combined_literal_index:
            print(f"  Art. {art}: {len(combined_literal_index[art])} referências")
        else:
            print(f"  Art. {art}: NÃO indexado")
    
    # Criar vectorstore
    print("\nCriando vectorstore...")
    
    try:
        # Remover vectorstore antigo
        if os.path.exists(vectorstore_path):
            shutil.rmtree(vectorstore_path)
        
        # Criar vectorstore
        store = VectorStore(vectorstore_path)
        store.create_from_documents(all_chunks, combined_literal_index)
        
        print(f"✓ Vectorstore salvo em: {vectorstore_path}")
        
        # Testes de busca
        print("\nTestando busca...")
        
        test_cases = [
            ("Art. 175", "175"),
            ("Artigo 175", "175"),
            ("Art. 178", "178"),
            ("Artigo 178", "178"),
            ("cidade inteligente diretrizes", "175"),
            ("participação controle social", "178")
        ]
        
        success_count = 0
        
        for query, expected_art in test_cases:
            results = store.search(query, k=3)
            found = False
            
            for doc, score in results:
                if re.search(rf'\bArt\.?\s*{expected_art}\b', doc.page_content, re.IGNORECASE):
                    print(f"✓ '{query}' → Art. {expected_art} (score: {score:.4f})")
                    found = True
                    success_count += 1
                    break
            
            if not found:
                print(f"✗ '{query}' → Art. {expected_art} NÃO encontrado")
        
        print(f"\nResultado: {success_count}/{len(test_cases)} sucessos")
        
        return True
        
    except Exception as e:
        print(f"Erro ao criar vectorstore: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_search(vectorstore_path: str = "vectorstore"):
    """Testa o sistema de busca"""
    
    print("Testando Sistema de Busca")
    print("=" * 50)
    
    try:
        # Carregar vectorstore
        store = VectorStore(vectorstore_path)
        store.load()
        
        print(f"✓ Vectorstore carregado: {len(store.chunks)} chunks")
        print(f"✓ Índice literal: {len(store.literal_index)} artigos")
        
        # Testes
        test_queries = [
            ("Art. 175", "Busca literal direta"),
            ("Artigo 175", "Busca literal com 'Artigo'"),
            ("Art. 178", "Busca literal direta"),
            ("Artigo 178", "Busca literal com 'Artigo'"),
            ("diretrizes cidade inteligente", "Busca semântica"),
            ("participação social controle", "Busca semântica"),
            ("smart city", "Busca conceitual"),
            ("governo aberto", "Busca conceitual")
        ]
        
        for query, description in test_queries:
            print(f"\n{description}: '{query}'")
            
            results = store.search(query, k=3)
            
            if results:
                for i, (doc, score) in enumerate(results):
                    article_match = re.search(r'\bArt\.?\s*(\d+)', doc.page_content)
                    article_info = f"Art. {article_match.group(1)}" if article_match else "Sem artigo"
                    
                    preview = doc.page_content[:100].replace('\n', ' ')
                    print(f"  {i+1}. {article_info} (score: {score:.4f})")
                    print(f"     {preview}...")
            else:
                print("  Nenhum resultado encontrado")
    
    except Exception as e:
        print(f"Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--test":
            vectorstore_path = sys.argv[2] if len(sys.argv) > 2 else "vectorstore"
            test_search(vectorstore_path)
            
        else:
            docs_dir = command
            vectorstore_path = sys.argv[2] if len(sys.argv) > 2 else "vectorstore"
            
            success = ingest_pdfs(docs_dir, vectorstore_path)
            if success:
                print("\nIngestão concluída com sucesso")
                print("Use '--test' para testar o sistema de busca")
            else:
                print("\nFalha na ingestão")
    else:
        # Modo padrão
        success = ingest_pdfs()
        if success:
            print("\nIngestão concluída com sucesso")
            print("Use 'python3 ingest/ingest.py --test' para testar a busca")
        else:
            print("\nFalha na ingestão")