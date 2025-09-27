from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main.workflow import WorkflowEngine
import os
from src.agents.utils import open_client
from src.database.state_store import StateStore
from src.main.model import LLMInterface

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Chatbot Backend API", version="Final")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_engines = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str
    # Sadece Gemini API anahtarını alıyoruz
    gemini_api_key: str
    # MCP kullanıcı kimlik bilgileri (isteğe bağlı)
    mcp_user: str | None = None
    mcp_password: str | None = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        session_id = request.session_id
        
        if session_id not in session_engines:
            logger.info(f"Creating new WorkflowEngine for session: {session_id}")
            
            # MCP bağlantısı - konteyner içindeki npx'i çalıştıracağız.
            # Önce istekten gelen kimlik bilgilerini kontrol et, yoksa env'den al.
            mcp_user = request.mcp_user or os.getenv("MCP_USER")
            mcp_password = request.mcp_password or os.getenv("MCP_PASSWORD")
            if not mcp_user or not mcp_password:
                raise RuntimeError("MCP kullanıcı bilgileri sağlanmadı. Request içinde veya MCP_USER/MCP_PASSWORD env'de olmalı.")
            mcp_client = await open_client(mcp_user, mcp_password)
            
            # LLM, kullanıcıdan gelen API anahtarı ile başlatılıyor
            llm_interface = LLMInterface(api_key=request.gemini_api_key)

            session_engines[session_id] = WorkflowEngine(
                llm_interface=llm_interface,
                client_session=mcp_client,
                data_store=StateStore(),
                session_id=session_id
            )

        session_workflow = session_engines[session_id]
        result = await session_workflow.process(request.message)
        answer = result.get('answer', 'An answer could not be generated.')
        return ChatResponse(answer=answer, session_id=session_id)

    except Exception as e:
        logger.error(f"Error during chat for session {request.session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)