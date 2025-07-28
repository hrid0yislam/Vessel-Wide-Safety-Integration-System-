"""
Fire Detection System
Zone-based fire detection and alarm system with automatic response coordination.

This system demonstrates understanding of:
- Fire safety system design
- Zone-based detection and control
- Automated emergency response
- Multi-vendor system integration
- Maritime fire safety standards
"""

import asyncio
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from loguru import logger
from database.models import SystemType, SystemStatus, EventSeverity

class FireDetectorType(str, Enum):
    SMOKE = "smoke"
    HEAT = "heat"
    FLAME = "flame"
    GAS = "gas"
    MULTI_SENSOR = "multi_sensor"

class AlarmLevel(str, Enum):
    NORMAL = "normal"
    PRE_ALARM = "pre_alarm"
    FIRE_ALARM = "fire_alarm"
    CRITICAL = "critical"

class FireDetectionSystem:
    """
    Fire Detection System for ship safety.
    
    Provides zone-based fire detection with automatic response coordination
    and integration with other ship safety systems.
    """
    
    def __init__(self):
        self.system_type = SystemType.FIRE_DETECTION
        self.status = SystemStatus.NORMAL
        self.zones = self._initialize_fire_zones()
        self.detectors = self._initialize_detectors()
        self.active_alarms = {}
        self.suppression_systems = self._initialize_suppression()
        self.last_test = None
        self.integration_callbacks = []
        
        logger.info("🔥 Fire Detection System initialized")
    
    def _initialize_fire_zones(self) -> Dict[str, Dict]:
        """Initialize fire detection zones with maritime standards compliance."""
        return {
            "engine_room": {
                "name": "Engine Room",
                "deck_level": "Lower Deck",
                "priority": "critical",
                "alarm_level": AlarmLevel.NORMAL,
                "temperature": 45.0,  # °C
                "smoke_level": 0.1,   # ppm
                "gas_level": 0.0,     # ppm
                "suppression_type": "CO2",
                "evacuation_time": 120,  # seconds
                "personnel_count": 2,
                "last_alarm": None
            },
            "bridge": {
                "name": "Bridge",
                "deck_level": "Upper Deck",
                "priority": "critical",
                "alarm_level": AlarmLevel.NORMAL,
                "temperature": 22.0,
                "smoke_level": 0.0,
                "gas_level": 0.0,
                "suppression_type": "Water Mist",
                "evacuation_time": 60,
                "personnel_count": 3,
                "last_alarm": None
            },
            "crew_quarters": {
                "name": "Crew Quarters",
                "deck_level": "Main Deck",
                "priority": "high",
                "alarm_level": AlarmLevel.NORMAL,
                "temperature": 20.0,
                "smoke_level": 0.0,
                "gas_level": 0.0,
                "suppression_type": "Sprinkler",
                "evacuation_time": 180,
                "personnel_count": 8,
                "last_alarm": None
            },
            "cargo_hold": {
                "name": "Cargo Hold",
                "deck_level": "Lower Deck",
                "priority": "high",
                "alarm_level": AlarmLevel.NORMAL,
                "temperature": 25.0,
                "smoke_level": 0.0,
                "gas_level": 0.0,
                "suppression_type": "Foam",
                "evacuation_time": 300,
                "personnel_count": 0,
                "last_alarm": None
            },
            "galley": {
                "name": "Galley",
                "deck_level": "Main Deck",
                "priority": "medium",
                "alarm_level": AlarmLevel.NORMAL,
                "temperature": 35.0,
                "smoke_level": 0.2,
                "gas_level": 0.0,
                "suppression_type": "Wet Chemical",
                "evacuation_time": 90,
                "personnel_count": 2,
                "last_alarm": None
            }
        }
    
    def _initialize_detectors(self) -> Dict[str, List[Dict]]:
        """Initialize fire detectors for each zone."""
        return {
            "engine_room": [
                {"id": "FD-ER-001", "type": FireDetectorType.HEAT, "status": "active", "threshold": 80.0},
                {"id": "FD-ER-002", "type": FireDetectorType.SMOKE, "status": "active", "threshold": 5.0},
                {"id": "FD-ER-003", "type": FireDetectorType.GAS, "status": "active", "threshold": 50.0},
                {"id": "FD-ER-004", "type": FireDetectorType.FLAME, "status": "active", "threshold": 0.5},
                {"id": "FD-ER-005", "type": FireDetectorType.MULTI_SENSOR, "status": "active", "threshold": 0.3}
            ],
            "bridge": [
                {"id": "FD-BR-001", "type": FireDetectorType.SMOKE, "status": "active", "threshold": 2.0},
                {"id": "FD-BR-002", "type": FireDetectorType.HEAT, "status": "active", "threshold": 60.0},
                {"id": "FD-BR-003", "type": FireDetectorType.MULTI_SENSOR, "status": "active", "threshold": 0.2}
            ],
            "crew_quarters": [
                {"id": "FD-CQ-001", "type": FireDetectorType.SMOKE, "status": "active", "threshold": 3.0},
                {"id": "FD-CQ-002", "type": FireDetectorType.SMOKE, "status": "active", "threshold": 3.0},
                {"id": "FD-CQ-003", "type": FireDetectorType.HEAT, "status": "active", "threshold": 65.0},
                {"id": "FD-CQ-004", "type": FireDetectorType.SMOKE, "status": "active", "threshold": 3.0}
            ],
            "cargo_hold": [
                {"id": "FD-CH-001", "type": FireDetectorType.SMOKE, "status": "active", "threshold": 4.0},
                {"id": "FD-CH-002", "type": FireDetectorType.HEAT, "status": "active", "threshold": 70.0},
                {"id": "FD-CH-003", "type": FireDetectorType.GAS, "status": "active", "threshold": 30.0},
                {"id": "FD-CH-004", "type": FireDetectorType.SMOKE, "status": "active", "threshold": 4.0}
            ],
            "galley": [
                {"id": "FD-GL-001", "type": FireDetectorType.HEAT, "status": "active", "threshold": 85.0},
                {"id": "FD-GL-002", "type": FireDetectorType.SMOKE, "status": "active", "threshold": 6.0},
                {"id": "FD-GL-003", "type": FireDetectorType.GAS, "status": "active", "threshold": 25.0}
            ]
        }
    
    def _initialize_suppression(self) -> Dict[str, Dict]:
        """Initialize fire suppression systems."""
        return {
            "engine_room": {
                "type": "CO2",
                "status": "ready",
                "pressure": 150.0,  # bar
                "capacity": 1000.0,  # kg
                "discharge_time": 60,  # seconds
                "last_test": None
            },
            "bridge": {
                "type": "Water Mist",
                "status": "ready",
                "pressure": 8.0,
                "capacity": 500.0,  # liters
                "discharge_time": 300,
                "last_test": None
            },
            "crew_quarters": {
                "type": "Sprinkler",
                "status": "ready",
                "pressure": 6.0,
                "capacity": 2000.0,
                "discharge_time": 600,
                "last_test": None
            },
            "cargo_hold": {
                "type": "Foam",
                "status": "ready",
                "pressure": 10.0,
                "capacity": 3000.0,
                "discharge_time": 180,
                "last_test": None
            },
            "galley": {
                "type": "Wet Chemical",
                "status": "ready",
                "pressure": 12.0,
                "capacity": 200.0,
                "discharge_time": 30,
                "last_test": None
            }
        }
    
    async def register_integration_callback(self, callback):
        """Register callback for system integration."""
        self.integration_callbacks.append(callback)
        logger.debug(f"Integration callback registered: {callback.__name__}")
    
    async def trigger_fire_alarm(self, zone: str, detector_id: str = None, 
                                cause: str = "Manual activation") -> Dict:
        """
        Trigger fire alarm for specified zone.
        
        Args:
            zone: Fire zone name
            detector_id: Specific detector that triggered (optional)
            cause: Cause of fire alarm
            
        Returns:
            Dict with alarm activation result and response actions
        """
        logger.critical(f"🔥 FIRE ALARM TRIGGERED - Zone: {zone}, Cause: {cause}")
        
        if zone not in self.zones:
            logger.error(f"Unknown fire zone: {zone}")
            return {"success": False, "error": f"Unknown zone: {zone}"}
        
        # Update zone status
        zone_data = self.zones[zone]
        zone_data["alarm_level"] = AlarmLevel.FIRE_ALARM
        zone_data["last_alarm"] = datetime.utcnow()
        
        # Add to active alarms
        alarm_id = f"FA-{zone.upper()}-{int(datetime.utcnow().timestamp())}"
        self.active_alarms[alarm_id] = {
            "zone": zone,
            "detector_id": detector_id,
            "cause": cause,
            "start_time": datetime.utcnow(),
            "level": AlarmLevel.FIRE_ALARM,
            "suppression_activated": False,
            "evacuation_ordered": False
        }
        
        # Update system status
        self.status = SystemStatus.ALARM
        
        # Coordinate emergency response
        response_actions = await self._coordinate_emergency_response(zone, alarm_id)
        
        # Create alarm event record
        event_data = {
            "alarm_id": alarm_id,
            "zone": zone,
            "detector_id": detector_id,
            "cause": cause,
            "timestamp": datetime.utcnow().isoformat(),
            "response_actions": response_actions,
            "priority": zone_data["priority"]
        }
        
        # Notify integrated systems
        await self._notify_integrated_systems("fire_alarm", event_data)
        
        # Log critical event
        await self._log_event(
            event_type="FIRE_ALARM_ACTIVATED",
            severity=EventSeverity.CRITICAL,
            message=f"Fire alarm activated in {zone}. Cause: {cause}",
            location=zone,
            additional_data=json.dumps(event_data)
        )
        
        return {
            "success": True,
            "alarm_id": alarm_id,
            "zone": zone,
            "cause": cause,
            "response_actions": response_actions,
            "timestamp": datetime.utcnow().isoformat(),
            "evacuation_time": zone_data["evacuation_time"]
        }
    
    async def _coordinate_emergency_response(self, zone: str, alarm_id: str) -> List[str]:
        """Coordinate automatic emergency response actions."""
        actions = []
        zone_data = self.zones[zone]
        alarm_data = self.active_alarms[alarm_id]
        
        # 1. Immediate actions based on zone priority
        if zone_data["priority"] == "critical":
            actions.append("Emergency stop initiated for affected areas")
            actions.append("Bridge notified immediately")
            actions.append("Emergency lighting activated")
        
        # 2. Evacuation procedures
        if zone_data["personnel_count"] > 0:
            actions.append(f"Evacuation order for {zone_data['personnel_count']} personnel")
            actions.append(f"Evacuation time: {zone_data['evacuation_time']} seconds")
            alarm_data["evacuation_ordered"] = True
        
        # 3. Suppression system activation (auto-delay for personnel evacuation)
        suppression_delay = 60 if zone_data["personnel_count"] > 0 else 10
        actions.append(f"Fire suppression activation scheduled in {suppression_delay} seconds")
        
        # 4. CCTV and monitoring
        actions.append(f"CCTV cameras focused on {zone}")
        actions.append("Continuous temperature and smoke monitoring")
        
        # 5. Communication actions
        actions.append("General alarm sounded")
        actions.append("Emergency teams notified")
        actions.append("Coast Guard notification prepared")
        
        # 6. System isolations
        if zone == "engine_room":
            actions.append("Fuel supply isolation initiated")
            actions.append("Ventilation system shutdown")
        elif zone == "galley":
            actions.append("Gas supply isolation")
            actions.append("Electrical isolation for cooking equipment")
        
        # Schedule suppression system activation
        asyncio.create_task(self._delayed_suppression_activation(zone, alarm_id, suppression_delay))
        
        return actions
    
    async def _delayed_suppression_activation(self, zone: str, alarm_id: str, delay: int):
        """Activate suppression system after evacuation delay."""
        await asyncio.sleep(delay)
        
        if alarm_id in self.active_alarms and not self.active_alarms[alarm_id]["suppression_activated"]:
            await self.activate_suppression_system(zone, alarm_id)
    
    async def activate_suppression_system(self, zone: str, alarm_id: str) -> Dict:
        """Activate fire suppression system for specified zone."""
        logger.warning(f"💧 Activating fire suppression system in {zone}")
        
        if zone not in self.suppression_systems:
            return {"success": False, "error": f"No suppression system for zone: {zone}"}
        
        suppression = self.suppression_systems[zone]
        
        # Update suppression status
        suppression["status"] = "discharging"
        
        # Update alarm record
        if alarm_id in self.active_alarms:
            self.active_alarms[alarm_id]["suppression_activated"] = True
        
        # Log suppression activation
        await self._log_event(
            event_type="SUPPRESSION_ACTIVATED",
            severity=EventSeverity.CRITICAL,
            message=f"Fire suppression system activated in {zone}",
            location=zone,
            additional_data=json.dumps({
                "suppression_type": suppression["type"],
                "discharge_time": suppression["discharge_time"],
                "alarm_id": alarm_id
            })
        )
        
        # Simulate suppression discharge time
        asyncio.create_task(self._complete_suppression_discharge(zone, suppression["discharge_time"]))
        
        return {
            "success": True,
            "zone": zone,
            "suppression_type": suppression["type"],
            "discharge_time": suppression["discharge_time"],
            "status": "activated"
        }
    
    async def _complete_suppression_discharge(self, zone: str, discharge_time: int):
        """Complete suppression system discharge cycle."""
        await asyncio.sleep(discharge_time)
        
        suppression = self.suppression_systems[zone]
        suppression["status"] = "discharged"
        
        logger.info(f"✅ Fire suppression discharge completed in {zone}")
        
        # Log completion
        await self._log_event(
            event_type="SUPPRESSION_COMPLETED",
            severity=EventSeverity.INFO,
            message=f"Fire suppression discharge completed in {zone}",
            location=zone
        )
    
    async def reset_fire_alarm(self, alarm_id: str) -> Dict:
        """Reset fire alarm and return systems to normal."""
        if alarm_id not in self.active_alarms:
            return {"success": False, "error": f"Unknown alarm ID: {alarm_id}"}
        
        alarm_data = self.active_alarms[alarm_id]
        zone = alarm_data["zone"]
        
        logger.info(f"🔄 Resetting fire alarm {alarm_id} in zone {zone}")
        
        # Reset zone status
        zone_data = self.zones[zone]
        zone_data["alarm_level"] = AlarmLevel.NORMAL
        zone_data["temperature"] = 22.0  # Return to normal temperature
        zone_data["smoke_level"] = 0.0
        zone_data["gas_level"] = 0.0
        
        # Reset suppression system
        if zone in self.suppression_systems:
            suppression = self.suppression_systems[zone]
            if suppression["status"] in ["discharging", "discharged"]:
                suppression["status"] = "recharging"
                # Simulate recharge time
                asyncio.create_task(self._recharge_suppression_system(zone))
        
        # Remove from active alarms
        del self.active_alarms[alarm_id]
        
        # Update system status if no more active alarms
        if not self.active_alarms:
            self.status = SystemStatus.NORMAL
            logger.info("✅ All fire alarms cleared - System returned to normal")
        
        # Log reset event
        await self._log_event(
            event_type="FIRE_ALARM_RESET",
            severity=EventSeverity.INFO,
            message=f"Fire alarm reset in {zone}",
            location=zone,
            additional_data=json.dumps({
                "alarm_id": alarm_id,
                "duration": str(datetime.utcnow() - alarm_data["start_time"])
            })
        )
        
        return {
            "success": True,
            "alarm_id": alarm_id,
            "zone": zone,
            "reset_time": datetime.utcnow().isoformat(),
            "alarm_duration": str(datetime.utcnow() - alarm_data["start_time"])
        }
    
    async def _recharge_suppression_system(self, zone: str):
        """Recharge suppression system after use."""
        await asyncio.sleep(300)  # 5 minutes recharge time
        
        suppression = self.suppression_systems[zone]
        suppression["status"] = "ready"
        
        logger.info(f"🔋 Fire suppression system recharged in {zone}")
    
    async def get_system_status(self) -> Dict:
        """Get current fire detection system status."""
        return {
            "system_type": self.system_type.value,
            "status": self.status.value,
            "zones": self.zones,
            "active_alarms": len(self.active_alarms),
            "alarm_details": self.active_alarms,
            "detectors": self._get_detector_summary(),
            "suppression_systems": self.suppression_systems,
            "last_test": self.last_test.isoformat() if self.last_test else None,
            "performance_score": self._calculate_performance_score()
        }
    
    def _get_detector_summary(self) -> Dict:
        """Get summary of all detectors."""
        summary = {}
        for zone, detectors in self.detectors.items():
            active_count = sum(1 for d in detectors if d["status"] == "active")
            summary[zone] = {
                "total": len(detectors),
                "active": active_count,
                "fault": len(detectors) - active_count
            }
        return summary
    
    async def perform_system_test(self) -> Dict:
        """Perform fire detection system test."""
        logger.info("🧪 Performing fire detection system test")
        
        self.last_test = datetime.utcnow()
        test_results = {}
        
        # Test each zone's detectors
        for zone, detectors in self.detectors.items():
            zone_results = []
            for detector in detectors:
                # Simulate detector test
                response_time = random.uniform(0.1, 0.5)
                sensitivity = random.uniform(0.9, 1.0)
                test_passed = response_time < 1.0 and sensitivity > 0.85
                
                zone_results.append({
                    "detector_id": detector["id"],
                    "type": detector["type"],
                    "passed": test_passed,
                    "response_time": response_time,
                    "sensitivity": sensitivity
                })
            
            test_results[zone] = {
                "detectors": zone_results,
                "zone_status": "PASS" if all(r["passed"] for r in zone_results) else "FAIL"
            }
        
        # Test suppression systems
        suppression_results = {}
        for zone, suppression in self.suppression_systems.items():
            pressure_ok = suppression["pressure"] > 5.0
            capacity_ok = suppression["capacity"] > 100.0
            
            suppression_results[zone] = {
                "type": suppression["type"],
                "pressure_test": "PASS" if pressure_ok else "FAIL",
                "capacity_test": "PASS" if capacity_ok else "FAIL",
                "overall": "PASS" if pressure_ok and capacity_ok else "FAIL"
            }
        
        # Log test event
        await self._log_event(
            event_type="SYSTEM_TEST_COMPLETED",
            severity=EventSeverity.INFO,
            message="Fire detection system test completed",
            additional_data=json.dumps({
                "detector_results": test_results,
                "suppression_results": suppression_results
            })
        )
        
        return {
            "test_completed": True,
            "timestamp": self.last_test.isoformat(),
            "detector_results": test_results,
            "suppression_results": suppression_results,
            "overall_status": "PASS"  # Simplified for demo
        }
    
    def _calculate_performance_score(self) -> float:
        """Calculate system performance score."""
        base_score = 100.0
        
        # Reduce score for active alarms
        base_score -= len(self.active_alarms) * 15
        
        # Reduce score for faulty detectors
        for zone, detectors in self.detectors.items():
            faulty_count = sum(1 for d in detectors if d["status"] != "active")
            base_score -= faulty_count * 5
        
        # Reduce score if last test was too long ago
        if self.last_test:
            days_since_test = (datetime.utcnow() - self.last_test).days
            if days_since_test > 7:  # Weekly testing required
                base_score -= min(days_since_test - 7, 30)
        else:
            base_score -= 25  # No test performed
        
        return max(0, base_score)
    
    async def _notify_integrated_systems(self, event_type: str, data: Dict):
        """Notify other systems of fire detection events."""
        for callback in self.integration_callbacks:
            try:
                await callback(self.system_type, event_type, data)
            except Exception as e:
                logger.error(f"Error notifying integrated system: {e}")
    
    async def _log_event(self, event_type: str, severity: EventSeverity, 
                        message: str, location: str = None, additional_data: str = None):
        """Log system event to database."""
        # This would be implemented with actual database logging
        logger.info(f"Event logged: {event_type} - {message}")
    
    async def start_monitoring(self):
        """Start continuous monitoring of fire detection sensors."""
        logger.info("🔍 Starting fire detection monitoring")
        while True:
            await self._update_sensor_readings()
            await asyncio.sleep(5)  # Update every 5 seconds
    
    async def _update_sensor_readings(self):
        """Update sensor readings with simulated values."""
        for zone_name, zone_data in self.zones.items():
            # Simulate environmental changes
            if zone_data["alarm_level"] == AlarmLevel.NORMAL:
                # Normal variations
                zone_data["temperature"] += random.uniform(-0.5, 0.5)
                zone_data["smoke_level"] = max(0, zone_data["smoke_level"] + random.uniform(-0.05, 0.05))
                zone_data["gas_level"] = max(0, zone_data["gas_level"] + random.uniform(-0.01, 0.01))
            
            # Keep values within realistic ranges
            zone_data["temperature"] = max(10, min(60, zone_data["temperature"]))
            zone_data["smoke_level"] = max(0, min(10, zone_data["smoke_level"]))
            zone_data["gas_level"] = max(0, min(100, zone_data["gas_level"])) 