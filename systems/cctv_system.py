"""
CCTV System
Security and monitoring camera network with intelligent event-driven focus.

This system demonstrates understanding of:
- Security system integration
- Event-driven camera control
- Maritime monitoring requirements
- Multi-vendor camera system coordination
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from loguru import logger
from database.models import SystemType, SystemStatus, EventSeverity

class CameraStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    FAULT = "fault"

class RecordingMode(str, Enum):
    CONTINUOUS = "continuous"
    EVENT_BASED = "event_based"
    MOTION_DETECTION = "motion_detection"
    MANUAL = "manual"

class CCTVSystem:
    """
    CCTV System for ship security and monitoring.
    
    Provides intelligent camera management with automatic focus
    on emergency events and integration with other safety systems.
    """
    
    def __init__(self):
        self.system_type = SystemType.CCTV
        self.status = SystemStatus.NORMAL
        self.cameras = self._initialize_cameras()
        self.recording_sessions = {}
        self.event_presets = self._initialize_event_presets()
        self.storage_usage = 65.0  # Percentage
        self.last_maintenance = None
        self.integration_callbacks = []
        
        logger.info("📹 CCTV System initialized")
    
    def _initialize_cameras(self) -> Dict[str, Dict]:
        """Initialize camera configuration for ship monitoring."""
        return {
            "CAM001": {
                "name": "Bridge Main View",
                "location": "Bridge",
                "zone": "bridge",
                "type": "PTZ",  # Pan-Tilt-Zoom
                "status": CameraStatus.ONLINE,
                "recording": RecordingMode.CONTINUOUS,
                "resolution": "4K",
                "night_vision": True,
                "audio": True,
                "current_preset": "normal_view",
                "pan": 0,
                "tilt": 0,
                "zoom": 1.0,
                "storage_days": 30,
                "last_maintenance": None
            },
            "CAM002": {
                "name": "Engine Room Overview",
                "location": "Engine Room",
                "zone": "engine_room",
                "type": "Fixed",
                "status": CameraStatus.ONLINE,
                "recording": RecordingMode.CONTINUOUS,
                "resolution": "1080p",
                "night_vision": True,
                "audio": False,
                "current_preset": "engine_monitoring",
                "temperature_overlay": True,
                "vibration_detection": True,
                "storage_days": 90,
                "last_maintenance": None
            },
            "CAM003": {
                "name": "Main Deck Port Side",
                "location": "Main Deck",
                "zone": "crew_quarters",
                "type": "PTZ",
                "status": CameraStatus.ONLINE,
                "recording": RecordingMode.MOTION_DETECTION,
                "resolution": "1080p",
                "night_vision": True,
                "audio": False,
                "current_preset": "deck_patrol",
                "pan": -45,
                "tilt": -15,
                "zoom": 1.2,
                "weather_resistant": True,
                "storage_days": 14,
                "last_maintenance": None
            },
            "CAM004": {
                "name": "Cargo Hold Monitor",
                "location": "Cargo Hold",
                "zone": "cargo_hold",
                "type": "Fixed",
                "status": CameraStatus.ONLINE,
                "recording": RecordingMode.EVENT_BASED,
                "resolution": "1080p",
                "night_vision": True,
                "audio": False,
                "current_preset": "cargo_overview",
                "low_light_enhancement": True,
                "storage_days": 60,
                "last_maintenance": None
            },
            "CAM005": {
                "name": "Galley Safety Monitor",
                "location": "Galley",
                "zone": "galley",
                "type": "Fixed",
                "status": CameraStatus.ONLINE,
                "recording": RecordingMode.CONTINUOUS,
                "resolution": "1080p",
                "night_vision": False,
                "audio": True,
                "current_preset": "kitchen_safety",
                "heat_detection": True,
                "smoke_overlay": True,
                "storage_days": 30,
                "last_maintenance": None
            },
            "CAM006": {
                "name": "Emergency Exit Monitor",
                "location": "Emergency Exit",
                "zone": "main_deck",
                "type": "Fixed",
                "status": CameraStatus.ONLINE,
                "recording": RecordingMode.MOTION_DETECTION,
                "resolution": "1080p",
                "night_vision": True,
                "audio": False,
                "current_preset": "exit_monitoring",
                "motion_sensitivity": "high",
                "storage_days": 7,
                "last_maintenance": None
            }
        }
    
    def _initialize_event_presets(self) -> Dict[str, Dict]:
        """Initialize camera presets for different emergency scenarios."""
        return {
            "fire_emergency": {
                "description": "Fire emergency camera positions",
                "camera_settings": {
                    "CAM001": {"preset": "fire_command_view", "pan": 0, "tilt": -30, "zoom": 2.0},
                    "CAM002": {"preset": "engine_fire_view", "zoom": 1.5, "thermal_overlay": True},
                    "CAM003": {"preset": "evacuation_routes", "pan": 0, "tilt": -10, "zoom": 1.0},
                    "CAM004": {"preset": "cargo_fire_monitor", "zoom": 2.0, "smoke_detection": True},
                    "CAM005": {"preset": "galley_fire_view", "zoom": 1.8, "heat_overlay": True},
                    "CAM006": {"preset": "emergency_exit_focus", "zoom": 2.5, "motion_track": True}
                },
                "recording_mode": RecordingMode.CONTINUOUS,
                "retention_priority": "high"
            },
            "emergency_stop": {
                "description": "Emergency stop monitoring positions",
                "camera_settings": {
                    "CAM001": {"preset": "command_center", "pan": 0, "tilt": 0, "zoom": 1.0},
                    "CAM002": {"preset": "machinery_overview", "zoom": 1.0, "status_overlay": True},
                    "CAM003": {"preset": "personnel_monitoring", "pan": 30, "tilt": -20, "zoom": 1.5},
                    "CAM004": {"preset": "cargo_security", "zoom": 1.0},
                    "CAM005": {"preset": "galley_safety", "zoom": 1.0},
                    "CAM006": {"preset": "exit_readiness", "zoom": 1.0, "door_status": True}
                },
                "recording_mode": RecordingMode.CONTINUOUS,
                "retention_priority": "critical"
            },
            "security_alert": {
                "description": "Security alert monitoring",
                "camera_settings": {
                    "CAM001": {"preset": "perimeter_scan", "pan": "patrol", "tilt": 0, "zoom": 1.2},
                    "CAM002": {"preset": "restricted_access", "zoom": 1.0},
                    "CAM003": {"preset": "deck_patrol", "pan": "sweep", "tilt": -10, "zoom": 1.5},
                    "CAM004": {"preset": "cargo_security", "zoom": 1.8, "motion_detect": True},
                    "CAM005": {"preset": "access_control", "zoom": 1.0},
                    "CAM006": {"preset": "exit_monitoring", "zoom": 1.0, "facial_recognition": True}
                },
                "recording_mode": RecordingMode.EVENT_BASED,
                "retention_priority": "medium"
            },
            "normal_operations": {
                "description": "Normal operational monitoring",
                "camera_settings": {
                    "CAM001": {"preset": "normal_view", "pan": 0, "tilt": 0, "zoom": 1.0},
                    "CAM002": {"preset": "engine_monitoring", "zoom": 1.0},
                    "CAM003": {"preset": "deck_patrol", "pan": -45, "tilt": -15, "zoom": 1.2},
                    "CAM004": {"preset": "cargo_overview", "zoom": 1.0},
                    "CAM005": {"preset": "kitchen_safety", "zoom": 1.0},
                    "CAM006": {"preset": "exit_monitoring", "zoom": 1.0}
                },
                "recording_mode": RecordingMode.MOTION_DETECTION,
                "retention_priority": "low"
            }
        }
    
    async def register_integration_callback(self, callback):
        """Register callback for system integration."""
        self.integration_callbacks.append(callback)
        logger.debug(f"Integration callback registered: {callback.__name__}")
    
    async def handle_emergency_event(self, event_type: str, event_data: Dict) -> Dict:
        """
        Handle emergency events by focusing cameras and adjusting recording.
        
        Args:
            event_type: Type of emergency event
            event_data: Event details including location
            
        Returns:
            Dict with camera response actions
        """
        logger.warning(f"📹 CCTV responding to emergency: {event_type}")
        
        # Determine appropriate preset based on event type
        preset_name = self._get_preset_for_event(event_type)
        if not preset_name:
            preset_name = "emergency_stop"  # Default emergency preset
        
        # Apply emergency preset
        result = await self.apply_camera_preset(preset_name)
        
        # Focus specific cameras on event location if provided
        if "zone" in event_data:
            await self._focus_on_zone(event_data["zone"], event_type)
        
        # Start emergency recording session
        session_id = await self._start_emergency_recording(event_type, event_data)
        
        # Log CCTV response
        await self._log_event(
            event_type="CCTV_EMERGENCY_RESPONSE",
            severity=EventSeverity.WARNING,
            message=f"CCTV system responding to {event_type}",
            additional_data=json.dumps({
                "preset_applied": preset_name,
                "recording_session": session_id,
                "event_data": event_data
            })
        )
        
        return {
            "success": True,
            "preset_applied": preset_name,
            "cameras_focused": await self._get_focused_cameras(event_data.get("zone")),
            "recording_session": session_id,
            "response_time": "immediate"
        }
    
    def _get_preset_for_event(self, event_type: str) -> Optional[str]:
        """Get appropriate camera preset for event type."""
        event_preset_map = {
            "fire_alarm": "fire_emergency",
            "emergency_stop": "emergency_stop",
            "security_breach": "security_alert",
            "medical_emergency": "emergency_stop",
            "man_overboard": "security_alert"
        }
        return event_preset_map.get(event_type)
    
    async def _focus_on_zone(self, zone: str, event_type: str):
        """Focus cameras on specific zone during emergency."""
        focused_cameras = []
        
        for camera_id, camera in self.cameras.items():
            if camera["zone"] == zone or camera["location"].lower() in zone.lower():
                # Adjust camera for zone focus
                if camera["type"] == "PTZ":
                    await self._adjust_ptz_camera(camera_id, zone, event_type)
                
                # Switch to continuous recording
                camera["recording"] = RecordingMode.CONTINUOUS
                focused_cameras.append(camera_id)
                
                logger.info(f"📹 Camera {camera_id} focused on zone {zone}")
        
        return focused_cameras
    
    async def _adjust_ptz_camera(self, camera_id: str, zone: str, event_type: str):
        """Adjust PTZ camera position for optimal zone coverage."""
        camera = self.cameras[camera_id]
        
        # Zone-specific positioning (simplified for demo)
        zone_positions = {
            "engine_room": {"pan": 0, "tilt": -20, "zoom": 2.0},
            "bridge": {"pan": 0, "tilt": 0, "zoom": 1.5},
            "crew_quarters": {"pan": 30, "tilt": -15, "zoom": 1.8},
            "cargo_hold": {"pan": 0, "tilt": -30, "zoom": 2.5},
            "galley": {"pan": 0, "tilt": -10, "zoom": 1.8}
        }
        
        if zone in zone_positions:
            position = zone_positions[zone]
            camera["pan"] = position["pan"]
            camera["tilt"] = position["tilt"]
            camera["zoom"] = position["zoom"]
            
            logger.debug(f"PTZ camera {camera_id} positioned for {zone}")
    
    async def _start_emergency_recording(self, event_type: str, event_data: Dict) -> str:
        """Start emergency recording session for all cameras."""
        session_id = f"EMR-{int(datetime.utcnow().timestamp())}"
        
        self.recording_sessions[session_id] = {
            "start_time": datetime.utcnow(),
            "event_type": event_type,
            "event_data": event_data,
            "cameras": list(self.cameras.keys()),
            "priority": "high",
            "retention_days": 365,  # Extended retention for emergencies
            "status": "active"
        }
        
        logger.info(f"📹 Emergency recording session started: {session_id}")
        return session_id
    
    async def _get_focused_cameras(self, zone: str = None) -> List[str]:
        """Get list of cameras focused on specific zone."""
        if not zone:
            return []
        
        focused = []
        for camera_id, camera in self.cameras.items():
            if camera["zone"] == zone or camera["location"].lower() in zone.lower():
                focused.append({
                    "camera_id": camera_id,
                    "name": camera["name"],
                    "location": camera["location"],
                    "status": camera["status"]
                })
        
        return focused
    
    async def apply_camera_preset(self, preset_name: str) -> Dict:
        """Apply predefined camera preset configuration."""
        if preset_name not in self.event_presets:
            logger.error(f"Unknown camera preset: {preset_name}")
            return {"success": False, "error": f"Unknown preset: {preset_name}"}
        
        preset = self.event_presets[preset_name]
        applied_cameras = []
        
        logger.info(f"📹 Applying camera preset: {preset_name}")
        
        for camera_id, settings in preset["camera_settings"].items():
            if camera_id in self.cameras:
                camera = self.cameras[camera_id]
                
                # Apply preset settings
                camera["current_preset"] = settings.get("preset", camera["current_preset"])
                
                if "pan" in settings:
                    camera["pan"] = settings["pan"]
                if "tilt" in settings:
                    camera["tilt"] = settings["tilt"]
                if "zoom" in settings:
                    camera["zoom"] = settings["zoom"]
                
                # Apply recording mode
                camera["recording"] = preset["recording_mode"]
                
                applied_cameras.append({
                    "camera_id": camera_id,
                    "preset": settings.get("preset"),
                    "recording": preset["recording_mode"]
                })
                
                logger.debug(f"Preset applied to camera {camera_id}")
        
        return {
            "success": True,
            "preset_name": preset_name,
            "description": preset["description"],
            "cameras_configured": len(applied_cameras),
            "applied_cameras": applied_cameras
        }
    
    async def get_system_status(self) -> Dict:
        """Get current CCTV system status."""
        online_cameras = sum(1 for cam in self.cameras.values() if cam["status"] == CameraStatus.ONLINE)
        recording_cameras = sum(1 for cam in self.cameras.values() 
                              if cam["recording"] == RecordingMode.CONTINUOUS)
        
        return {
            "system_type": self.system_type.value,
            "status": self.status.value,
            "total_cameras": len(self.cameras),
            "online_cameras": online_cameras,
            "recording_cameras": recording_cameras,
            "active_recording_sessions": len(self.recording_sessions),
            "storage_usage": self.storage_usage,
            "cameras": self.cameras,
            "recording_sessions": self.recording_sessions,
            "last_maintenance": self.last_maintenance.isoformat() if self.last_maintenance else None,
            "performance_score": self._calculate_performance_score()
        }
    
    async def get_camera_feed(self, camera_id: str) -> Dict:
        """Get live camera feed information (simulated)."""
        if camera_id not in self.cameras:
            return {"success": False, "error": f"Camera {camera_id} not found"}
        
        camera = self.cameras[camera_id]
        
        # Simulate live feed data
        feed_data = {
            "camera_id": camera_id,
            "name": camera["name"],
            "location": camera["location"],
            "status": camera["status"],
            "resolution": camera["resolution"],
            "recording": camera["recording"],
            "stream_url": f"rtsp://ship-cctv/{camera_id}/live",
            "timestamp": datetime.utcnow().isoformat(),
            "frame_rate": "25fps",
            "bitrate": "2048kbps"
        }
        
        # Add PTZ position if applicable
        if camera["type"] == "PTZ":
            feed_data["ptz_position"] = {
                "pan": camera["pan"],
                "tilt": camera["tilt"],
                "zoom": camera["zoom"]
            }
        
        return {
            "success": True,
            "feed_data": feed_data
        }
    
    async def control_ptz_camera(self, camera_id: str, pan: float = None, 
                                tilt: float = None, zoom: float = None) -> Dict:
        """Control PTZ camera movement."""
        if camera_id not in self.cameras:
            return {"success": False, "error": f"Camera {camera_id} not found"}
        
        camera = self.cameras[camera_id]
        if camera["type"] != "PTZ":
            return {"success": False, "error": f"Camera {camera_id} is not PTZ capable"}
        
        # Update camera position
        if pan is not None:
            camera["pan"] = max(-180, min(180, pan))
        if tilt is not None:
            camera["tilt"] = max(-90, min(90, tilt))
        if zoom is not None:
            camera["zoom"] = max(1.0, min(10.0, zoom))
        
        logger.info(f"📹 PTZ camera {camera_id} positioned: pan={camera['pan']}, tilt={camera['tilt']}, zoom={camera['zoom']}")
        
        return {
            "success": True,
            "camera_id": camera_id,
            "position": {
                "pan": camera["pan"],
                "tilt": camera["tilt"],
                "zoom": camera["zoom"]
            }
        }
    
    async def perform_system_test(self) -> Dict:
        """Perform CCTV system test."""
        logger.info("🧪 Performing CCTV system test")
        
        self.last_maintenance = datetime.utcnow()
        test_results = {}
        
        # Test each camera
        for camera_id, camera in self.cameras.items():
            # Simulate camera tests
            video_quality = "excellent" if camera["status"] == CameraStatus.ONLINE else "poor"
            recording_test = camera["status"] == CameraStatus.ONLINE
            connectivity_test = camera["status"] == CameraStatus.ONLINE
            
            # PTZ functionality test
            ptz_test = True
            if camera["type"] == "PTZ":
                # Simulate PTZ movement test
                ptz_test = camera["status"] == CameraStatus.ONLINE
            
            test_results[camera_id] = {
                "name": camera["name"],
                "location": camera["location"],
                "video_quality": video_quality,
                "recording_test": "PASS" if recording_test else "FAIL",
                "connectivity_test": "PASS" if connectivity_test else "FAIL",
                "ptz_test": "PASS" if ptz_test else "N/A",
                "overall": "PASS" if all([recording_test, connectivity_test, ptz_test]) else "FAIL"
            }
        
        # Storage system test
        storage_test = {
            "usage_percentage": self.storage_usage,
            "available_space": f"{(100 - self.storage_usage):.1f}%",
            "retention_compliance": "PASS",
            "backup_systems": "PASS"
        }
        
        # Log test completion
        await self._log_event(
            event_type="SYSTEM_TEST_COMPLETED",
            severity=EventSeverity.INFO,
            message="CCTV system test completed",
            additional_data=json.dumps({
                "camera_results": test_results,
                "storage_test": storage_test
            })
        )
        
        return {
            "test_completed": True,
            "timestamp": self.last_maintenance.isoformat(),
            "camera_results": test_results,
            "storage_test": storage_test,
            "overall_status": "PASS"
        }
    
    def _calculate_performance_score(self) -> float:
        """Calculate system performance score."""
        base_score = 100.0
        
        # Reduce score for offline cameras
        offline_cameras = sum(1 for cam in self.cameras.values() if cam["status"] != CameraStatus.ONLINE)
        base_score -= offline_cameras * 15
        
        # Reduce score for high storage usage
        if self.storage_usage > 90:
            base_score -= 20
        elif self.storage_usage > 80:
            base_score -= 10
        
        # Reduce score if maintenance is overdue
        if self.last_maintenance:
            days_since_maintenance = (datetime.utcnow() - self.last_maintenance).days
            if days_since_maintenance > 30:
                base_score -= min(days_since_maintenance - 30, 25)
        else:
            base_score -= 20  # No maintenance performed
        
        return max(0, base_score)
    
    async def _notify_integrated_systems(self, event_type: str, data: Dict):
        """Notify other systems of CCTV events."""
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