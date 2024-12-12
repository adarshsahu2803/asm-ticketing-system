# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
from db_service import DynamoDBService
from bedrock_service import BedrockService
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    db = DynamoDBService()
    bedrock = BedrockService()
except Exception as e:
    print(f"Error initializing services: {e}")
    raise

class TicketCreate(BaseModel):
    title: str
    description: str
    priority: Optional[int] = 3

@app.post("/tickets/")
async def create_ticket(ticket: TicketCreate):
    try:
        ticket_id = str(uuid.uuid4())
        
        # Get classification and guidance from Bedrock
        result = bedrock.classify_and_guide_ticket(ticket.description)
        
        ticket_data = {
            "ticket_id": ticket_id,
            "created_at": str(datetime.now()),
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority,
            "status": "new",
            "classification": result
        }
        
        # Store in DynamoDB only if Classified or Prioritized
        if result.get("category") in ["Classified", "Prioritized"]:
            stored_ticket = db.create_ticket(ticket_data)
            return {**stored_ticket, "stored_in_db": True}
        
        return {**ticket_data, "stored_in_db": False}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets/")
async def list_tickets():
    try:
        return db.list_tickets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    try:
        ticket = db.get_ticket(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        return ticket
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)