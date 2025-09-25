from loguru import logger
from src.main.prompts import Prompts, format_prompt
from src.agents.utils import execute_tool_with_params
from src.database.state_store import StateStore

class ToolExecutingAgent():

    def __init__(self, llm_interface=None, client_session=None, data_store=None):
        self.llm_interface = llm_interface
        self.client_session = client_session
        self.data_store = data_store or StateStore()

    def process(self, state):
        # Tool selection ve input parameter extraction burada değil, 
        # önceki agent'lar tarafından yapılmış olmalı
        selected_tool = state.get('selected_tool', {})
        input_params = state.get('input_params', {})
        
        if not selected_tool or not selected_tool.get('tool_name'):
            logger.error("No tool selected for execution")
            return {"execution_result": {"error": "No tool selected"}}

        execution_result = execute_tool_with_params(
            selected_tool['tool_name'],
            input_params,
            self.client_session
        )
        logger.info(f"Executed tool {selected_tool['tool_name']} with result: {execution_result}")
        self.data_store.save_state({
            "current_agent": "tool_executing",
            "tool_result": execution_result
        })
        return {
            "execution_result": execution_result
        }

