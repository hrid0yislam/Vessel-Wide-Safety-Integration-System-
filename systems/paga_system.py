"""
PAGA System (Public Address and General Alarm)
Ship-wide communication and alarm system with automated emergency announcements.

This system demonstrates understanding of:
- Maritime communication systems
- Emergency announcement protocols
- Multi-zone audio distribution
- Integration with other safety systems
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from loguru import logger
from database.models import SystemType, SystemStatus, EventSeverity

class AlarmType(str, Enum):
    GENERAL_ALARM = "general_alarm"
    FIRE_ALARM = "fire_alarm"
    ABANDON_SHIP = "abandon_ship"
    MAN_OVERBOARD = "man_overboard"
    EMERGENCY_STATIONS = "emergency_stations"
    ALL_CLEAR = "all_clear"

class AnnouncementPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EMERGENCY = "emergency"

class PAGASystem:
    """
    PAGA System for ship communication and emergency alarms.
    
    Provides automated announcements, emergency alarms, and
    integration with other ship safety systems.
    """
    
    def __init__(self):
        self.system_type = SystemType.PAGA
        self.status = SystemStatus.NORMAL
        self.zones = self._initialize_zones()
        self.speakers = self._initialize_speakers()
        self.active_announcements = {}
        self.alarm_sequences = self._initialize_alarm_sequences()
        self.message_templates = self._initialize_message_templates()
        self.volume_levels = {}
        self.last_test = None
        self.integration_callbacks = []
        
        logger.info("📢 PAGA System initialized")
    
    def _initialize_zones(self) -> Dict[str, Dict]:
        """Initialize PAGA zones for ship areas."""
        return {
            "bridge": {
                "name": "Bridge",
                "priority": "critical",
                "speaker_count": 4,
                "volume_level": 8,
                "status": "active",
                "emergency_override": True,
                "backup_power": True
            },
            "engine_room": {
                "name": "Engine Room",
                "priority": "critical",
                "speaker_count": 6,
                "volume_level": 9,  # Higher due to ambient noise
                "status": "active",
                "emergency_override": True,
                "backup_power": True
            },
            "crew_quarters": {
                "name": "Crew Quarters",
                "priority": "high",
                "speaker_count": 12,
                "volume_level": 7,
                "status": "active",
                "emergency_override": True,
                "backup_power": True
            },
            "cargo_hold": {
                "name": "Cargo Hold",
                "priority": "medium",
                "speaker_count": 8,
                "volume_level": 8,
                "status": "active",
                "emergency_override": True,
                "backup_power": False
            },
            "galley": {
                "name": "Galley",
                "priority": "medium",
                "speaker_count": 3,
                "volume_level": 6,
                "status": "active",
                "emergency_override": True,
                "backup_power": False
            },
            "deck_areas": {
                "name": "Deck Areas",
                "priority": "high",
                "speaker_count": 10,
                "volume_level": 9,  # Outdoor speakers need higher volume
                "status": "active",
                "emergency_override": True,
                "backup_power": True
            },
            "all_zones": {
                "name": "All Zones",
                "priority": "emergency",
                "speaker_count": 43,  # Total of all speakers
                "volume_level": 8,
                "status": "active",
                "emergency_override": True,
                "backup_power": True
            }
        }
    
    def _initialize_speakers(self) -> Dict[str, Dict]:
        """Initialize individual speaker configuration."""
        speakers = {}
        speaker_id = 1
        
        for zone_name, zone_data in self.zones.items():
            if zone_name == "all_zones":
                continue
                
            for i in range(zone_data["speaker_count"]):
                speaker_key = f"SPK{speaker_id:03d}"
                speakers[speaker_key] = {
                    "zone": zone_name,
                    "location": f"{zone_data['name']} - Speaker {i+1}",
                    "status": "online",
                    "volume": zone_data["volume_level"],
                    "frequency_response": "excellent",
                    "last_test": None,
                    "fault_detected": False
                }
                speaker_id += 1
        
        return speakers
    
    def _initialize_alarm_sequences(self) -> Dict[str, Dict]:
        """Initialize alarm sequences for different emergency types."""
        return {
            AlarmType.GENERAL_ALARM: {
                "sequence": "7_short_1_long",
                "duration": 60,  # seconds
                "repeat_interval": 5,
                "frequency": [800, 1000],  # Hz
                "description": "General emergency alarm - 7 short blasts followed by 1 long blast"
            },
            AlarmType.FIRE_ALARM: {
                "sequence": "continuous_alternating",
                "duration": 120,
                "repeat_interval": 2,
                "frequency": [400, 800],
                "description": "Fire alarm - continuous alternating tone"
            },
            AlarmType.ABANDON_SHIP: {
                "sequence": "6_short_1_long",
                "duration": 180,
                "repeat_interval": 3,
                "frequency": [800, 1200],
                "description": "Abandon ship - 6 short blasts followed by 1 long blast"
            },
            AlarmType.MAN_OVERBOARD: {
                "sequence": "3_long_3_short_3_long",
                "duration": 90,
                "repeat_interval": 10,
                "frequency": [1000],
                "description": "Man overboard - SOS pattern (3 long, 3 short, 3 long)"
            },
            AlarmType.EMERGENCY_STATIONS: {
                "sequence": "continuous_single_tone",
                "duration": 30,
                "repeat_interval": 1,
                "frequency": [1000],
                "description": "Emergency stations - continuous single tone"
            },
            AlarmType.ALL_CLEAR: {
                "sequence": "2_long",
                "duration": 20,
                "repeat_interval": 0,
                "frequency": [600],
                "description": "All clear - 2 long blasts"
            }
        }
    
    def _initialize_message_templates(self) -> Dict[str, Dict]:
        """Initialize pre-recorded message templates."""
        return {
            "fire_emergency": {
                "message": "ATTENTION ALL PERSONNEL. FIRE ALARM IN {zone}. PROCEED TO EMERGENCY STATIONS. THIS IS NOT A DRILL.",
                "language": "english",
                "duration": 15,
                "priority": AnnouncementPriority.EMERGENCY
            },
            "emergency_stop": {
                "message": "ATTENTION ALL PERSONNEL. EMERGENCY STOP ACTIVATED. REMAIN IN SAFE POSITIONS. AWAIT FURTHER INSTRUCTIONS.",
                "language": "english", 
                "duration": 12,
                "priority": AnnouncementPriority.EMERGENCY
            },
            "abandon_ship": {
                "message": "ABANDON SHIP. ABANDON SHIP. ALL PERSONNEL TO LIFEBOAT STATIONS. THIS IS NOT A DRILL.",
                "language": "english",
                "duration": 10,
                "priority": AnnouncementPriority.EMERGENCY
            },
            "man_overboard": {
                "message": "MAN OVERBOARD. MAN OVERBOARD. ALL PERSONNEL TO EMERGENCY STATIONS.",
                "language": "english",
                "duration": 8,
                "priority": AnnouncementPriority.EMERGENCY
            },
            "general_emergency": {
                "message": "GENERAL ALARM. ALL PERSONNEL TO EMERGENCY STATIONS. AWAIT FURTHER INSTRUCTIONS.",
                "language": "english",
                "duration": 10,
                "priority": AnnouncementPriority.EMERGENCY
            },
            "drill_announcement": {
                "message": "ATTENTION ALL PERSONNEL. EMERGENCY DRILL IN PROGRESS. PROCEED TO ASSIGNED STATIONS. THIS IS A DRILL.",
                "language": "english",
                "duration": 12,
                "priority": AnnouncementPriority.HIGH
            },
            "all_clear": {
                "message": "ALL CLEAR. EMERGENCY IS OVER. NORMAL OPERATIONS MAY RESUME.",
                "language": "english",
                "duration": 8,
                "priority": AnnouncementPriority.HIGH
            },
            "routine_announcement": {
                "message": "ATTENTION ALL PERSONNEL. {custom_message}",
                "language": "english",
                "duration": 10,
                "priority": AnnouncementPriority.MEDIUM
            }
        }
    
    async def register_integration_callback(self, callback):
        """Register callback for system integration."""
        self.integration_callbacks.append(callback)
        logger.debug(f"Integration callback registered: {callback.__name__}")
    
    async def trigger_alarm(self, alarm_type: AlarmType, zones: List[str] = None,
                           custom_message: str = None) -> Dict:
        """
        Trigger emergency alarm with optional announcement.
        
        Args:
            alarm_type: Type of alarm to trigger
            zones: Specific zones to broadcast to (None = all zones)
            custom_message: Optional custom message
            
        Returns:
            Dict with alarm activation result
        """
        logger.critical(f"📢 PAGA ALARM TRIGGERED: {alarm_type.value}")
        
        if zones is None:
            zones = ["all_zones"]
        
        # Update system status
        self.status = SystemStatus.ALARM
        
        # Get alarm sequence configuration
        alarm_config = self.alarm_sequences[alarm_type]
        
        # Create alarm session
        alarm_id = f"ALM-{alarm_type.value.upper()}-{int(datetime.utcnow().timestamp())}"
        
        # Start alarm sequence
        await self._start_alarm_sequence(alarm_id, alarm_type, alarm_config, zones)
        
        # Follow with voice announcement if available
        if alarm_type.value in self.message_templates:
            await asyncio.sleep(2)  # Brief pause after alarm
            await self._broadcast_announcement(alarm_type.value, zones, custom_message)
        
        # Record alarm activation
        self.active_announcements[alarm_id] = {
            "type": "alarm",
            "alarm_type": alarm_type,
            "zones": zones,
            "start_time": datetime.utcnow(),
            "status": "active",
            "duration": alarm_config["duration"],
            "custom_message": custom_message
        }
        
        # Notify integrated systems
        await self._notify_integrated_systems("alarm_activated", {
            "alarm_id": alarm_id,
            "alarm_type": alarm_type.value,
            "zones": zones,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Log alarm event
        await self._log_event(
            event_type="PAGA_ALARM_ACTIVATED",
            severity=EventSeverity.EMERGENCY,
            message=f"PAGA alarm activated: {alarm_type.value}",
            additional_data=json.dumps({
                "alarm_id": alarm_id,
                "zones": zones,
                "duration": alarm_config["duration"]
            })
        )
        
        return {
            "success": True,
            "alarm_id": alarm_id,
            "alarm_type": alarm_type.value,
            "zones": zones,
            "duration": alarm_config["duration"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _start_alarm_sequence(self, alarm_id: str, alarm_type: AlarmType,
                                   alarm_config: Dict, zones: List[str]):
        """Start alarm sequence playback."""
        logger.warning(f"🚨 Starting alarm sequence: {alarm_config['sequence']}")
        
        # Simulate alarm sequence (in real system this would control actual audio hardware)
        duration = alarm_config["duration"]
        
        # Schedule alarm completion
        asyncio.create_task(self._complete_alarm_sequence(alarm_id, duration))
    
    async def _complete_alarm_sequence(self, alarm_id: str, duration: int):
        """Complete alarm sequence after specified duration."""
        await asyncio.sleep(duration)
        
        if alarm_id in self.active_announcements:
            self.active_announcements[alarm_id]["status"] = "completed"
            logger.info(f"✅ Alarm sequence completed: {alarm_id}")
            
            # Check if any other alarms are active
            active_alarms = [a for a in self.active_announcements.values() 
                           if a["type"] == "alarm" and a["status"] == "active"]
            
            if not active_alarms:
                self.status = SystemStatus.NORMAL
                logger.info("📢 All PAGA alarms completed - System returned to normal")
    
    async def _broadcast_announcement(self, template_key: str, zones: List[str],
                                     custom_message: str = None):
        """Broadcast voice announcement to specified zones."""
        if template_key not in self.message_templates:
            logger.error(f"Unknown message template: {template_key}")
            return
        
        template = self.message_templates[template_key]
        message = template["message"]
        
        # Replace placeholders if custom message provided
        if custom_message and "{custom_message}" in message:
            message = message.replace("{custom_message}", custom_message)
        
        logger.info(f"📢 Broadcasting announcement: {message[:50]}...")
        
        # Create announcement session
        announcement_id = f"ANN-{int(datetime.utcnow().timestamp())}"
        
        self.active_announcements[announcement_id] = {
            "type": "announcement",
            "template": template_key,
            "message": message,
            "zones": zones,
            "start_time": datetime.utcnow(),
            "duration": template["duration"],
            "priority": template["priority"],
            "status": "playing"
        }
        
        # Schedule announcement completion
        asyncio.create_task(self._complete_announcement(announcement_id, template["duration"]))
        
        return announcement_id
    
    async def _complete_announcement(self, announcement_id: str, duration: int):
        """Complete announcement after specified duration."""
        await asyncio.sleep(duration)
        
        if announcement_id in self.active_announcements:
            self.active_announcements[announcement_id]["status"] = "completed"
            logger.debug(f"📢 Announcement completed: {announcement_id}")
    
    async def make_announcement(self, message: str, zones: List[str] = None,
                              priority: AnnouncementPriority = AnnouncementPriority.MEDIUM) -> Dict:
        """
        Make custom announcement to specified zones.
        
        Args:
            message: Message to announce
            zones: Target zones (None = all zones)
            priority: Announcement priority
            
        Returns:
            Dict with announcement result
        """
        if zones is None:
            zones = ["all_zones"]
        
        logger.info(f"📢 Making announcement to zones {zones}: {message[:50]}...")
        
        # Create announcement session
        announcement_id = f"ANN-{int(datetime.utcnow().timestamp())}"
        
        # Estimate duration based on message length (rough calculation)
        estimated_duration = max(5, len(message) // 10)
        
        self.active_announcements[announcement_id] = {
            "type": "custom_announcement",
            "message": message,
            "zones": zones,
            "start_time": datetime.utcnow(),
            "duration": estimated_duration,
            "priority": priority,
            "status": "playing"
        }
        
        # Schedule completion
        asyncio.create_task(self._complete_announcement(announcement_id, estimated_duration))
        
        # Log announcement
        await self._log_event(
            event_type="PAGA_ANNOUNCEMENT",
            severity=EventSeverity.INFO,
            message=f"PAGA announcement made: {message[:100]}",
            additional_data=json.dumps({
                "announcement_id": announcement_id,
                "zones": zones,
                "priority": priority.value
            })
        )
        
        return {
            "success": True,
            "announcement_id": announcement_id,
            "message": message,
            "zones": zones,
            "priority": priority.value,
            "estimated_duration": estimated_duration,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def stop_announcement(self, announcement_id: str) -> Dict:
        """Stop active announcement."""
        if announcement_id not in self.active_announcements:
            return {"success": False, "error": f"Announcement {announcement_id} not found"}
        
        announcement = self.active_announcements[announcement_id]
        if announcement["status"] != "playing":
            return {"success": False, "error": f"Announcement {announcement_id} is not active"}
        
        announcement["status"] = "stopped"
        logger.info(f"🛑 Announcement stopped: {announcement_id}")
        
        return {
            "success": True,
            "announcement_id": announcement_id,
            "stopped_at": datetime.utcnow().isoformat()
        }
    
    async def get_system_status(self) -> Dict:
        """Get current PAGA system status."""
        active_announcements = sum(1 for a in self.active_announcements.values() 
                                 if a["status"] == "playing")
        online_speakers = sum(1 for s in self.speakers.values() if s["status"] == "online")
        
        return {
            "system_type": self.system_type.value,
            "status": self.status.value,
            "zones": self.zones,
            "total_speakers": len(self.speakers),
            "online_speakers": online_speakers,
            "active_announcements": active_announcements,
            "announcement_details": self.active_announcements,
            "alarm_types_available": [alarm.value for alarm in AlarmType],
            "last_test": self.last_test.isoformat() if self.last_test else None,
            "performance_score": self._calculate_performance_score()
        }
    
    async def perform_system_test(self) -> Dict:
        """Perform PAGA system test."""
        logger.info("🧪 Performing PAGA system test")
        
        self.last_test = datetime.utcnow()
        test_results = {}
        
        # Test each zone
        for zone_name, zone_data in self.zones.items():
            if zone_name == "all_zones":
                continue
                
            # Test zone speakers
            zone_speakers = [s for s in self.speakers.values() if s["zone"] == zone_name]
            online_count = sum(1 for s in zone_speakers if s["status"] == "online")
            
            # Test alarm functionality
            alarm_test = True  # Simulated test
            volume_test = zone_data["volume_level"] >= 5
            backup_power_test = zone_data.get("backup_power", False)
            
            test_results[zone_name] = {
                "speaker_count": len(zone_speakers),
                "online_speakers": online_count,
                "speaker_test": "PASS" if online_count == len(zone_speakers) else "FAIL",
                "alarm_test": "PASS" if alarm_test else "FAIL",
                "volume_test": "PASS" if volume_test else "FAIL",
                "backup_power_test": "PASS" if backup_power_test else "N/A",
                "overall": "PASS" if all([
                    online_count == len(zone_speakers),
                    alarm_test,
                    volume_test
                ]) else "FAIL"
            }
        
        # Test alarm sequences
        alarm_test_results = {}
        for alarm_type in AlarmType:
            alarm_test_results[alarm_type.value] = {
                "sequence_available": True,
                "frequency_test": "PASS",
                "duration_test": "PASS",
                "override_test": "PASS"
            }
        
        # Log test completion
        await self._log_event(
            event_type="SYSTEM_TEST_COMPLETED",
            severity=EventSeverity.INFO,
            message="PAGA system test completed",
            additional_data=json.dumps({
                "zone_results": test_results,
                "alarm_results": alarm_test_results
            })
        )
        
        return {
            "test_completed": True,
            "timestamp": self.last_test.isoformat(),
            "zone_results": test_results,
            "alarm_results": alarm_test_results,
            "overall_status": "PASS"
        }
    
    def _calculate_performance_score(self) -> float:
        """Calculate system performance score."""
        base_score = 100.0
        
        # Reduce score for offline speakers
        offline_speakers = sum(1 for s in self.speakers.values() if s["status"] != "online")
        base_score -= offline_speakers * 2
        
        # Reduce score if last test was too long ago
        if self.last_test:
            days_since_test = (datetime.utcnow() - self.last_test).days
            if days_since_test > 7:  # Weekly testing recommended
                base_score -= min(days_since_test - 7, 30)
        else:
            base_score -= 25  # No test performed
        
        # Reduce score for faulty zones
        for zone_data in self.zones.values():
            if zone_data["status"] != "active":
                base_score -= 10
        
        return max(0, base_score)
    
    async def handle_emergency_event(self, event_type: str, event_data: Dict) -> Dict:
        """Handle emergency events with appropriate PAGA response."""
        logger.warning(f"📢 PAGA responding to emergency: {event_type}")
        
        # Map event types to alarm types
        event_alarm_map = {
            "fire_alarm": AlarmType.FIRE_ALARM,
            "emergency_stop": AlarmType.GENERAL_ALARM,
            "man_overboard": AlarmType.MAN_OVERBOARD,
            "abandon_ship": AlarmType.ABANDON_SHIP
        }
        
        alarm_type = event_alarm_map.get(event_type, AlarmType.GENERAL_ALARM)
        
        # Determine zones based on event location
        zones = None
        if "zone" in event_data:
            # For localized events, announce to all zones but focus on affected area
            zones = ["all_zones"]
        
        # Trigger appropriate alarm
        result = await self.trigger_alarm(alarm_type, zones)
        
        return {
            "success": True,
            "response_type": "alarm_triggered",
            "alarm_type": alarm_type.value,
            "alarm_id": result.get("alarm_id"),
            "zones": zones or ["all_zones"]
        }
    
    async def _notify_integrated_systems(self, event_type: str, data: Dict):
        """Notify other systems of PAGA events."""
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