"""
State definitions for workflow engine
"""
from typing import TypedDict, Optional, Any

class GraphState(TypedDict, total=False):
  """State representation for the workflow graph.

  NOTE: total=False allows us to add keys dynamically (e.g. agents can return
  additional fields like 'answer'). We declare the core fields plus the
  'answer' field explicitly so downstream code (backend & notebook) can rely
  on it without KeyError.
  """
  session_id: Optional[str]
  conversation_history: list[str]
  current_user_query: str
  selected_tool: Optional[str]
  tool_inputs: Optional[dict[str, Any]]
  tool_result: Optional[str | dict | list | Any]
  available_tools: list[dict[str, Any]]
  input_status: Optional[str]
  answer_status: Optional[str]
  routed_agent: Optional[str]
  client_session: Optional[Any]
  answer: Optional[str]

  