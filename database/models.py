"""
Database models for Ship Safety System Integration Platform
Stores system events, states, and compliance monitoring data.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (Column, Integer, String, DateTime, Boolean, Float,
                        Text, Enum as SQLEnum, select)
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./ship_safety_system.db"
Base = declarative_base()


# Enums
class SystemType(str, Enum):
    EMERGENCY_STOP = "emergency_stop"
    FIRE_DETECTION = "fire_detection"
    CCTV = "cctv"
    PAGA = "paga"
    COMMUNICATION = "communication"
    COMPLIANCE = "compliance"


class EventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class SystemStatus(str, Enum):
    NORMAL = "normal"
    ALARM = "alarm"
    FAULT = "fault"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"


# Database Models
class SystemEvent(Base):
    """System events and logs table."""
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    system_type = Column(SQLEnum(SystemType), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    severity = Column(SQLEnum(EventSeverity), nullable=False, index=True)
    message = Column(Text, nullable=False)
    location = Column(String(100), nullable=True)
    additional_data = Column(Text, nullable=True)  # JSON string for extra data


class SystemState(Base):
    """Current system states table."""
    __tablename__ = "system_states"

    id = Column(Integer, primary_key=True, index=True)
    system_type = Column(SQLEnum(SystemType), nullable=False, unique=True,
                         index=True)
    status = Column(SQLEnum(SystemStatus), nullable=False)
    last_update = Column(DateTime, default=datetime.utcnow)
    active_alarms = Column(Integer, default=0)
    performance_score = Column(Float, default=100.0)
    details = Column(Text, nullable=True)  # JSON string for additional details


class ComplianceCheck(Base):
    """Compliance monitoring table."""
    __tablename__ = "compliance_checks"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    standard_type = Column(String(50), nullable=False)  # SOLAS, DNV, etc.
    check_name = Column(String(200), nullable=False)
    passed = Column(Boolean, nullable=False)
    system_type = Column(SQLEnum(SystemType), nullable=False)
    details = Column(Text, nullable=True)
    recommendation = Column(Text, nullable=True)


class FireZone(Base):
    """Fire detection zones table."""
    __tablename__ = "fire_zones"

    id = Column(Integer, primary_key=True, index=True)
    zone_name = Column(String(100), nullable=False, unique=True)
    deck_level = Column(String(50), nullable=False)
    detector_count = Column(Integer, default=0)
    status = Column(SQLEnum(SystemStatus), default=SystemStatus.NORMAL)
    last_test = Column(DateTime, nullable=True)
    temperature = Column(Float, nullable=True)
    smoke_level = Column(Float, nullable=True)


class CCTVCamera(Base):
    """CCTV camera configuration table."""
    __tablename__ = "cctv_cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(String(50), nullable=False, unique=True)
    location = Column(String(100), nullable=False)
    zone = Column(String(50), nullable=True)
    status = Column(SQLEnum(SystemStatus), default=SystemStatus.NORMAL)
    recording = Column(Boolean, default=False)
    last_maintenance = Column(DateTime, nullable=True)


# Pydantic models for API responses
class SystemEventResponse(BaseModel):
    id: int
    timestamp: datetime
    system_type: SystemType
    event_type: str
    severity: EventSeverity
    message: str
    location: Optional[str] = None

    class Config:
        from_attributes = True


class SystemStateResponse(BaseModel):
    system_type: SystemType
    status: SystemStatus
    last_update: datetime
    active_alarms: int
    performance_score: float

    class Config:
        from_attributes = True


class ComplianceCheckResponse(BaseModel):
    timestamp: datetime
    standard_type: str
    check_name: str
    passed: bool
    system_type: SystemType
    details: Optional[str] = None
    recommendation: Optional[str] = None

    class Config:
        from_attributes = True


# Database initialization
async def init_database():
    """Initialize the database and create all tables."""
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Initialize default system states
    async_session = sessionmaker(engine, class_=AsyncSession,
                                 expire_on_commit=False)
    async with async_session() as session:
        # Check if system states exist, if not create defaults
        for system_type in SystemType:
            # Use proper query to check if system_type already exists
            result = await session.execute(
                select(SystemState).where(SystemState.system_type == system_type)
            )
            existing = result.first()
            if not existing:
                system_state = SystemState(
                    system_type=system_type,
                    status=SystemStatus.NORMAL,
                    performance_score=100.0
                )
                session.add(system_state)

        # Initialize fire zones
        default_zones = [
            {"zone_name": "Engine Room", "deck_level": "Lower Deck",
             "detector_count": 8},
            {"zone_name": "Bridge", "deck_level": "Upper Deck",
             "detector_count": 4},
            {"zone_name": "Crew Quarters", "deck_level": "Main Deck",
             "detector_count": 12},
            {"zone_name": "Cargo Hold", "deck_level": "Lower Deck",
             "detector_count": 16},
            {"zone_name": "Galley", "deck_level": "Main Deck",
             "detector_count": 6}
        ]

        for zone_data in default_zones:
            # Use proper SQLAlchemy query syntax instead of raw SQL
            result = await session.execute(
                select(FireZone).where(FireZone.zone_name == zone_data['zone_name'])
            )
            existing_zone = result.first()
            if not existing_zone:
                fire_zone = FireZone(**zone_data)
                session.add(fire_zone)

        # Initialize CCTV cameras
        default_cameras = [
            {"camera_id": "CAM001", "location": "Bridge", "zone": "Bridge"},
            {"camera_id": "CAM002", "location": "Engine Room",
             "zone": "Engine Room"},
            {"camera_id": "CAM003", "location": "Main Deck",
             "zone": "Crew Quarters"},
            {"camera_id": "CAM004", "location": "Cargo Hold",
             "zone": "Cargo Hold"},
            {"camera_id": "CAM005", "location": "Galley", "zone": "Galley"},
            {"camera_id": "CAM006", "location": "Emergency Exit",
             "zone": "Main Deck"}
        ]

        for camera_data in default_cameras:
            # Use proper SQLAlchemy query syntax instead of raw SQL
            result = await session.execute(
                select(CCTVCamera).where(CCTVCamera.camera_id == camera_data['camera_id'])
            )
            existing_camera = result.first()
            if not existing_camera:
                camera = CCTVCamera(**camera_data)
                session.add(camera)

        await session.commit()

    await engine.dispose()


# Database session management
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession,
                                 expire_on_commit=False)


async def get_db_session():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session
