import streamlit as st
import sys
import warnings
from pathlib import Path

# Configuração da página 
st.set_page_config(
    page_title="Assistente Educacional RAG",
    page_icon="🎓",
    layout="centered"
)

# Suprimir warnings desnecessários
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

# Adicionar paths para importação
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_dir))

# Importar o sistema RAG
try:
    from src.agent_educacional import AgentEducacional
except ImportError:
    try:
        from agent_educacional import AgentEducacional
    except ImportError as e:
        st.error(f"Erro ao importar AgentEducacional: {e}")
        st.stop()

@st.cache_resource
def load_rag_system(vectorstore_path):
    """Carrega o sistema RAG com cache"""
    return AgentEducacional(vectorstore_path)

def main():
    # Título centralizado
    st.markdown("""
    <h1 style='text-align: center; color: #1f77b4; margin-bottom: 10px;'>
        🎓 Assistente Do Plano Diretor de Campina Grande
    </h1>
    <p style='text-align: center; color: #666; margin-bottom: 30px;'>
        Sistema de perguntas e respostas com agentes inteligentes
    </p>
    """, unsafe_allow_html=True)
    
    # Inicializar sistema RAG
    st.session_state.rag_system = load_rag_system("vectorstore")
    
    # Inicializar histórico de conversas
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Inicializar contador para limpar campo
    if 'input_counter' not in st.session_state:
        st.session_state.input_counter = 0
    
    # Exibir histórico de conversas
    if st.session_state.messages:
        st.markdown("### Conversa")
        
        for message in st.session_state.messages:
            if message['role'] == 'user':
                st.markdown(f"**Você:** {message['content']}")
            else:
                st.markdown(f"**Assistente:**")
                st.markdown(message['content'])
                st.markdown("---")
    
    # Campo de entrada 
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "",
            placeholder="Digite sua pergunta sobre o Plano Diretor...",
            key=f"user_input_{st.session_state.input_counter}",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Enviar", type="primary")
    
    # Processar entrada
    if (send_button or user_input) and user_input and user_input.strip():
        try:
            # Adicionar pergunta do usuário ao histórico
            st.session_state.messages.append({
                'role': 'user',
                'content': user_input.strip()
            })
            
            # Obter resposta do sistema com indicador de carregamento
            with st.spinner("Carregando..."):
                response = st.session_state.rag_system.ask(user_input.strip())
            
            # Adicionar resposta ao histórico
            st.session_state.messages.append({
                'role': 'assistant',
                'content': response
            })
            
            st.session_state.input_counter += 1
            st.rerun()
            
        except Exception as e:
            st.error(f"Erro ao processar pergunta: {e}")
    
    elif send_button and (not user_input or not user_input.strip()):
        st.warning("Digite uma pergunta.")

if __name__ == "__main__":
    main()