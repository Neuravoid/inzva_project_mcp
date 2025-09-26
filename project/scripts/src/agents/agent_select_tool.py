# src/agents/agent_select_tool.py

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
        self.session_id = session_id
        # self.tools'u __init__ içinde bir kez yüklemek yerine, her process'te alacağız
        # çünkü bu asenkron bir çağrı.

    async def process(self, state):
        """Process state and determine query type. Bu metod artık asenkron."""
        logger.info("Processing in ToolSelectingAgent")

        # Asenkron olarak araçları al
        available_tools_list = await get_structured_tools(self.client_session)
        
        conversation_history = state.get('conversation_history', [])
        history_str = "\n".join(conversation_history)

        # Prompt için araç listesini hazırla
        tools_for_prompt = "\n".join([f"{tool['name']}: {tool['description']}" for tool in available_tools_list])

        prompt = format_prompt(self.prompt, user_question=state.get('current_user_query', ''),
                               available_tools_list=tools_for_prompt)

        selected_tool_name = self.llm_interface.generate(prompt).strip()
        logger.info(f"LLM selected tool name: '{selected_tool_name}'")

        # Seçilen aracı tam tanımıyla bul
        selected_tool_definition = next((tool for tool in available_tools_list if tool['name'] == selected_tool_name), None)

        if not selected_tool_definition:
            logger.warning(f"Tool '{selected_tool_name}' not found in available tools. Returning no_tool_found.")
            # State'i güncellemek için boş bir tool tanımı veya hata durumu dönebiliriz.
            return {"selected_tool": {"name": "no_tool_found", "description": "No suitable tool was found."}}

        logger.info(f"Selected tool definition: {selected_tool_definition}")
        
        # State'e seçilen aracın tam tanımını kaydet
        self.data_store.save_state({
            "current_agent": "tool_selecting",
            "selected_tool": selected_tool_definition
        }, self.session_id)

        # State güncellemesi için tam tanımı döndür
        return {"selected_tool": selected_tool_definition}