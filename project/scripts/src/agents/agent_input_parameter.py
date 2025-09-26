from loguru import logger
from ..main.prompts import Prompts, format_prompt
from ..database.state_store import StateStore
from src.main.model import LLMInterface

class InputParameterAgent():

    def __init__(self, llm_interface=LLMInterface(), client_session=None, data_store=None):
        # HATA DÜZELTİLDİ: Doğru prompt çağrılıyor
        self.prompt = Prompts.get_input_parameter_agent_prompt()
        self.llm_interface = llm_interface
        self.client_session = client_session
        self.data_store = data_store or StateStore()

    def process(self, state):
        conversation_history = state.get('conversation_history', [])
        selected_tool = state.get('selected_tool', {}) # Artık bir dict olmalı

        # Araç parametrelerini (input_schema) al
        tool_parameters = selected_tool.get('input_schema', {}).get('properties', {})
        
        # Konuşma geçmişini tek bir metin haline getir
        conversation_text = "\n".join(conversation_history)

        prompt = format_prompt(self.prompt, 
                               tool_parameters=list(tool_parameters.keys()), 
                               user_conversation=conversation_text)
        
        response = self.llm_interface.generate(prompt)
        logger.info(f"Input parameters extracted: {response}")
        
        # State'i güncellemek için sonucu döndür. Veritabanı kaydını WorkflowEngine yapacak.
        return {"tool_inputs": response}