#!/usr/bin/env python3
"""
Real-time Database Enhancements for Ship Safety System
Integrates realistic sensor data with existing safety systems
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from .historical_data_manager import HistoricalDataManager, SensorData, SystemPerformanceHistory
from .sensor_data_generator import MaritimeSensorGenerator
from .models import SystemState, SystemType, SystemStatus

class RealTimeEnhancer:
    """
    Enhances the safety system with real-time sensor data and analytics.
    
    Integrates with:
    - Safety System Manager
    - Individual safety systems  
    - Historical data collection
    - Performance monitoring
    """
    
    def __init__(self, safety_manager, historical_manager: HistoricalDataManager):
        self.safety_manager = safety_manager
        self.historical_manager = historical_manager
        self.sensor_generator = MaritimeSensorGenerator()
        self.enhanced_systems = {}
        self.active = False
        
    async def initialize(self):
        """Initialize real-time enhancements."""
        await self.historical_manager.initialize()
        
        # Map safety systems to their sensor types
        self.enhanced_systems = {
            "emergency_stop": ["VIBE_ER_001", "POWER_ER_001"],
            "fire_detection": ["TEMP_ER_001", "TEMP_ER_002", "SMOKE_BR_001", "TEMP_GAL_001", "CO2_CQ_001"],
            "cctv": ["MOTION_CH_001", "DOOR_BR_001"],
            "paga": ["NOISE_LEVELS"],  # Would add noise level sensors
            "communication": ["SIGNAL_STRENGTH"],  # Would add signal strength sensors
            "compliance": ["ALL_SENSORS"]  # Compliance monitors all sensors
        }
        
        logger.info("🔄 Real-time database enhancements initialized")
    
    async def start_enhancements(self):
        """Start all real-time enhancement processes."""
        self.active = True
        
        # Start historical data collection
        await self.historical_manager.start_data_collection()
        
        # Start enhancement tasks
        asyncio.create_task(self._update_system_performance())
        asyncio.create_task(self._simulate_operational_changes())
        asyncio.create_task(self._monitor_sensor_health())
        asyncio.create_task(self._generate_realistic_events())
        
        logger.info("🚀 Real-time enhancements started")
    
    async def stop_enhancements(self):
        """Stop all enhancement processes."""
        self.active = False
        await self.historical_manager.stop_data_collection()
        logger.info("🛑 Real-time enhancements stopped")
    
    async def _update_system_performance(self):
        """Continuously update system performance based on real sensor data."""
        while self.active:
            try:
                for system_name in self.enhanced_systems.keys():
                    # Get system's sensor data
                    sensor_ids = self.enhanced_systems[system_name]
                    performance_score = await self._calculate_realistic_performance(sensor_ids)
                    
                    # Update the safety system's performance
                    await self._update_safety_system_performance(system_name, performance_score)
                
                await asyncio.sleep(60)  # Update every minute
                
            except Exception as e:
                logger.error(f"Error updating system performance: {e}")
                await asyncio.sleep(60)
    
    async def _calculate_realistic_performance(self, sensor_ids: List[str]) -> float:
        """Calculate realistic performance score based on sensor data."""
        base_score = 100.0
        
        async with self.historical_manager.session_factory() as session:
            # Get recent sensor data (last hour)
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            
            for sensor_id in sensor_ids:
                if sensor_id in ["ALL_SENSORS", "NOISE_LEVELS", "SIGNAL_STRENGTH"]:
                    continue  # Skip virtual sensors
                
                # Get recent readings for this sensor
                result = await session.execute(
                    select(SensorData).where(
                        SensorData.sensor_id == sensor_id,
                        SensorData.timestamp >= cutoff_time
                    ).order_by(SensorData.timestamp.desc()).limit(10)
                )
                
                readings = result.scalars().all()
                
                if not readings:
                    continue
                
                # Reduce score based on sensor issues
                for reading in readings:
                    if reading.is_faulty:
                        base_score -= 5.0  # Faulty sensor reduces performance
                    if reading.is_alarm:
                        base_score -= 3.0  # Alarms reduce performance
                    if reading.quality < 0.8:
                        base_score -= 2.0  # Poor quality reduces performance
        
        # Add realistic variation and degradation over time
        time_factor = self._get_time_degradation_factor()
        environmental_factor = self._get_environmental_factor()
        
        final_score = base_score * time_factor * environmental_factor
        
        # Add some realistic noise
        noise = random.uniform(-2, 2)
        final_score += noise
        
        return max(50.0, min(100.0, final_score))
    
    def _get_time_degradation_factor(self) -> float:
        """Simulate equipment degradation over time."""
        # Equipment gradually degrades but gets restored during maintenance
        current_hour = datetime.utcnow().hour
        
        # Simulate daily degradation cycle
        degradation = 1.0 - (current_hour * 0.005)  # Slight degradation throughout day
        
        # Weekly maintenance cycle (better performance on Mondays)
        day_of_week = datetime.utcnow().weekday()
        if day_of_week == 0:  # Monday - post maintenance
            degradation += 0.05
        elif day_of_week == 6:  # Sunday - pre maintenance
            degradation -= 0.03
        
        return max(0.85, min(1.0, degradation))
    
    def _get_environmental_factor(self) -> float:
        """Get environmental factors affecting performance."""
        sea_state = self.sensor_generator.sea_state
        weather_factor = self.sensor_generator.weather_factor
        
        # Rough seas and bad weather reduce performance
        environmental_impact = 1.0 - ((sea_state - 1) * 0.02) - ((weather_factor - 1) * 0.05)
        
        return max(0.8, min(1.0, environmental_impact))
    
    async def _update_safety_system_performance(self, system_name: str, performance_score: float):
        """Update the safety system's performance score."""
        try:
            # Update in the safety manager's system data
            if hasattr(self.safety_manager, system_name):
                system = getattr(self.safety_manager, system_name)
                if hasattr(system, 'performance_score'):
                    system.performance_score = performance_score
            
            # Update in database
            async with self.historical_manager.session_factory() as session:
                # Get system type enum
                system_type_map = {
                    "emergency_stop": SystemType.EMERGENCY_STOP,
                    "fire_detection": SystemType.FIRE_DETECTION,
                    "cctv": SystemType.CCTV,
                    "paga": SystemType.PAGA,
                    "communication": SystemType.COMMUNICATION,
                    "compliance": SystemType.COMPLIANCE
                }
                
                if system_name in system_type_map:
                    await session.execute(
                        update(SystemState).where(
                            SystemState.system_type == system_type_map[system_name]
                        ).values(
                            performance_score=performance_score,
                            last_update=datetime.utcnow()
                        )
                    )
                    await session.commit()
                    
        except Exception as e:
            logger.error(f"Error updating system performance for {system_name}: {e}")
    
    async def _simulate_operational_changes(self):
        """Simulate realistic operational changes throughout the day."""
        while self.active:
            try:
                current_hour = datetime.utcnow().hour
                
                # Simulate different operational modes based on time
                if 6 <= current_hour <= 18:  # Day time - normal operations
                    if self.sensor_generator.operational_mode != "normal":
                        self.sensor_generator.simulate_emergency_scenario("normal_operations")
                        logger.info("🌅 Switching to normal day operations")
                        
                elif 22 <= current_hour or current_hour <= 4:  # Night time - reduced activity
                    if self.sensor_generator.sea_state > 3:
                        self.sensor_generator.sea_state = 2  # Calmer at night
                        logger.info("🌙 Night time - reduced operational activity")
                
                # Randomly simulate weather changes
                if random.random() < 0.1:  # 10% chance every cycle
                    new_weather = random.uniform(0.8, 1.5)
                    new_sea_state = random.randint(1, 6)
                    
                    self.sensor_generator.weather_factor = new_weather
                    self.sensor_generator.sea_state = new_sea_state
                    
                    logger.info(f"🌊 Weather change: sea state {new_sea_state}, "
                               f"weather factor {new_weather:.2f}")
                
                # Occasionally simulate emergency scenarios for testing
                if random.random() < 0.02:  # 2% chance
                    scenarios = ["engine_room_fire", "rough_weather"]
                    scenario = random.choice(scenarios)
                    self.sensor_generator.simulate_emergency_scenario(scenario)
                    logger.warning(f"🚨 Simulated emergency scenario: {scenario}")
                    
                    # Return to normal after a few minutes
                    await asyncio.sleep(300)  # 5 minutes
                    self.sensor_generator.simulate_emergency_scenario("normal_operations")
                    logger.info("✅ Returned to normal operations")
                
                await asyncio.sleep(1800)  # Check every 30 minutes
                
            except Exception as e:
                logger.error(f"Error in operational simulation: {e}")
                await asyncio.sleep(1800)
    
    async def _monitor_sensor_health(self):
        """Monitor sensor health and trigger maintenance alerts."""
        while self.active:
            try:
                async with self.historical_manager.session_factory() as session:
                    # Check for sensors with poor quality
                    cutoff_time = datetime.utcnow() - timedelta(hours=2)
                    
                    result = await session.execute(
                        select(SensorData.sensor_id, SensorData.quality).where(
                            SensorData.timestamp >= cutoff_time,
                            SensorData.quality < 0.7  # Poor quality threshold
                        ).group_by(SensorData.sensor_id)
                    )
                    
                    poor_sensors = result.all()
                    
                    for sensor_id, quality in poor_sensors:
                        logger.warning(f"🔧 Sensor {sensor_id} quality degraded: {quality:.2f}")
                        
                        # Trigger maintenance alert in safety manager
                        await self._trigger_maintenance_alert(sensor_id, quality)
                    
                    # Check for sensors that haven't reported recently
                    result = await session.execute(
                        select(SensorData.sensor_id).where(
                            SensorData.timestamp < cutoff_time
                        ).group_by(SensorData.sensor_id)
                    )
                    
                    stale_sensors = [row[0] for row in result]
                    
                    for sensor_id in stale_sensors:
                        logger.warning(f"📡 Sensor {sensor_id} not reporting - possible failure")
                        await self._trigger_sensor_failure_alert(sensor_id)
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"Error monitoring sensor health: {e}")
                await asyncio.sleep(3600)
    
    async def _generate_realistic_events(self):
        """Generate realistic system events based on operational patterns."""
        while self.active:
            try:
                # Generate routine maintenance events
                if random.random() < 0.1:  # 10% chance per cycle
                    system = random.choice(list(self.enhanced_systems.keys()))
                    await self._generate_maintenance_event(system)
                
                # Generate operational events
                if random.random() < 0.2:  # 20% chance per cycle
                    await self._generate_operational_event()
                
                # Generate compliance events
                if random.random() < 0.05:  # 5% chance per cycle
                    await self._generate_compliance_event()
                
                await asyncio.sleep(600)  # Every 10 minutes
                
            except Exception as e:
                logger.error(f"Error generating events: {e}")
                await asyncio.sleep(600)
    
    async def _trigger_maintenance_alert(self, sensor_id: str, quality: float):
        """Trigger maintenance alert for degraded sensor."""
        if self.safety_manager and hasattr(self.safety_manager, '_handle_system_event'):
            event_data = {
                "sensor_id": sensor_id,
                "quality": quality,
                "alert_type": "maintenance_required",
                "priority": "medium"
            }
            await self.safety_manager._handle_system_event(
                SystemType.COMPLIANCE, "maintenance_alert", event_data
            )
    
    async def _trigger_sensor_failure_alert(self, sensor_id: str):
        """Trigger alert for failed sensor."""
        if self.safety_manager and hasattr(self.safety_manager, '_handle_system_event'):
            event_data = {
                "sensor_id": sensor_id,
                "alert_type": "sensor_failure",
                "priority": "high"
            }
            await self.safety_manager._handle_system_event(
                SystemType.COMPLIANCE, "sensor_failure", event_data
            )
    
    async def _generate_maintenance_event(self, system: str):
        """Generate a realistic maintenance event."""
        events = [
            f"{system} system routine maintenance completed",
            f"{system} system performance check completed",
            f"{system} system sensor calibration completed",
            f"{system} system backup test completed"
        ]
        
        event = random.choice(events)
        logger.info(f"🔧 Generated maintenance event: {event}")
    
    async def _generate_operational_event(self):
        """Generate realistic operational events."""
        events = [
            "Crew watch change completed",
            "Navigation system position update",
            "Engine room inspection completed",
            "Safety drill conducted",
            "Port authority communication",
            "Weather routing update received"
        ]
        
        event = random.choice(events)
        logger.info(f"⚓ Generated operational event: {event}")
    
    async def _generate_compliance_event(self):
        """Generate compliance-related events."""
        events = [
            "SOLAS compliance check completed",
            "DNV classification survey reminder",
            "ISM audit preparation initiated",
            "Port state control preparation",
            "Safety certificate renewal reminder"
        ]
        
        event = random.choice(events)
        logger.info(f"📋 Generated compliance event: {event}")
    
    async def get_realtime_dashboard_data(self) -> Dict:
        """Get enhanced real-time data for dashboard."""
        try:
            # Get recent sensor trends
            sensor_trends = {}
            for sensor_id in ["TEMP_ER_001", "SMOKE_BR_001", "FUEL_001", "VIBE_ER_001"]:
                trend = await self.historical_manager.get_sensor_trends(sensor_id, hours=6)
                sensor_trends[sensor_id] = {
                    "current_value": trend.average_value,
                    "trend_direction": trend.trend_direction,
                    "trend_strength": trend.trend_strength,
                    "quality": trend.quality_average,
                    "alarm_frequency": trend.alarm_frequency,
                    "prediction_1h": trend.predictions.get("1h", 0)
                }
            
            # Get recent alarm analytics
            alarm_analytics = await self.historical_manager.get_alarm_analytics(hours=24)
            
            # Get system performance history
            performance_history = {}
            for system in self.enhanced_systems.keys():
                history = await self.historical_manager.get_system_performance_history(
                    system, hours=12
                )
                performance_history[system] = history[-10:] if history else []  # Last 10 points
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "sensor_trends": sensor_trends,
                "alarm_analytics": alarm_analytics,
                "performance_history": performance_history,
                "operational_status": {
                    "sea_state": self.sensor_generator.sea_state,
                    "weather_factor": self.sensor_generator.weather_factor,
                    "operational_mode": self.sensor_generator.operational_mode
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time dashboard data: {e}")
            return {}

# Integration function for existing safety manager
async def integrate_realtime_enhancements(safety_manager):
    """
    Integration function to add real-time enhancements to existing safety manager.
    
    Call this from the safety manager initialization.
    """
    try:
        historical_manager = HistoricalDataManager()
        enhancer = RealTimeEnhancer(safety_manager, historical_manager)
        
        await enhancer.initialize()
        await enhancer.start_enhancements()
        
        # Add methods to safety manager
        safety_manager.realtime_enhancer = enhancer
        safety_manager.get_enhanced_dashboard_data = enhancer.get_realtime_dashboard_data
        
        logger.info("✅ Real-time enhancements integrated with safety manager")
        
        return enhancer
        
    except Exception as e:
        logger.error(f"Failed to integrate real-time enhancements: {e}")
        return None 