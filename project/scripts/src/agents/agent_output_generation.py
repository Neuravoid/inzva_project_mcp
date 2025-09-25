from loguru import logger
from ..main.prompts import Prompts, format_prompt
from ..database.state_store import StateStore

class OutputGenerationAgent():

    def __init__(self, llm_interface=None, client_session=None, data_store=None):
        self.prompts = Prompts.get_generation_agent_prompts()
        self.data_store = data_store or StateStore()
        self.llm_interface = llm_interface
        self.client_session = client_session
    
    def process(self, state):
        """Process state and determine query type"""
        question = state.get('question', '').strip()
        prompt = self.prompts.get("router_prompt", "")
        classification = self.llm_interface.generate(prompt, {"message": question})

        return {"classification": classification}
    
    def route(self, state):
        classification = state.get("classification", "").strip()
        try:
            if classification == "selamlama":
                logger.info("The prompt has been classified as greetings")
                return "say_hello"
            elif classification == "rag":
                logger.info("The prompt has been classified as rag")
                return "call_agent"
            else:
                return "error"
        except Exception as e:
            logger.error(f"There has been an error with classification routing. \n {e}")
            return "error"