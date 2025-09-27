from langgraph.graph import StateGraph, END
from src.main.state import GraphState
from src.agents.agent_select_tool import ToolSelectingAgent
from src.agents.agent_input_parameter import InputParameterAgent
from src.agents.agent_output_generation import OutputGenerationAgent
from src.agents.agent_executing_tool import ToolExecutingAgent
from loguru import logger

def after_tool_selection(state: GraphState) -> str:
    """A tool has been selected, decide if it's valid or not."""
    selected_tool = state.get("selected_tool", {})
    tool_name = selected_tool.get("name", "no_tool_found")
    logger.debug(f"ROUTER: Checking selected tool. Tool name: {tool_name}")

    if tool_name == "no_tool_found":
        return "generate_output_no_tool"
    else:
        return "extract_parameters"

class WorkflowEngine():
    def __init__(self, llm_interface=None, client_session=None, data_store=None, session_id=None):
        self.llm_interface = llm_interface
        self.session = client_session
        self.session_id = session_id
        self.data_store = data_store
        
        self.tool_selecting_agent = ToolSelectingAgent(self.llm_interface, self.session, self.data_store, self.session_id)
        self.tool_executing_agent = ToolExecutingAgent(self.llm_interface, self.session, self.data_store)
        self.input_parameter_agent = InputParameterAgent(self.llm_interface, self.session, self.data_store)
        self.output_generation_agent = OutputGenerationAgent(self.llm_interface, self.session, self.data_store)

        self.graph = self._build_graph()
        self.runnable = self.graph.compile()

    def _build_graph(self):
        workflow = StateGraph(GraphState)
        
        workflow.add_node("tool_selecting_agent", self.tool_selecting_agent.process)
        workflow.add_node("tool_executing_agent", self.tool_executing_agent.process)
        workflow.add_node("input_parameter_agent", self.input_parameter_agent.process)
        workflow.add_node("output_generation_agent", self.output_generation_agent.process)
        
        workflow.set_entry_point("tool_selecting_agent")
        
        workflow.add_edge("input_parameter_agent", "tool_executing_agent")
        workflow.add_edge("tool_executing_agent", "output_generation_agent")
        
        workflow.add_conditional_edges(
            "tool_selecting_agent",
            after_tool_selection,
            {
                "extract_parameters": "input_parameter_agent",
                "generate_output_no_tool": "output_generation_agent"
            }
        )
        
        workflow.add_edge("output_generation_agent", END)
        
        return workflow
    
    async def process(self, question: str):
        previous_states = self.data_store.get_session_states(self.session_id)
        conversation_history = [s['state_data'].get('conversation_history', []) for s in previous_states]
        conversation_history = conversation_history[0] if conversation_history else []


        conversation_history.append(f"Human: {question}")

        initial_state = GraphState(
            current_user_query=question,
            conversation_history=conversation_history,
            session_id=self.session_id,
            client_session=self.session
        )
        
        final_state = await self.runnable.ainvoke(initial_state)

        final_answer = final_state.get("answer", "[Cevap üretilemedi]")
        final_state["answer"] = final_answer

        conversation_history.append(f"AI: {final_answer}")

        self.data_store.save_state({
            "final_answer": final_answer,
            "conversation_history": conversation_history
        }, self.session_id)

        return dict(final_state)