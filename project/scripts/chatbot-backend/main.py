from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import asyncio
from pathlib import Path
import uuid
import logging

# Ana proje path'ini ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main.workflow import WorkflowEngine
from src.agents.utils import open_client
from src.database.state_store import StateStore
from src.main.model import LLMInterface

# Logging ayarları
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Chatbot Backend API",
    description="MCP WorkflowEngine ile entegre chatbot backend",
    version="1.0.0"
)

# CORS ayarları - React frontend'i için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8080", "http://127.0.0.1:8080"],  # React dev server ve backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global değişkenler
workflow_engine = None
client_session = None
# Oturum bazlı WorkflowEngine cache'i (session_id -> engine)
session_engines = {}

# Request/Response modelleri
class ChatRequest(BaseModel):
    message: str
    session_id: str

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    status: str = "success"

class ErrorResponse(BaseModel):
    error: str
    session_id: str
    status: str = "error"

@app.on_event("startup")
async def startup_event():
    """Uygulama başlatıldığında WorkflowEngine'i hazırla"""
    global workflow_engine, client_session, session_engines
    
    try:
        logger.info("WorkflowEngine başlatılıyor...")
        
        # MCP client session başlat
        client_session = await open_client()
        logger.info("MCP client session başarıyla oluşturuldu")
        
        # LLM interface oluştur
        llm_interface = LLMInterface()
        
        # WorkflowEngine oluştur
        workflow_engine = WorkflowEngine(
            llm_interface=llm_interface,
            client_session=client_session,
            data_store=StateStore(),
            session_id="default"  # Her istek için kendi session_id'sini kullanacak
        )
        
        logger.info("WorkflowEngine başarıyla başlatıldı")
        
    except Exception as e:
        logger.error(f"Startup hatası: {str(e)}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Uygulama kapatıldığında cleanup yap"""
    global client_session
    
    if client_session:
        try:
            # MCP client session'ı kapat
            await client_session.close()
            logger.info("MCP client session kapatıldı")
        except Exception as e:
            logger.error(f"Shutdown hatası: {str(e)}")

@app.get("/")
async def root():
    """API durumu kontrolü"""
    return {
        "message": "Chatbot Backend API çalışıyor",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Sağlık kontrolü endpoint'i"""
    global workflow_engine
    
    if workflow_engine is None:
        raise HTTPException(status_code=503, detail="WorkflowEngine henüz hazır değil")
    
    return {
        "status": "healthy",
        "workflow_engine": "ready",
        "timestamp": str(asyncio.get_event_loop().time())
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Ana chat endpoint'i - React frontend'den gelen mesajları işler"""
    global workflow_engine, client_session, session_engines
    
    if workflow_engine is None or client_session is None:
        raise HTTPException(
            status_code=503, 
            detail="WorkflowEngine henüz hazır değil. Lütfen birkaç saniye bekleyin."
        )
    
    try:
        logger.info(f"Chat isteği alındı - Session: {request.session_id}, Message: {request.message}")
        
        # Session-specific WorkflowEngine'i cache'ten al veya oluştur
        if request.session_id not in session_engines:
            session_engines[request.session_id] = WorkflowEngine(
                llm_interface=LLMInterface(),
                client_session=client_session,
                data_store=StateStore(),
                session_id=request.session_id
            )
        session_workflow = session_engines[request.session_id]
        
        # Geçici test için basit yanıt
        logger.info("WorkflowEngine çağrısı öncesi")
        
        try:
            # Mesajı WorkflowEngine'e gönder
            result = await session_workflow.process(request.message)
            logger.info(f"WorkflowEngine result keys: {list(result.keys())}")
            answer = result.get('answer') or 'Hiçbir yanıt bulunamadı.'
            logger.info(f"Extracted answer: {answer}")
            
        except Exception as workflow_error:
            logger.error(f"WorkflowEngine hatası: {str(workflow_error)}")
            import traceback
            logger.error(f"WorkflowEngine traceback: {traceback.format_exc()}")
            answer = f"Test yanıtı: {request.message} mesajınızı aldım!"  # Geçici test yanıtı
        
        logger.info(f"Final answer: {answer}")
        logger.info(f"Chat cevabı oluşturuldu - Session: {request.session_id}")
        
        return ChatResponse(
            answer=answer,
            session_id=request.session_id,
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Chat işlemi hatası - Session: {request.session_id}, Error: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Hata durumunda HTTPException yerine error response döndür
        return ChatResponse(
            answer=f"Üzgünüm, bir hata oluştu: {str(e)}",
            session_id=request.session_id,
            status="error"
        )

@app.get("/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Belirli bir session'ın geçmişini getir"""
    global workflow_engine
    
    if workflow_engine is None:
        raise HTTPException(status_code=503, detail="WorkflowEngine henüz hazır değil")
    
    try:
        # StateStore'dan session geçmişini al (StateStore instance oluştur)
        state_store = StateStore()
        history = state_store.get_state(session_id)
        
        return {
            "session_id": session_id,
            "history": history,
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Session geçmişi alma hatası - Session: {session_id}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Session geçmişi alınamadı: {str(e)}")

@app.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    """Belirli bir session'ı temizle"""
    global workflow_engine
    
    if workflow_engine is None:
        raise HTTPException(status_code=503, detail="WorkflowEngine henüz hazır değil")
    
    try:
        # Session state'ini temizle (StateStore instance oluştur)
        state_store = StateStore()
        state_store.clear_session(session_id)
        
        return {
            "session_id": session_id,
            "message": "Session başarıyla temizlendi",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Session temizleme hatası - Session: {session_id}, Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Session temizlenemedi: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Development server'ı başlat
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )