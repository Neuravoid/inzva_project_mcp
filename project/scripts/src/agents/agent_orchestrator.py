from loguru import logger
from ..main.prompts import Prompts, format_prompt
from ..database.state_store import StateStore

class OrchestratorAgent():

    def __init__(self, llm_interface=None, client_session=None, data_store=None):
        self.prompt = Prompts.get_orchestrator_prompt()
        self.data_store = data_store or StateStore()
        self.llm_interface = llm_interface
        self.client_session = client_session

    def route(self, state) -> str:
        routed_agent = state.get('routed_agent', '').strip()

        try:
            if routed_agent == "tool_selecting_agent":
                logger.info("tool_selecting_agent has been selected by the orchestrator")
                return "route_tool_selecting_agent"
            
            elif routed_agent == "tool_executing_agent":
                logger.info("tool_executing_agent has been selected by the orchestrator")
                return "route_tool_executing_agent"

            elif routed_agent == "generation_router_agent":
                logger.info("generation_router_agent has been selected by the orchestrator")
                return "route_generation_router_agent"

            elif routed_agent == "input_parameter_agent":
                logger.info("input_parameter_agent has been selected by the orchestrator")
                return "route_input_parameter_agent"
            
            elif routed_agent == "output_generation_agent":
                logger.info("output_generation_agent has been selected by the orchestrator")
                return "route_output_generation_agent"
   
            else:
                return "error"

        except Exception as e:
            logger.error(f"There has been an error with classification routing. \n {e}")
            return "error"
    
    def process(self, state) -> dict:
        """Process state and determine query type"""
        conversation_history = state.get('conversation_history', '').strip()
        current_user_query = state.get('current_user_query', '').strip()
        selected_tool = state.get('selected_tool', '').strip()
        tool_inputs = state.get('tool_inputs', '').strip()
        tool_result = state.get('tool_result', '').strip()
        available_tools = state.get('available_tools', '').strip()
        input_status = state.get('input_status', '').strip()
        answer_status = state.get('answer_status', '').strip()

        full_prompt = format_prompt(self.prompt, user_question=current_user_query,
                                    conversation_history=conversation_history,
                                    selected_tool=selected_tool,
                                    tool_inputs=tool_inputs,
                                    tool_result=tool_result,
                                    available_tools=available_tools,
                                    input_status=input_status,
                                    answer_status=answer_status)

        routed_agent = self.llm_interface.generate(full_prompt)
        self.route(state)

        return {"routed_agent": routed_agent}
   