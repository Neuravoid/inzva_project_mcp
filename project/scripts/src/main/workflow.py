"""Workflow engine for coordinating agents"""
from langgraph.graph import StateGraph, END
from src.main.state import GraphState
from src.agents.agent_orchestrator import OrchestratorAgent
from src.agents.agent_select_tool import ToolSelectingAgent
from src.agents.agent_input_parameter import InputParameterAgent
from src.agents.agent_output_generation import OutputGenerationAgent
from src.agents.agent_executing_tool import ToolExecutingAgent

from loguru import logger

class WorkflowEngine():
    """Engine for managing workflow between agents"""

    def __init__(self, llm_interface=None, client_session=None, data_store=None, session_id=None):
        """Initialize workflow engine"""
        self.llm_interface = llm_interface
        self.session = client_session
        self.session_id = session_id
        self.data_store = data_store
        # Ajanları session_id ile başlat
        self.orchestrator_agent = OrchestratorAgent(self.llm_interface, self.session, self.data_store)
        self.tool_selecting_agent = ToolSelectingAgent(self.llm_interface, self.session, self.data_store)
        self.tool_executing_agent = ToolExecutingAgent(self.llm_interface, self.session, self.data_store)
        self.input_parameter_agent = InputParameterAgent(self.llm_interface, self.session, self.data_store)
        self.output_generation_agent = OutputGenerationAgent(self.llm_interface, self.session, self.data_store)

        # Build workflow graph
        self.graph = self._build_graph()
        self.runnable = self.graph.compile()

    def _build_graph(self):
        """Build workflow graph with nodes and edges"""
        workflow = StateGraph(GraphState)
        
        workflow.add_node("orchestrator", self.orchestrator_agent.process)
        workflow.add_node("tool_selecting_agent", self.tool_selecting_agent.process)
        workflow.add_node("tool_executing_agent", self.tool_executing_agent.process)
        workflow.add_node("input_parameter_agent", self.input_parameter_agent.process)
        workflow.add_node("output_generation_agent", self.output_generation_agent.process)
        
        workflow.add_conditional_edges(
            "orchestrator",
            self.orchestrator_agent.route,
            {
                "route_tool_selecting_agent": "tool_selecting_agent", 
                "route_tool_executing_agent": "tool_executing_agent",
                "route_input_parameter_agent": "input_parameter_agent",
                "route_output_generation_agent": "output_generation_agent",
                "error": END
            }
        )
        
        workflow.add_edge("tool_selecting_agent", "orchestrator")
        workflow.add_edge("tool_executing_agent", "output_generation_agent")
        workflow.add_edge("input_parameter_agent", "orchestrator")
        workflow.add_edge("output_generation_agent", END)
        
        workflow.set_entry_point("orchestrator")
        
        return workflow
    
    def process(self, question: str):
        """Process a user question, managing conversation history."""
        # 1. Mevcut oturumun geçmişini veritabanından yükle
        previous_states = self.data_store.get_session_states(self.session_id)
        conversation_history = []
        if previous_states:
            latest_state_data = previous_states[0].get('state_data', {})
            conversation_history = latest_state_data.get('conversation_history', [])

        # 2. Yeni kullanıcı sorusunu geçmişe ekle
        conversation_history.append(f"Human: {question}")

        # 3. İş akışını güncel state ile başlat
        initial_state = {
            "current_user_query": question,
            "conversation_history": conversation_history,
            "session_id": self.session_id,
            "client_session": self.session,
            "selected_tool": None,
            "tool_inputs": None,
            "tool_result": None,
        }
        
        # Runnable'ı invoke et
        final_state = self.runnable.invoke(initial_state)
        
        # 4. AI'ın son cevabını da geçmişe ekleyip kaydet
        final_answer = final_state.get("answer", "[Cevap üretilemedi]")
        conversation_history.append(f"AI: {final_answer}")
        
        # Nihai durumu tüm geçmişle birlikte veritabanına kaydet
        # Bu, bir sonraki `process` çağrısında geçmişin yüklenebilmesini sağlar
        self.data_store.save_state({
            "final_answer": final_answer,
            "conversation_history": conversation_history
        }, self.session_id)

        return final_state