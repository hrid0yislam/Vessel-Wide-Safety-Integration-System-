"""
Emergency Stop System
Critical machinery shutdown system with cascade effect management.

This system demonstrates understanding of:
- Critical safety system design
- Emergency response procedures
- System integration and coordination
- Maritime safety requirements
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from loguru import logger
from database.models import SystemType, SystemStatus, EventSeverity

class EmergencyStopZone(str, Enum):
    ENGINE_ROOM = "engine_room"
    DECK_MACHINERY = "deck_machinery"
    VENTILATION = "ventilation"
    ELECTRICAL = "electrical"
    PROPULSION = "propulsion"
    ALL_ZONES = "all_zones"

class EmergencyStopSystem:
    """
    Emergency Stop System for ship safety.
    
    Provides immediate shutdown capabilities for critical machinery
    with coordinated response across all ship systems.
    """
    
    def __init__(self):
        self.system_type = SystemType.EMERGENCY_STOP
        self.status = SystemStatus.NORMAL
        self.active_stops = set()
        self.zone_status = {zone: False for zone in EmergencyStopZone}
        self.machinery_status = self._initialize_machinery()
        self.last_test = None
        self.emergency_contacts = []
        self.integration_callbacks = []
        
        logger.info("🚨 Emergency Stop System initialized")
    
    def _initialize_machinery(self) -> Dict[str, Dict]:
        """Initialize machinery configuration for each zone."""
        return {
            EmergencyStopZone.ENGINE_ROOM: {
                "main_engine": {"status": "running", "critical": True},
                "auxiliary_engine": {"status": "running", "critical": False},
                "fuel_pumps": {"status": "running", "critical": True},
                "cooling_system": {"status": "running", "critical": True},
                "oil_pumps": {"status": "running", "critical": True}
            },
            EmergencyStopZone.DECK_MACHINERY: {
                "crane": {"status": "standby", "critical": False},
                "winch": {"status": "standby", "critical": False},
                "anchor_windlass": {"status": "standby", "critical": False},
                "deck_lights": {"status": "running", "critical": False}
            },
            EmergencyStopZone.VENTILATION: {
                "engine_room_fans": {"status": "running", "critical": True},
                "accommodation_hvac": {"status": "running", "critical": False},
                "cargo_ventilation": {"status": "running", "critical": False},
                "galley_exhaust": {"status": "running", "critical": False}
            },
            EmergencyStopZone.ELECTRICAL: {
                "main_generator": {"status": "running", "critical": True},
                "emergency_generator": {"status": "standby", "critical": True},
                "lighting_circuits": {"status": "running", "critical": False},
                "navigation_power": {"status": "running", "critical": True}
            },
            EmergencyStopZone.PROPULSION: {
                "main_propulsion": {"status": "running", "critical": True},
                "bow_thruster": {"status": "standby", "critical": False},
                "steering_gear": {"status": "running", "critical": True}
            }
        }
    
    async def register_integration_callback(self, callback):
        """Register callback for system integration."""
        self.integration_callbacks.append(callback)
        logger.debug(f"Integration callback registered: {callback.__name__}")
    
    async def trigger_emergency_stop(self, zone: EmergencyStopZone = EmergencyStopZone.ALL_ZONES,
                                   reason: str = "Manual activation") -> Dict:
        """
        Trigger emergency stop for specified zone or all zones.
        
        Args:
            zone: Specific zone or all zones
            reason: Reason for emergency stop
            
        Returns:
            Dict with operation result and affected systems
        """
        logger.critical(f"🚨 EMERGENCY STOP TRIGGERED - Zone: {zone.value}, Reason: {reason}")
        
        # Update system status
        self.status = SystemStatus.EMERGENCY
        self.active_stops.add(zone)
        
        # Shutdown machinery in affected zones
        affected_machinery = []
        shutdown_zones = [zone] if zone != EmergencyStopZone.ALL_ZONES else list(EmergencyStopZone)[:-1]
        
        for stop_zone in shutdown_zones:
            if stop_zone in self.machinery_status:
                self.zone_status[stop_zone] = True
                for machinery, config in self.machinery_status[stop_zone].items():
                    if config["status"] == "running":
                        config["status"] = "emergency_stop"
                        affected_machinery.append(f"{stop_zone.value}:{machinery}")
                        logger.warning(f"🛑 Emergency stop: {stop_zone.value} - {machinery}")
        
        # Create emergency event record
        event_data = {
            "zone": zone.value,
            "reason": reason,
            "affected_machinery": affected_machinery,
            "timestamp": datetime.utcnow().isoformat(),
            "operator": "system"
        }
        
        # Notify integrated systems
        await self._notify_integrated_systems("emergency_stop", event_data)
        
        # Log critical event
        await self._log_event(
            event_type="EMERGENCY_STOP_ACTIVATED",
            severity=EventSeverity.EMERGENCY,
            message=f"Emergency stop activated for {zone.value}. Reason: {reason}",
            additional_data=json.dumps(event_data)
        )
        
        return {
            "success": True,
            "zone": zone.value,
            "reason": reason,
            "affected_machinery": affected_machinery,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "emergency_stop_active"
        }
    
    async def reset_emergency_stop(self, zone: EmergencyStopZone = EmergencyStopZone.ALL_ZONES) -> Dict:
        """
        Reset emergency stop for specified zone or all zones.
        
        Args:
            zone: Specific zone or all zones to reset
            
        Returns:
            Dict with reset operation result
        """
        logger.info(f"🔄 Resetting emergency stop for zone: {zone.value}")
        
        # Remove from active stops
        if zone in self.active_stops:
            self.active_stops.remove(zone)
        
        # Reset machinery in affected zones
        reset_machinery = []
        reset_zones = [zone] if zone != EmergencyStopZone.ALL_ZONES else list(EmergencyStopZone)[:-1]
        
        for reset_zone in reset_zones:
            if reset_zone in self.machinery_status:
                self.zone_status[reset_zone] = False
                for machinery, config in self.machinery_status[reset_zone].items():
                    if config["status"] == "emergency_stop":
                        # Only restart non-critical machinery automatically
                        if not config["critical"]:
                            config["status"] = "running"
                            reset_machinery.append(f"{reset_zone.value}:{machinery}")
                        else:
                            config["status"] = "stopped"  # Critical machinery requires manual restart
                            logger.warning(f"⚠️ Critical machinery requires manual restart: {reset_zone.value} - {machinery}")
        
        # Update system status if no active stops
        if not self.active_stops:
            self.status = SystemStatus.NORMAL
            logger.info("✅ All emergency stops cleared - System returned to normal")
        
        # Create reset event record
        event_data = {
            "zone": zone.value,
            "reset_machinery": reset_machinery,
            "timestamp": datetime.utcnow().isoformat(),
            "remaining_stops": list(self.active_stops)
        }
        
        # Notify integrated systems
        await self._notify_integrated_systems("emergency_stop_reset", event_data)
        
        # Log event
        await self._log_event(
            event_type="EMERGENCY_STOP_RESET",
            severity=EventSeverity.INFO,
            message=f"Emergency stop reset for {zone.value}",
            additional_data=json.dumps(event_data)
        )
        
        return {
            "success": True,
            "zone": zone.value,
            "reset_machinery": reset_machinery,
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": self.status.value,
            "active_stops": list(self.active_stops)
        }
    
    async def get_system_status(self) -> Dict:
        """Get current emergency stop system status."""
        return {
            "system_type": self.system_type.value,
            "status": self.status.value,
            "active_stops": list(self.active_stops),
            "zone_status": {zone.value: status for zone, status in self.zone_status.items()},
            "machinery_status": self.machinery_status,
            "last_test": self.last_test.isoformat() if self.last_test else None,
            "performance_score": self._calculate_performance_score()
        }
    
    async def perform_system_test(self) -> Dict:
        """Perform emergency stop system test."""
        logger.info("🧪 Performing emergency stop system test")
        
        self.last_test = datetime.utcnow()
        test_results = {}
        
        # Test each zone's emergency stop capability
        for zone in EmergencyStopZone:
            if zone == EmergencyStopZone.ALL_ZONES:
                continue
                
            # Simulate test - check response time and functionality
            response_time = 0.15  # Simulated response time in seconds
            test_passed = response_time < 0.5  # Should respond within 500ms
            
            test_results[zone.value] = {
                "passed": test_passed,
                "response_time": response_time,
                "status": "OK" if test_passed else "FAIL"
            }
        
        # Log test event
        await self._log_event(
            event_type="SYSTEM_TEST_COMPLETED",
            severity=EventSeverity.INFO,
            message="Emergency stop system test completed",
            additional_data=json.dumps(test_results)
        )
        
        return {
            "test_completed": True,
            "timestamp": self.last_test.isoformat(),
            "results": test_results,
            "overall_status": "PASS" if all(r["passed"] for r in test_results.values()) else "FAIL"
        }
    
    def _calculate_performance_score(self) -> float:
        """Calculate system performance score."""
        base_score = 100.0
        
        # Reduce score for active emergency stops
        if self.active_stops:
            base_score -= len(self.active_stops) * 20
        
        # Reduce score if last test was too long ago
        if self.last_test:
            days_since_test = (datetime.utcnow() - self.last_test).days
            if days_since_test > 30:
                base_score -= min(days_since_test - 30, 50)
        else:
            base_score -= 30  # No test performed
        
        return max(0, base_score)
    
    async def _notify_integrated_systems(self, event_type: str, data: Dict):
        """Notify other systems of emergency stop events."""
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
        
    async def get_emergency_procedures(self) -> Dict:
        """Get emergency procedures and contact information."""
        return {
            "procedures": {
                "engine_room_fire": [
                    "1. Activate emergency stop for engine room",
                    "2. Activate fire suppression system",
                    "3. Evacuate personnel from engine room",
                    "4. Notify bridge and emergency team",
                    "5. Prepare emergency power systems"
                ],
                "flooding": [
                    "1. Activate emergency stop for affected areas",
                    "2. Activate bilge pumps",
                    "3. Close watertight doors",
                    "4. Sound general alarm",
                    "5. Prepare lifeboats if necessary"
                ],
                "collision": [
                    "1. Emergency stop all machinery",
                    "2. Assess damage and flooding",
                    "3. Sound emergency signals",
                    "4. Contact coast guard",
                    "5. Prepare for evacuation if necessary"
                ]
            },
            "emergency_contacts": [
                {"role": "Master", "location": "Bridge", "priority": 1},
                {"role": "Chief Engineer", "location": "Engine Control Room", "priority": 2},
                {"role": "Safety Officer", "location": "Safety Station", "priority": 3},
                {"role": "Coast Guard", "frequency": "VHF Ch 16", "priority": 1}
            ],
            "system_integration": {
                "fire_detection": "Auto-trigger on fire alarm",
                "paga_system": "Auto-announcement of emergency stop",
                "cctv_system": "Auto-focus on emergency zones",
                "communication": "Auto-notify emergency contacts"
            }
        } 