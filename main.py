#!/usr/bin/env python3
"""
Ship Safety System Integration Platform
Main Application Entry Point

Demonstrates ship safety system design, integration, and compliance monitoring
for maritime engineering positions.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from systems.safety_manager import SafetySystemManager
from systems.emergency_stop import EmergencyStopSystem
from systems.fire_detection import FireDetectionSystem
from systems.cctv_system import CCTVSystem
from systems.paga_system import PAGASystem
from systems.communication import CommunicationSystem
from systems.compliance_monitor import ComplianceMonitor
from database.models import init_database
from utils.logger import setup_logger

# Setup logging
logger = setup_logger()

# Initialize FastAPI application
app = FastAPI(
    title="Ship Safety System Integration Platform",
    description="Maritime Safety Systems Integration Dashboard",
    version="1.0.0"
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global system manager
safety_manager = None
active_connections = []

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize all ship safety systems and database on startup."""
    global safety_manager
    
    logger.info("🚢 Initializing Ship Safety System Integration Platform...")
    
    # Initialize database
    await init_database()
    logger.info("✅ Database initialized")
    
    # Initialize all safety systems
    emergency_stop = EmergencyStopSystem()
    fire_detection = FireDetectionSystem()
    cctv_system = CCTVSystem()
    paga_system = PAGASystem()
    communication = CommunicationSystem()
    compliance_monitor = ComplianceMonitor()
    
    # Initialize main safety system manager
    safety_manager = SafetySystemManager(
        emergency_stop=emergency_stop,
        fire_detection=fire_detection,
        cctv_system=cctv_system,
        paga_system=paga_system,
        communication=communication,
        compliance_monitor=compliance_monitor,
        connection_manager=manager
    )
    
    # Start all systems
    await safety_manager.initialize()
    logger.info("✅ All safety systems initialized and integrated")
    
    # Start background monitoring
    asyncio.create_task(safety_manager.start_monitoring())
    logger.info("✅ Background monitoring started")
    
    logger.info("🎯 Ship Safety System Integration Platform ready!")
    logger.info("🌐 Dashboard available at: http://localhost:8000")

@app.on_event("shutdown")
async def shutdown_event():
    """Gracefully shutdown all systems."""
    global safety_manager
    if safety_manager:
        await safety_manager.shutdown()
    logger.info("🛑 Ship Safety System Integration Platform shutdown complete")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard interface."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/system/status")
async def get_system_status():
    """Get current status of all ship safety systems."""
    if not safety_manager:
        return {"error": "Systems not initialized"}
    
    return await safety_manager.get_system_status()

@app.get("/api/system/events")
async def get_recent_events():
    """Get recent system events and logs."""
    if not safety_manager:
        return {"error": "Systems not initialized"}
    
    return await safety_manager.get_recent_events()

@app.get("/api/compliance/status")
async def get_compliance_status():
    """Get current compliance status with maritime standards."""
    if not safety_manager:
        return {"error": "Systems not initialized"}
    
    return await safety_manager.get_compliance_status()

@app.post("/api/emergency/stop")
async def trigger_emergency_stop():
    """Trigger emergency stop system."""
    if not safety_manager:
        return {"error": "Systems not initialized"}
    
    logger.warning("🚨 EMERGENCY STOP TRIGGERED via API")
    result = await safety_manager.trigger_emergency_stop()
    return result

@app.post("/api/fire/alarm/{zone}")
async def trigger_fire_alarm(zone: str):
    """Trigger fire alarm in specific zone."""
    if not safety_manager:
        return {"error": "Systems not initialized"}
    
    logger.warning(f"🔥 FIRE ALARM TRIGGERED in zone {zone}")
    result = await safety_manager.trigger_fire_alarm(zone)
    return result

@app.post("/api/system/reset")
async def reset_all_systems():
    """Reset all safety systems to normal operation."""
    if not safety_manager:
        return {"error": "Systems not initialized"}
    
    logger.info("🔄 SYSTEM RESET initiated")
    result = await safety_manager.reset_all_systems()
    return result

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time system updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            logger.debug(f"Received WebSocket message: {data}")
            
            # Echo back system status if requested
            if data == "get_status" and safety_manager:
                status = await safety_manager.get_system_status()
                await websocket.send_json({"type": "status_update", "data": status})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    logger.info("🚀 Starting Ship Safety System Integration Platform")
    logger.info("📋 This project demonstrates:")
    logger.info("   • Ship safety system design and integration")
    logger.info("   • Maritime compliance monitoring (SOLAS, DNV)")
    logger.info("   • Multi-vendor system coordination")
    logger.info("   • Real-time monitoring and control")
    logger.info("   • Emergency response automation")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 