#!/usr/bin/env python3
"""
Realistic Maritime Sensor Data Generator
Generates authentic sensor data patterns for ship safety systems
"""

import asyncio
import random
import math
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

import numpy as np
from loguru import logger

class SensorType(Enum):
    TEMPERATURE = "temperature"
    SMOKE_DENSITY = "smoke_density"
    PRESSURE = "pressure"
    VIBRATION = "vibration"
    HUMIDITY = "humidity"
    CO2_LEVEL = "co2_level"
    MOTION_DETECTOR = "motion_detector"
    DOOR_STATUS = "door_status"
    POWER_CONSUMPTION = "power_consumption"
    FUEL_LEVEL = "fuel_level"

@dataclass
class SensorReading:
    sensor_id: str
    sensor_type: SensorType
    location: str
    timestamp: datetime
    value: float
    unit: str
    quality: float  # 0-1, sensor reliability
    alarm_threshold_low: float
    alarm_threshold_high: float
    is_alarm: bool
    is_faulty: bool

class MaritimeSensorGenerator:
    """
    Generates realistic maritime sensor data with:
    - Realistic operational patterns (day/night, weather)
    - Gradual equipment degradation
    - Random sensor failures
    - Maritime-specific alarm conditions
    """
    
    def __init__(self):
        self.sensors = {}
        self.base_time = datetime.utcnow()
        self.weather_factor = 1.0  # Weather intensity
        self.sea_state = 1  # Sea conditions 1-9
        self.operational_mode = "normal"  # normal, emergency, maintenance
        self.sensor_readings_history = []
        
        self._initialize_maritime_sensors()
    
    def _initialize_maritime_sensors(self):
        """Initialize realistic maritime sensors across ship zones."""
        
        # Engine Room Sensors
        self.sensors.update({
            "TEMP_ER_001": {
                "type": SensorType.TEMPERATURE,
                "location": "Engine Room - Main Engine",
                "base_value": 85.0,  # °C
                "variation": 15.0,
                "unit": "°C",
                "alarm_low": 40.0,
                "alarm_high": 120.0,
                "degradation_rate": 0.001,  # Performance degrades over time
                "failure_probability": 0.0001,
                "last_maintenance": datetime.utcnow() - timedelta(days=30)
            },
            "TEMP_ER_002": {
                "type": SensorType.TEMPERATURE,
                "location": "Engine Room - Exhaust",
                "base_value": 180.0,
                "variation": 25.0,
                "unit": "°C",
                "alarm_low": 100.0,
                "alarm_high": 250.0,
                "degradation_rate": 0.002,
                "failure_probability": 0.0002,
                "last_maintenance": datetime.utcnow() - timedelta(days=45)
            },
            "VIBE_ER_001": {
                "type": SensorType.VIBRATION,
                "location": "Engine Room - Main Engine Mount",
                "base_value": 2.5,  # mm/s RMS
                "variation": 1.0,
                "unit": "mm/s",
                "alarm_low": 0.0,
                "alarm_high": 8.0,
                "degradation_rate": 0.0005,
                "failure_probability": 0.00005,
                "last_maintenance": datetime.utcnow() - timedelta(days=15)
            },
            "FUEL_001": {
                "type": SensorType.FUEL_LEVEL,
                "location": "Fuel Tank #1",
                "base_value": 75.0,  # % full
                "variation": 5.0,
                "unit": "%",
                "alarm_low": 15.0,
                "alarm_high": 95.0,
                "degradation_rate": 0.0001,
                "failure_probability": 0.00001,
                "last_maintenance": datetime.utcnow() - timedelta(days=60)
            }
        })
        
        # Fire Detection Sensors
        self.sensors.update({
            "SMOKE_BR_001": {
                "type": SensorType.SMOKE_DENSITY,
                "location": "Bridge - Control Room",
                "base_value": 0.05,  # % obscuration/meter
                "variation": 0.02,
                "unit": "%/m",
                "alarm_low": 0.0,
                "alarm_high": 1.5,
                "degradation_rate": 0.0003,
                "failure_probability": 0.00002,
                "last_maintenance": datetime.utcnow() - timedelta(days=90)
            },
            "TEMP_GAL_001": {
                "type": SensorType.TEMPERATURE,
                "location": "Galley - Kitchen Area",
                "base_value": 35.0,
                "variation": 15.0,
                "unit": "°C",
                "alarm_low": 10.0,
                "alarm_high": 80.0,
                "degradation_rate": 0.0002,
                "failure_probability": 0.00001,
                "last_maintenance": datetime.utcnow() - timedelta(days=20)
            },
            "CO2_CQ_001": {
                "type": SensorType.CO2_LEVEL,
                "location": "Crew Quarters - Common Area",
                "base_value": 400.0,  # ppm
                "variation": 100.0,
                "unit": "ppm",
                "alarm_low": 0.0,
                "alarm_high": 1000.0,
                "degradation_rate": 0.0001,
                "failure_probability": 0.00003,
                "last_maintenance": datetime.utcnow() - timedelta(days=120)
            }
        })
        
        # Security/Access Sensors
        self.sensors.update({
            "DOOR_BR_001": {
                "type": SensorType.DOOR_STATUS,
                "location": "Bridge - Main Entry",
                "base_value": 0.0,  # 0=closed, 1=open
                "variation": 0.0,
                "unit": "state",
                "alarm_low": 0.0,
                "alarm_high": 1.0,
                "degradation_rate": 0.0,
                "failure_probability": 0.00001,
                "last_maintenance": datetime.utcnow() - timedelta(days=180)
            },
            "MOTION_CH_001": {
                "type": SensorType.MOTION_DETECTOR,
                "location": "Cargo Hold - Main Area",
                "base_value": 0.0,  # 0=no motion, 1=motion detected
                "variation": 0.0,
                "unit": "state",
                "alarm_low": 0.0,
                "alarm_high": 1.0,
                "degradation_rate": 0.0001,
                "failure_probability": 0.00002,
                "last_maintenance": datetime.utcnow() - timedelta(days=150)
            }
        })
    
    def _calculate_time_factors(self) -> Dict[str, float]:
        """Calculate time-based factors affecting sensor readings."""
        current_time = datetime.utcnow()
        
        # Time of day factor (24-hour cycle)
        hour = current_time.hour
        time_of_day_factor = 1.0 + 0.1 * math.sin(2 * math.pi * hour / 24)
        
        # Day of week factor (maintenance patterns)
        day_of_week = current_time.weekday()
        maintenance_factor = 0.95 if day_of_week == 6 else 1.0  # Sunday maintenance
        
        # Seasonal factor (annual cycle)
        day_of_year = current_time.timetuple().tm_yday
        seasonal_factor = 1.0 + 0.05 * math.sin(2 * math.pi * day_of_year / 365)
        
        return {
            "time_of_day": time_of_day_factor,
            "maintenance": maintenance_factor,
            "seasonal": seasonal_factor,
            "weather": self.weather_factor,
            "sea_state": 1.0 + (self.sea_state - 1) * 0.1
        }
    
    def _simulate_equipment_degradation(self, sensor_config: Dict) -> float:
        """Simulate gradual equipment degradation over time."""
        days_since_maintenance = (datetime.utcnow() - sensor_config["last_maintenance"]).days
        degradation = 1.0 - (sensor_config["degradation_rate"] * days_since_maintenance)
        return max(0.5, degradation)  # Never below 50% performance
    
    def _check_sensor_failure(self, sensor_config: Dict) -> bool:
        """Check if sensor has failed based on probability."""
        return random.random() < sensor_config["failure_probability"]
    
    def generate_realistic_reading(self, sensor_id: str) -> SensorReading:
        """Generate a realistic sensor reading with all factors considered."""
        sensor_config = self.sensors[sensor_id]
        time_factors = self._calculate_time_factors()
        
        # Check for sensor failure
        is_faulty = self._check_sensor_failure(sensor_config)
        
        if is_faulty:
            # Faulty sensor returns invalid readings
            value = random.uniform(-999, 999)
            quality = 0.0
        else:
            # Calculate base value with all factors
            base_value = sensor_config["base_value"]
            variation = sensor_config["variation"]
            
            # Apply time-based factors
            time_factor = (time_factors["time_of_day"] * 
                          time_factors["maintenance"] * 
                          time_factors["seasonal"] * 
                          time_factors["weather"] * 
                          time_factors["sea_state"])
            
            # Apply equipment degradation
            degradation_factor = self._simulate_equipment_degradation(sensor_config)
            
            # Add realistic noise (normal distribution)
            noise = np.random.normal(0, variation * 0.1)
            
            # Special handling for different sensor types
            if sensor_config["type"] == SensorType.DOOR_STATUS:
                # Doors open/close based on operational patterns
                if time_factors["time_of_day"] > 1.1:  # Busy periods
                    value = 1.0 if random.random() < 0.3 else 0.0
                else:
                    value = 1.0 if random.random() < 0.05 else 0.0
            elif sensor_config["type"] == SensorType.MOTION_DETECTOR:
                # Motion based on operational activity
                activity_probability = 0.1 * time_factors["time_of_day"]
                value = 1.0 if random.random() < activity_probability else 0.0
            elif sensor_config["type"] == SensorType.FUEL_LEVEL:
                # Fuel decreases over time with consumption
                consumption_rate = 0.1 * time_factors["sea_state"]  # Higher consumption in rough seas
                value = max(0, base_value - consumption_rate + noise)
            else:
                # Normal analog sensors
                value = (base_value * time_factor * degradation_factor) + noise
            
            # Calculate quality based on degradation and environmental factors
            if variation > 0:
                quality = degradation_factor * (1.0 - abs(noise) / variation)
            else:
                quality = degradation_factor  # For sensors with no variation (like digital sensors)
            quality = max(0.0, min(1.0, quality))
        
        # Check for alarm conditions
        is_alarm = (value < sensor_config["alarm_low"] or 
                   value > sensor_config["alarm_high"]) and not is_faulty
        
        reading = SensorReading(
            sensor_id=sensor_id,
            sensor_type=sensor_config["type"],
            location=sensor_config["location"],
            timestamp=datetime.utcnow(),
            value=round(value, 3),
            unit=sensor_config["unit"],
            quality=round(quality, 3),
            alarm_threshold_low=sensor_config["alarm_low"],
            alarm_threshold_high=sensor_config["alarm_high"],
            is_alarm=is_alarm,
            is_faulty=is_faulty
        )
        
        self.sensor_readings_history.append(reading)
        return reading
    
    def generate_all_sensors(self) -> List[SensorReading]:
        """Generate readings for all sensors."""
        readings = []
        for sensor_id in self.sensors.keys():
            reading = self.generate_realistic_reading(sensor_id)
            readings.append(reading)
        return readings
    
    def simulate_emergency_scenario(self, scenario_type: str):
        """Simulate emergency scenarios affecting multiple sensors."""
        if scenario_type == "engine_room_fire":
            # Engine room fire affects multiple sensors
            self.sensors["TEMP_ER_001"]["base_value"] = 150.0  # High temperature
            self.sensors["TEMP_ER_002"]["base_value"] = 300.0  # Very high exhaust temp
            self.sensors["SMOKE_BR_001"]["base_value"] = 5.0   # Heavy smoke
            self.operational_mode = "emergency"
            
        elif scenario_type == "rough_weather":
            # Rough weather affects vibration and motion
            self.sea_state = 7  # Very rough seas
            self.weather_factor = 1.5
            for sensor_id in self.sensors:
                if self.sensors[sensor_id]["type"] == SensorType.VIBRATION:
                    self.sensors[sensor_id]["base_value"] *= 2.0
                    
        elif scenario_type == "normal_operations":
            # Reset to normal operations
            self._initialize_maritime_sensors()
            self.sea_state = 2
            self.weather_factor = 1.0
            self.operational_mode = "normal"
    
    def get_sensor_statistics(self) -> Dict:
        """Get statistical summary of sensor data."""
        if not self.sensor_readings_history:
            return {}
        
        stats = {
            "total_readings": len(self.sensor_readings_history),
            "time_span": {
                "start": min(r.timestamp for r in self.sensor_readings_history).isoformat(),
                "end": max(r.timestamp for r in self.sensor_readings_history).isoformat()
            },
            "sensor_health": {},
            "alarm_summary": {
                "total_alarms": sum(1 for r in self.sensor_readings_history if r.is_alarm),
                "faulty_sensors": sum(1 for r in self.sensor_readings_history if r.is_faulty),
                "average_quality": np.mean([r.quality for r in self.sensor_readings_history])
            }
        }
        
        # Per-sensor statistics
        for sensor_id in self.sensors:
            sensor_readings = [r for r in self.sensor_readings_history if r.sensor_id == sensor_id]
            if sensor_readings:
                values = [r.value for r in sensor_readings if not r.is_faulty]
                if values:
                    stats["sensor_health"][sensor_id] = {
                        "readings_count": len(sensor_readings),
                        "avg_value": np.mean(values),
                        "min_value": np.min(values),
                        "max_value": np.max(values),
                        "std_dev": np.std(values),
                        "alarm_rate": sum(1 for r in sensor_readings if r.is_alarm) / len(sensor_readings),
                        "quality_avg": np.mean([r.quality for r in sensor_readings])
                    }
        
        return stats

# Example usage and testing
async def main():
    """Test the maritime sensor data generator."""
    logger.info("🌊 Testing Maritime Sensor Data Generator")
    
    generator = MaritimeSensorGenerator()
    
    # Generate normal readings
    logger.info("📊 Generating normal operational readings...")
    for i in range(10):
        readings = generator.generate_all_sensors()
        logger.info(f"Generated {len(readings)} sensor readings")
        await asyncio.sleep(1)
    
    # Simulate emergency
    logger.info("🔥 Simulating engine room fire emergency...")
    generator.simulate_emergency_scenario("engine_room_fire")
    for i in range(5):
        readings = generator.generate_all_sensors()
        alarms = [r for r in readings if r.is_alarm]
        logger.warning(f"Emergency readings: {len(alarms)} alarms detected")
        await asyncio.sleep(1)
    
    # Return to normal
    logger.info("✅ Returning to normal operations...")
    generator.simulate_emergency_scenario("normal_operations")
    
    # Show statistics
    stats = generator.get_sensor_statistics()
    logger.info(f"📈 Sensor Statistics: {json.dumps(stats, indent=2, default=str)}")

if __name__ == "__main__":
    asyncio.run(main()) 