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
        # route mantığı aynı kalabilir
        routed_agent = state.get('routed_agent', '').strip()

        try:
            if routed_agent == "tool_selecting_agent":
                return "route_tool_selecting_agent"
            elif routed_agent == "tool_executing_agent":
                return "route_tool_executing_agent"
            elif routed_agent == "input_parameter_agent":
                return "route_input_parameter_agent"
            elif routed_agent == "output_generation_agent":
                return "route_output_generation_agent"
            else:
                logger.warning(f"Orchestrator received an unknown agent to route: {routed_agent}")
                return "error"
        except Exception as e:
            logger.error(f"There has been an error with classification routing. \n {e}")
            return "error"
    
    def process(self, state) -> dict:
        """Process state and determine the next agent."""
        conversation_history = state.get('conversation_history', [])
        # GÜNCELLENDİ: listeyi string'e çevir
        history_str = "\n".join(conversation_history)

        full_prompt = format_prompt(self.prompt, 
                                    user_question=state.get('current_user_query', ''),
                                    conversation_history=history_str,
                                    selected_tool=str(state.get('selected_tool', '')),
                                    tool_inputs=str(state.get('tool_inputs', '')),
                                    tool_result=str(state.get('tool_result', '')),
                                    available_tools=str(state.get('available_tools', '')),
                                    input_status=str(state.get('input_status', '')),
                                    answer_status=str(state.get('answer_status', '')))

        routed_agent = self.llm_interface.generate(full_prompt)
        
        # State'e `routed_agent`'ı ekleyerek döndür. `route` metodu bunu kullanacak.
        return {"routed_agent": routed_agent}