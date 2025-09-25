import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path
from loguru import logger

class StateStore:
    def __init__(self, db_path: str = "workflow_state.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Database tablosunu oluştur"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS workflow_states (
                        id TEXT PRIMARY KEY,
                        session_id TEXT,
                        state_data TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        status TEXT DEFAULT 'active'
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_session_id 
                    ON workflow_states(session_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at 
                    ON workflow_states(created_at)
                """)
                
                logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def save_state(self, state: Dict[str, Any], session_id: Optional[str] = None) -> str:
        """State'i veritabanına kaydet"""
        state_id = str(uuid.uuid4())
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO workflow_states 
                    (id, session_id, state_data, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    state_id,
                    session_id,
                    json.dumps(state, ensure_ascii=False, indent=2),
                    datetime.now(),
                    datetime.now()
                ))
                
                logger.info(f"State saved: {state_id} for session: {session_id}")
                return state_id
                
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            raise
    
    def load_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """State'i ID ile yükle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT state_data FROM workflow_states 
                    WHERE id = ? AND status = 'active'
                """, (state_id,))
                
                row = cursor.fetchone()
                if row:
                    state_data = json.loads(row[0])
                    logger.info(f"State loaded: {state_id}")
                    return state_data
                else:
                    logger.warning(f"State not found: {state_id}")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to load state {state_id}: {e}")
            return None
    
    def update_state(self, state_id: str, state: Dict[str, Any]) -> bool:
        """Mevcut state'i güncelle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE workflow_states 
                    SET state_data = ?, updated_at = ?
                    WHERE id = ? AND status = 'active'
                """, (
                    json.dumps(state, ensure_ascii=False, indent=2),
                    datetime.now(),
                    state_id
                ))
                
                if cursor.rowcount > 0:
                    logger.info(f"State updated: {state_id}")
                    return True
                else:
                    logger.warning(f"State not found for update: {state_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update state {state_id}: {e}")
            return False
    
    def get_session_states(self, session_id: str) -> list[Dict[str, Any]]:
        """Session'a ait tüm state'leri getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, state_data, created_at, updated_at 
                    FROM workflow_states 
                    WHERE session_id = ? AND status = 'active'
                    ORDER BY created_at DESC
                """, (session_id,))
                
                states = []
                for row in cursor.fetchall():
                    states.append({
                        'id': row[0],
                        'state_data': json.loads(row[1]),
                        'created_at': row[2],
                        'updated_at': row[3]
                    })
                
                logger.info(f"Found {len(states)} states for session: {session_id}")
                return states
                
        except Exception as e:
            logger.error(f"Failed to get session states {session_id}: {e}")
            return []
    
    def delete_state(self, state_id: str) -> bool:
        """State'i soft delete yap"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE workflow_states 
                    SET status = 'deleted', updated_at = ?
                    WHERE id = ?
                """, (datetime.now(), state_id))
                
                if cursor.rowcount > 0:
                    logger.info(f"State deleted: {state_id}")
                    return True
                else:
                    logger.warning(f"State not found for deletion: {state_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to delete state {state_id}: {e}")
            return False
    
    def cleanup_old_states(self, days: int = 7) -> int:
        """Eski state'leri temizle"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    UPDATE workflow_states 
                    SET status = 'expired', updated_at = ?
                    WHERE created_at < datetime('now', '-{} days')
                    AND status = 'active'
                """.format(days), (datetime.now(),))
                
                deleted_count = cursor.rowcount
                logger.info(f"Cleaned up {deleted_count} old states")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup old states: {e}")
            return 0
    
    def get_state_history(self, session_id: str, limit: int = 10) -> list[Dict[str, Any]]:
        """Session'ın state geçmişini getir"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT id, state_data, created_at, status
                    FROM workflow_states 
                    WHERE session_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (session_id, limit))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'id': row[0],
                        'state_data': json.loads(row[1]),
                        'created_at': row[2],
                        'status': row[3]
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Failed to get state history {session_id}: {e}")
            return []
