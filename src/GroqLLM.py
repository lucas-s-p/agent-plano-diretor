from groq import Groq

class GroqLLM:
    """Wrapper para a API da Groq"""
    
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model
        
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 1000) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Você é um assistente educacional especializado. Responda sempre baseado no contexto fornecido e inclua citações precisas."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Erro na geração de resposta: {str(e)}"
