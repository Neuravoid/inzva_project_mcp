# neuravoid/inzva_project_mcp/inzva_project_mcp-ede13d7216f472a3544df84fe293f51acc2d9f74/project/scripts/src/agents/agent_input_parameter.py

from loguru import logger
from ..main.prompts import Prompts, format_prompt
from ..database.state_store import StateStore
from src.main.model import LLMInterface
import json
import re

class InputParameterAgent():

    def __init__(self, llm_interface=LLMInterface(), client_session=None, data_store=None):
        self.prompt = Prompts.get_input_parameter_agent_prompt()
        self.llm_interface = llm_interface
        self.client_session = client_session
        self.data_store = data_store or StateStore()

    def _parse_json_from_response(self, response: str) -> dict:
        """Extracts and parses a JSON object from a string, handling markdown code blocks and NaN values."""
        match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
        if match:
            json_str = match.group(1)
        else:
            json_str = response

        try:
            json_str = json_str.replace("NaN", "null")
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"Original response string: {response}")
            return {"error": "failed_to_parse_json", "details": str(e)}

    def process(self, state):
        conversation_history = state.get('conversation_history', [])
        selected_tool = state.get('selected_tool', {})

        # DÜZELTME: Parametre isimleri yerine, aracın tam input şemasını alıyoruz.
        tool_schema = selected_tool.get('input_schema', {})
        
        conversation_text = "\n".join(conversation_history)

        # DÜZELTME: Prompt'u, parametre isimleri yerine tam şema ile formatlıyoruz.
        prompt = format_prompt(self.prompt, 
                               tool_schema=json.dumps(tool_schema, indent=2), 
                               user_conversation=conversation_text)
        
        response_str = self.llm_interface.generate(prompt)
        logger.info(f"Raw input parameters extracted from LLM: {response_str}")

        parsed_inputs = self._parse_json_from_response(response_str)
        logger.info(f"Parsed input parameters: {parsed_inputs}")
        
        return {"tool_inputs": parsed_inputs}