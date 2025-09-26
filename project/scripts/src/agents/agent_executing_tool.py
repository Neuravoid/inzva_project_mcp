# neuravoid/inzva_project_mcp/inzva_project_mcp-ede13d7216f472a3544df84fe293f51acc2d9f74/project/scripts/src/agents/agent_executing_tool.py

from loguru import logger
from src.agents.utils import execute_tool_with_params
from src.database.state_store import StateStore

class ToolExecutingAgent():

    def __init__(self, llm_interface=None, client_session=None, data_store=None):
        self.llm_interface = llm_interface
        self.client_session = client_session
        self.data_store = data_store or StateStore()

    async def process(self, state):
        """Process state and execute the selected tool."""
        logger.info("Processing in ToolExecutingAgent")

        selected_tool = state.get('selected_tool', {})
        # HATA DÜZELTİLDİ: 'input_params' yerine 'tool_inputs' kullanılıyor
        tool_inputs = state.get('tool_inputs', {}) 
        
        tool_name = selected_tool.get('name')
        if not tool_name or tool_name == 'no_tool_found':
            logger.error("No valid tool selected for execution.")
            return {"tool_result": {"error": "No valid tool was selected to be executed."}}

        logger.info(f"Executing tool '{tool_name}' with inputs: {tool_inputs}")

        execution_result = await execute_tool_with_params(
            tool_name,
            tool_inputs,
            self.client_session
        )
        logger.info(f"Executed tool {tool_name} with result: {execution_result}")
        
        self.data_store.save_state({
            "current_agent": "tool_executing",
            "tool_result": execution_result
        }, state.get("session_id"))

        # HATA DÜZELTİLDİ: State anahtarı 'tool_result' olarak güncellendi
        return {
            "tool_result": execution_result
        }