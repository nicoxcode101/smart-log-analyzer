import os
from typing import List, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import google.generativeai as genai
from dotenv import load_dotenv

# --- 1. CONFIGURATION & SECURE ENVIRONMENT ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Missing GEMINI_API_KEY in .env file. Please add it before running.")

genai.configure(api_key=api_key)
DATABASE_URL = "sqlite:///./log_analyzer.db"

# --- 2. DATABASE SETUP ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LogRecord(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    status = Column(Integer, nullable=True)
    message = Column(String, nullable=True)
    is_anomaly = Column(Boolean, default=False)
    ai_explanation = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)

# --- 3. PYDANTIC SCHEMAS ---
class LogInput(BaseModel):
    timestamp: Optional[str] = "Missing Timestamp"
    ip_address: Optional[str] = "Unknown IP"
    status: Optional[int] = 0
    message: str

# --- 4. FASTAPI APPLICATION ---
app = FastAPI(
    title="Smart Log Analyzer API", 
    version="1.0.0",
    description="Enterprise API for log ingestion and AI anomaly detection"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 5. LOGIC & INTELLIGENCE ---
def analyze_anomaly(log: LogInput) -> bool:
    if log.status and (log.status >= 500 or log.status in [401, 403]):
        return True
        
    critical_keywords = ["timeout", "exception", "crash", "failed", "unauthorized", "fatal"]
    message_lower = log.message.lower()
    
    if any(keyword in message_lower for keyword in critical_keywords):
        return True
        
    return False

def get_ai_root_cause(log_entry: dict) -> str:
    try:
        model = genai.GenerativeModel("gemini-3.6-flash")
        prompt = f"As a Site Reliability Engineer, briefly explain this anomalous server log. Provide the Root Cause and Next Step in plain English: {log_entry}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"\n--- GEMINI API ERROR ---\n{e}\n------------------------\n")
        return f"API Error: {str(e)}"

# --- 6. V1 ENDPOINTS (Versioning & Pagination) ---
@app.post("/api/v1/ingest/")
def ingest_logs(logs: List[LogInput]):
    db = SessionLocal()
    for log in logs:
        is_flagged = analyze_anomaly(log)
        ai_text = None
        
        if is_flagged:
            ai_text = get_ai_root_cause(log.model_dump())
            
        new_log = LogRecord(
            timestamp=log.timestamp,
            ip_address=log.ip_address,
            status=log.status,
            message=log.message,
            is_anomaly=is_flagged,
            ai_explanation=ai_text
        )
        db.add(new_log)
        
    db.commit()
    db.close()
    return {"message": f"Successfully ingested and analyzed {len(logs)} logs."}

@app.get("/api/v1/logs/")
def get_logs(skip: int = Query(0, description="Records to skip"), limit: int = Query(100, description="Maximum records to return")):
    db = SessionLocal()
    # Pagination: Offset and Limit ensures we never crash the DB with massive queries
    logs = db.query(LogRecord).order_by(LogRecord.id.desc()).offset(skip).limit(limit).all()
    db.close()
    return logs