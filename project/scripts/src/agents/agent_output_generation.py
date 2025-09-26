from loguru import logger
from ..main.prompts import Prompts, format_prompt
from ..database.state_store import StateStore

class OutputGenerationAgent():

    def __init__(self, llm_interface=None, client_session=None, data_store=None):
        # GÜNCELLENDİ: Doğrudan çıktı üretme prompt'u alınıyor
        self.prompt = Prompts.get_generation_agent_prompt()
        self.data_store = data_store or StateStore()
        self.llm_interface = llm_interface
        self.client_session = client_session
    
    def process(self, state):
        """Process state and generate final response."""
        conversation_history = state.get('conversation_history', [])
        tool_result = state.get('tool_result', {})
        
        # Konuşma geçmişini tek bir metin haline getir
        conversation_text = "\n".join(conversation_history)

        full_prompt = format_prompt(self.prompt, 
                                     user_conversation=conversation_text, 
                                     tool_result=str(tool_result)) # Tool sonucunu string'e çevir
        
        final_answer = self.llm_interface.generate(full_prompt)
        logger.info(f"Generated final answer: {final_answer}")
        
        # LangGraph'in state'i güncellemesi için sonucu döndür
        return {"answer": final_answer}