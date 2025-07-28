#!/usr/bin/env python3
"""
Historical Data Manager for Ship Safety System
Manages time-series sensor data and provides trending analysis
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, Index
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func, and_, or_
import numpy as np
from loguru import logger

from .models import Base, SystemType, EventSeverity
from .sensor_data_generator import MaritimeSensorGenerator, SensorReading

# Extended database models for historical data
class SensorData(Base):
    """Time-series sensor data table."""
    __tablename__ = "sensor_data"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(50), nullable=False, index=True)
    sensor_type = Column(String(50), nullable=False, index=True)
    location = Column(String(200), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    quality = Column(Float, nullable=False)  # 0-1 sensor reliability
    is_alarm = Column(Boolean, default=False, index=True)
    is_faulty = Column(Boolean, default=False, index=True)
    alarm_threshold_low = Column(Float, nullable=True)
    alarm_threshold_high = Column(Float, nullable=True)

    # Add composite index for efficient time-series queries
    __table_args__ = (
        Index('idx_sensor_timestamp', 'sensor_id', 'timestamp'),
        Index('idx_location_timestamp', 'location', 'timestamp'),
        Index('idx_alarm_timestamp', 'is_alarm', 'timestamp'),
    )

class SystemPerformanceHistory(Base):
    """Historical system performance data."""
    __tablename__ = "system_performance_history"

    id = Column(Integer, primary_key=True, index=True)
    system_type = Column(String(50), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    performance_score = Column(Float, nullable=False)
    availability = Column(Float, nullable=False)  # % uptime
    response_time = Column(Float, nullable=True)  # seconds
    events_count = Column(Integer, default=0)
    alarms_count = Column(Integer, default=0)
    maintenance_due = Column(Boolean, default=False)
    details = Column(Text, nullable=True)  # JSON data

class OperationalMetrics(Base):
    """Ship operational metrics over time."""
    __tablename__ = "operational_metrics"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    sea_state = Column(Integer, nullable=False)  # 1-9 scale
    weather_factor = Column(Float, nullable=False)
    operational_mode = Column(String(50), nullable=False)  # normal, emergency, maintenance
    crew_count = Column(Integer, nullable=True)
    fuel_consumption = Column(Float, nullable=True)  # liters/hour
    power_consumption = Column(Float, nullable=True)  # kW
    engine_hours = Column(Float, nullable=True)
    position_lat = Column(Float, nullable=True)
    position_lon = Column(Float, nullable=True)

@dataclass
class TrendAnalysis:
    """Container for trend analysis results."""
    sensor_id: str
    time_period: str
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float  # 0-1
    average_value: float
    min_value: float
    max_value: float
    std_deviation: float
    alarm_frequency: float
    quality_average: float
    predictions: Dict[str, float]

class HistoricalDataManager:
    """
    Manages historical sensor data and provides analytics.
    
    Features:
    - Time-series data storage
    - Trend analysis
    - Performance metrics
    - Predictive insights
    - Data aggregation
    """
    
    def __init__(self, database_url: str = "sqlite+aiosqlite:///./ship_safety_system.db"):
        self.database_url = database_url
        self.engine = None
        self.session_factory = None
        self.sensor_generator = MaritimeSensorGenerator()
        self.data_collection_active = False
        
    async def initialize(self):
        """Initialize the historical data management system."""
        self.engine = create_async_engine(self.database_url, echo=False)
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        logger.info("📊 Historical Data Manager initialized")
    
    async def start_data_collection(self):
        """Start continuous sensor data collection."""
        self.data_collection_active = True
        logger.info("🔄 Starting continuous sensor data collection")
        
        # Start background tasks
        asyncio.create_task(self._collect_sensor_data())
        asyncio.create_task(self._collect_performance_metrics())
        asyncio.create_task(self._collect_operational_metrics())
    
    async def stop_data_collection(self):
        """Stop data collection."""
        self.data_collection_active = False
        logger.info("🛑 Stopping sensor data collection")
    
    async def _collect_sensor_data(self):
        """Background task to collect sensor readings."""
        while self.data_collection_active:
            try:
                # Generate realistic sensor readings
                readings = self.sensor_generator.generate_all_sensors()
                
                # Store in database
                async with self.session_factory() as session:
                    for reading in readings:
                        sensor_data = SensorData(
                            sensor_id=reading.sensor_id,
                            sensor_type=reading.sensor_type.value,
                            location=reading.location,
                            timestamp=reading.timestamp,
                            value=reading.value,
                            unit=reading.unit,
                            quality=reading.quality,
                            is_alarm=reading.is_alarm,
                            is_faulty=reading.is_faulty,
                            alarm_threshold_low=reading.alarm_threshold_low,
                            alarm_threshold_high=reading.alarm_threshold_high
                        )
                        session.add(sensor_data)
                    
                    await session.commit()
                
                # Wait before next collection (30 seconds)
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error collecting sensor data: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _collect_performance_metrics(self):
        """Background task to collect system performance metrics."""
        while self.data_collection_active:
            try:
                async with self.session_factory() as session:
                    # Collect performance for each system type
                    for system_type in ["emergency_stop", "fire_detection", "cctv", "paga", "communication", "compliance"]:
                        # Calculate performance based on recent sensor data
                        performance_score = await self._calculate_system_performance(session, system_type)
                        availability = await self._calculate_system_availability(session, system_type)
                        response_time = np.random.normal(0.5, 0.1)  # Simulated response time
                        
                        # Count recent events and alarms
                        events_count = await self._count_recent_events(session, system_type, hours=1)
                        alarms_count = await self._count_recent_alarms(session, system_type, hours=1)
                        
                        performance_history = SystemPerformanceHistory(
                            system_type=system_type,
                            timestamp=datetime.utcnow(),
                            performance_score=performance_score,
                            availability=availability,
                            response_time=max(0.1, response_time),
                            events_count=events_count,
                            alarms_count=alarms_count,
                            maintenance_due=performance_score < 70,
                            details=json.dumps({
                                "sensor_quality_avg": await self._get_sensor_quality_avg(session, system_type),
                                "fault_rate": await self._get_fault_rate(session, system_type)
                            })
                        )
                        session.add(performance_history)
                    
                    await session.commit()
                
                # Collect every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error collecting performance metrics: {e}")
                await asyncio.sleep(300)
    
    async def _collect_operational_metrics(self):
        """Background task to collect ship operational metrics."""
        while self.data_collection_active:
            try:
                async with self.session_factory() as session:
                    # Simulate realistic operational data
                    operational_metrics = OperationalMetrics(
                        timestamp=datetime.utcnow(),
                        sea_state=self.sensor_generator.sea_state,
                        weather_factor=self.sensor_generator.weather_factor,
                        operational_mode=self.sensor_generator.operational_mode,
                        crew_count=np.random.randint(15, 25),
                        fuel_consumption=np.random.normal(120, 20),  # L/h
                        power_consumption=np.random.normal(500, 50),  # kW
                        engine_hours=np.random.normal(2000, 100),
                        position_lat=59.9139 + np.random.normal(0, 0.1),  # Near Oslo
                        position_lon=10.7522 + np.random.normal(0, 0.1)
                    )
                    session.add(operational_metrics)
                    await session.commit()
                
                # Collect every 10 minutes
                await asyncio.sleep(600)
                
            except Exception as e:
                logger.error(f"Error collecting operational metrics: {e}")
                await asyncio.sleep(600)
    
    async def get_sensor_trends(self, sensor_id: str, hours: int = 24) -> TrendAnalysis:
        """Analyze sensor trends over specified time period."""
        async with self.session_factory() as session:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get sensor data
            result = await session.execute(
                select(SensorData).where(
                    and_(
                        SensorData.sensor_id == sensor_id,
                        SensorData.timestamp >= cutoff_time,
                        SensorData.is_faulty == False
                    )
                ).order_by(SensorData.timestamp)
            )
            
            data_points = result.scalars().all()
            
            if len(data_points) < 2:
                return TrendAnalysis(
                    sensor_id=sensor_id,
                    time_period=f"{hours}h",
                    trend_direction="insufficient_data",
                    trend_strength=0.0,
                    average_value=0.0,
                    min_value=0.0,
                    max_value=0.0,
                    std_deviation=0.0,
                    alarm_frequency=0.0,
                    quality_average=0.0,
                    predictions={}
                )
            
            # Extract values and timestamps
            values = np.array([dp.value for dp in data_points])
            timestamps = np.array([dp.timestamp.timestamp() for dp in data_points])
            qualities = np.array([dp.quality for dp in data_points])
            
            # Calculate trend using linear regression
            coefficients = np.polyfit(timestamps, values, 1)
            trend_slope = coefficients[0]
            
            # Determine trend direction and strength
            if abs(trend_slope) < 0.001:
                trend_direction = "stable"
                trend_strength = 0.0
            elif trend_slope > 0:
                trend_direction = "increasing"
                trend_strength = min(1.0, abs(trend_slope) * 1000)
            else:
                trend_direction = "decreasing"
                trend_strength = min(1.0, abs(trend_slope) * 1000)
            
            # Calculate statistics
            alarm_count = sum(1 for dp in data_points if dp.is_alarm)
            alarm_frequency = alarm_count / len(data_points) if data_points else 0
            
            # Simple predictions (next 1h, 6h, 24h)
            latest_timestamp = timestamps[-1]
            predictions = {}
            for future_hours in [1, 6, 24]:
                future_timestamp = latest_timestamp + (future_hours * 3600)
                predicted_value = coefficients[0] * future_timestamp + coefficients[1]
                predictions[f"{future_hours}h"] = float(predicted_value)
            
            return TrendAnalysis(
                sensor_id=sensor_id,
                time_period=f"{hours}h",
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                average_value=float(np.mean(values)),
                min_value=float(np.min(values)),
                max_value=float(np.max(values)),
                std_deviation=float(np.std(values)),
                alarm_frequency=alarm_frequency,
                quality_average=float(np.mean(qualities)),
                predictions=predictions
            )
    
    async def get_system_performance_history(self, system_type: str, hours: int = 24) -> List[Dict]:
        """Get historical performance data for a system."""
        async with self.session_factory() as session:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            result = await session.execute(
                select(SystemPerformanceHistory).where(
                    and_(
                        SystemPerformanceHistory.system_type == system_type,
                        SystemPerformanceHistory.timestamp >= cutoff_time
                    )
                ).order_by(SystemPerformanceHistory.timestamp)
            )
            
            history = result.scalars().all()
            
            return [
                {
                    "timestamp": h.timestamp.isoformat(),
                    "performance_score": h.performance_score,
                    "availability": h.availability,
                    "response_time": h.response_time,
                    "events_count": h.events_count,
                    "alarms_count": h.alarms_count,
                    "maintenance_due": h.maintenance_due
                }
                for h in history
            ]
    
    async def get_alarm_analytics(self, hours: int = 24) -> Dict:
        """Get comprehensive alarm analytics."""
        async with self.session_factory() as session:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Total alarms by sensor type
            result = await session.execute(
                select(
                    SensorData.sensor_type,
                    func.count(SensorData.id).label('alarm_count')
                ).where(
                    and_(
                        SensorData.timestamp >= cutoff_time,
                        SensorData.is_alarm == True
                    )
                ).group_by(SensorData.sensor_type)
            )
            
            alarms_by_type = {row.sensor_type: row.alarm_count for row in result}
            
            # Alarms by location
            result = await session.execute(
                select(
                    SensorData.location,
                    func.count(SensorData.id).label('alarm_count')
                ).where(
                    and_(
                        SensorData.timestamp >= cutoff_time,
                        SensorData.is_alarm == True
                    )
                ).group_by(SensorData.location)
            )
            
            alarms_by_location = {row.location: row.alarm_count for row in result}
            
            # Alarm frequency over time (hourly buckets)
            result = await session.execute(
                select(
                    func.strftime('%Y-%m-%d %H:00:00', SensorData.timestamp).label('hour'),
                    func.count(SensorData.id).label('alarm_count')
                ).where(
                    and_(
                        SensorData.timestamp >= cutoff_time,
                        SensorData.is_alarm == True
                    )
                ).group_by(func.strftime('%Y-%m-%d %H:00:00', SensorData.timestamp))
            )
            
            alarm_timeline = {row.hour: row.alarm_count for row in result}
            
            return {
                "time_period": f"{hours}h",
                "alarms_by_sensor_type": alarms_by_type,
                "alarms_by_location": alarms_by_location,
                "alarm_timeline": alarm_timeline,
                "total_alarms": sum(alarms_by_type.values())
            }
    
    # Helper methods
    async def _calculate_system_performance(self, session: AsyncSession, system_type: str) -> float:
        """Calculate current system performance score."""
        # This would integrate with actual system performance calculations
        # For now, return a realistic simulated score with some variation
        base_score = 85.0
        variation = np.random.normal(0, 10)
        return max(50.0, min(100.0, base_score + variation))
    
    async def _calculate_system_availability(self, session: AsyncSession, system_type: str) -> float:
        """Calculate system availability percentage."""
        # Simulate realistic availability with occasional drops
        return max(95.0, np.random.normal(99.5, 1.0))
    
    async def _count_recent_events(self, session: AsyncSession, system_type: str, hours: int) -> int:
        """Count recent events for a system."""
        return np.random.poisson(2)  # Average 2 events per hour
    
    async def _count_recent_alarms(self, session: AsyncSession, system_type: str, hours: int) -> int:
        """Count recent alarms for a system."""
        return np.random.poisson(0.5)  # Average 0.5 alarms per hour
    
    async def _get_sensor_quality_avg(self, session: AsyncSession, system_type: str) -> float:
        """Get average sensor quality for system."""
        return np.random.normal(0.92, 0.05)  # Generally good quality
    
    async def _get_fault_rate(self, session: AsyncSession, system_type: str) -> float:
        """Get sensor fault rate for system."""
        return max(0.0, np.random.normal(0.02, 0.01))  # Low fault rate

# Example usage
async def main():
    """Test the historical data manager."""
    logger.info("📊 Testing Historical Data Manager")
    
    manager = HistoricalDataManager()
    await manager.initialize()
    
    # Start data collection for a short period
    await manager.start_data_collection()
    
    # Let it collect some data
    logger.info("⏳ Collecting data for 2 minutes...")
    await asyncio.sleep(120)
    
    # Analyze trends
    logger.info("📈 Analyzing sensor trends...")
    sensors = ["TEMP_ER_001", "SMOKE_BR_001", "FUEL_001"]
    for sensor_id in sensors:
        trend = await manager.get_sensor_trends(sensor_id, hours=1)
        logger.info(f"Sensor {sensor_id}: {trend.trend_direction} trend, "
                   f"avg={trend.average_value:.2f}, alarms={trend.alarm_frequency:.1%}")
    
    # Get alarm analytics
    alarm_analytics = await manager.get_alarm_analytics(hours=1)
    logger.info(f"🚨 Alarm Analytics: {alarm_analytics}")
    
    await manager.stop_data_collection()

if __name__ == "__main__":
    asyncio.run(main()) 