from loguru import logger
from ..main.prompts import Prompts, format_prompt
from .utils import get_structured_tools
from ..database.state_store import StateStore
from src.main.model import LLMInterface

class ToolSelectingAgent():

    def __init__(self, llm_interface=LLMInterface(), client_session=None, data_store=None, session_id=None):
        self.prompt = Prompts.get_tool_selecting_agent_prompt()
        self.data_store = data_store or StateStore()
        self.llm_interface = llm_interface
        self.client_session = client_session
        self.tools = get_structured_tools(self.client_session)
        self.session_id = session_id

    def process(self, state):
        """Process state and determine query type"""
        current_state = self.data_store.get_session_states(self.session_id) if self.session_id else {}
        if current_state:
            conversation_history = current_state.get('conversation_history', '').strip()
            available_tools = "\n".join([f"{tool['name']}: {tool['description']}" for tool in self.tools])

        prompt = format_prompt(self.prompt, user_question=conversation_history,
                               available_tools=available_tools)

        selected_tool = self.llm_interface.generate(prompt)
        logger.info(f"Selected tool: {selected_tool}")
        
        self.data_store.save_state({
            "current_agent": "tool_selecting",
            "selected_tool": selected_tool
        }, self.session_id)

        return {"selected_tool": selected_tool}
