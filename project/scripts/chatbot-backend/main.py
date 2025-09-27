from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sys
import asyncio
from pathlib import Path
import logging
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main.workflow import WorkflowEngine
from src.agents.utils import open_client
from src.database.state_store import StateStore
from src.main.model import LLMInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chatbot Backend API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Oturum bazlı (session-specific) motorları ve mcp client'larını saklamak için cache'ler
session_engines = {}
session_clients = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str
    gemini_api_key: str = Field(..., alias='gemini_api_key')
    mcp_user: str = Field(..., alias='mcp_user')
    mcp_password: str = Field(..., alias='mcp_password')

class ChatResponse(BaseModel):
    answer: str
    session_id: str

# --- Startup/Shutdown olayları artık kullanılmıyor, her şey istek bazlı ---

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Ana chat endpoint'i. Her oturum için kendi WorkflowEngine'ini yönetir."""
    try:
        session_id = request.session_id
        logger.info(f"Chat request for session: {session_id}, Message: {request.message}")

        # Eğer bu oturum için bir motor (engine) henüz yoksa, oluştur.
        if session_id not in session_engines:
            logger.info(f"Creating new WorkflowEngine for session: {session_id}")
            
            # Bu oturuma özel MCP client'ını oluştur
            mcp_client = await open_client(
                username=request.mcp_user,
                password=request.mcp_password
            )
            session_clients[session_id] = mcp_client

            # Bu oturuma özel LLM arayüzünü oluştur
            llm_interface = LLMInterface(api_key=request.gemini_api_key)

            # Bu oturuma özel WorkflowEngine'i oluştur ve cache'le
            session_engines[session_id] = WorkflowEngine(
                llm_interface=llm_interface,
                client_session=mcp_client,
                data_store=StateStore(),
                session_id=session_id
            )

        # İlgili oturumun motorunu al ve işlemi gerçekleştir
        session_workflow = session_engines[session_id]
        result = await session_workflow.process(request.message)
        
        answer = result.get('answer', 'An answer could not be generated.')
        logger.info(f"Generated answer for session {session_id}: {answer}")

        return ChatResponse(answer=answer, session_id=session_id)

    except Exception as e:
        logger.error(f"Error during chat for session {request.session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

# ... (Diğer endpoint'ler - health, history vb. - aynı kalabilir) ...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)