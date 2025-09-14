from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
import re
import pickle
from typing import List, Dict, Tuple


class VectorStore:
    """Vector store que combina FAISS com busca literal"""
    
    def __init__(self, vectorstore_path: str):
        self.vectorstore_path = vectorstore_path
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vectorstore = None
        self.literal_index = {}
        self.chunks = []
    
    def create_from_documents(self, documents: List[Document], literal_index: Dict):
        """Cria vectorstore a partir dos documentos"""
        
        self.chunks = documents
        self.literal_index = literal_index
        
        # Criar vectorstore FAISS
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        # Salvar tudo
        self.save()
    
    def save(self):
        """Salva vectorstore e índice literal"""
        
        # Salvar vectorstore FAISS
        self.vectorstore.save_local(self.vectorstore_path)
        
        # Salvar índice literal
        literal_path = f"{self.vectorstore_path}/literal_index.pkl"
        with open(literal_path, 'wb') as f:
            pickle.dump(self.literal_index, f)
        
        # Salvar chunks originais
        chunks_path = f"{self.vectorstore_path}/chunks.pkl"
        with open(chunks_path, 'wb') as f:
            pickle.dump(self.chunks, f)
    
    def load(self):
        """Carrega vectorstore e índice literal"""
        
        # Carregar vectorstore FAISS
        self.vectorstore = FAISS.load_local(
            self.vectorstore_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
        
        # Carregar índice literal
        literal_path = f"{self.vectorstore_path}/literal_index.pkl"
        if os.path.exists(literal_path):
            with open(literal_path, 'rb') as f:
                self.literal_index = pickle.load(f)
        
        # Carregar chunks originais
        chunks_path = f"{self.vectorstore_path}/chunks.pkl"
        if os.path.exists(chunks_path):
            with open(chunks_path, 'rb') as f:
                self.chunks = pickle.load(f)
    
    def search(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Busca que combina literal e semântica"""
        
        # Detectar busca por artigo específico
        article_pattern = r'(?:Art\.?|Artigo)\s*(\d+)'
        article_match = re.search(article_pattern, query, re.IGNORECASE)
        
        if article_match:
            article_num = article_match.group(1)
            
            # Busca literal primeiro
            if article_num in self.literal_index:
                literal_results = []
                chunk_indices = self.literal_index[article_num]
                
                for idx in chunk_indices:
                    if idx < len(self.chunks):
                        chunk = self.chunks[idx]
                        # Score baixo para resultados literais (alta prioridade)
                        literal_results.append((chunk, 0.1))
                
                if literal_results:
                    return literal_results[:k]
            
            # Se busca literal não funcionou, tentar semântica com queries expandidas
            expanded_queries = [
                f"Art. {article_num}",
                f"Artigo {article_num}",
                f"Art {article_num}",
                f"diretrizes Art {article_num}",
                f"política Art {article_num}"
            ]
            
            all_semantic_results = []
            
            for exp_query in expanded_queries:
                try:
                    results = self.vectorstore.similarity_search_with_score(exp_query, k=3)
                    for doc, score in results:
                        if re.search(rf'\bArt\.?\s*{article_num}\b', doc.page_content, re.IGNORECASE):
                            all_semantic_results.append((doc, score))
                except:
                    continue
            
            if all_semantic_results:
                # Ordenar por score e remover duplicatas
                unique_results = {}
                for doc, score in all_semantic_results:
                    content_key = doc.page_content[:100]
                    if content_key not in unique_results or score < unique_results[content_key][1]:
                        unique_results[content_key] = (doc, score)
                
                sorted_results = sorted(unique_results.values(), key=lambda x: x[1])
                return sorted_results[:k]
        
        # Busca semântica padrão
        return self.vectorstore.similarity_search_with_score(query, k=k)