from loguru import logger
from ..main.prompts import Prompts, format_prompt
from ..database.state_store import StateStore
from src.main.model import LLMInterface

class InputParameterAgent():

    def __init__(self, llm_interface=LLMInterface(), client_session=None, data_store=None, session_id=None):
        self.prompt = Prompts.get_tool_selecting_agent_prompt()
        self.llm_interface = llm_interface
        self.client_session = client_session
        self.data_store = data_store or StateStore()
        self.session_id = session_id


    def process(self, state):

        current_state = self.data_store.get_session_states(self.session_id) if self.session_id else {}
        if current_state:
            conversation_history = current_state.get('conversation_history', '').strip()
            selected_tool = current_state.get('selected_tool', '').strip()

            prompt = format_prompt(self.prompt, conversation_history=conversation_history, selected_tool=selected_tool)
            response = self.llm_interface.generate(prompt)
        
            logger.info(f"Input parameters: {response}")

            self.data_store.save_state({
                "current_agent": "input_parameter_agent",
                "input_parameters": response,
                "conversation_history": conversation_history,
            }, self.session_id) 

            return {"input_parameters": response}