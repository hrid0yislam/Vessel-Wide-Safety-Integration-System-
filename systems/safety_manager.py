"""
Safety System Manager
Central coordination hub for all ship safety systems integration.

This system demonstrates understanding of:
- System integration and coordination
- Event-driven architecture
- Emergency response automation
- Multi-vendor system management
- Real-time monitoring and control
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from loguru import logger
from database.models import SystemType, SystemStatus, EventSeverity

class SafetySystemManager:
    """
    Central Safety System Manager for ship safety integration.
    
    Coordinates all safety systems including Emergency Stop, Fire Detection,
    CCTV, PAGA, Communication, and Compliance monitoring with automated
    emergency response and real-time system integration.
    """
    
    def __init__(self, emergency_stop, fire_detection, cctv_system, paga_system,
                 communication, compliance_monitor, connection_manager):
        # System references
        self.emergency_stop = emergency_stop
        self.fire_detection = fire_detection
        self.cctv_system = cctv_system
        self.paga_system = paga_system
        self.communication = communication
        self.compliance_monitor = compliance_monitor
        self.connection_manager = connection_manager
        
        # Manager state
        self.system_type = "safety_manager"
        self.status = SystemStatus.NORMAL
        self.integration_active = False
        self.event_queue = asyncio.Queue()
        self.system_events = []
        self.emergency_protocols = self._initialize_emergency_protocols()
        self.performance_metrics = {}
        self.last_system_check = None
        
        logger.info("🎯 Safety System Manager initialized")
    
    def _initialize_emergency_protocols(self) -> Dict[str, Dict]:
        """Initialize emergency response protocols."""
        return {
            "fire_emergency": {
                "name": "Fire Emergency Response Protocol",
                "priority": "critical",
                "response_time": 30,  # seconds
                "systems_involved": ["fire_detection", "emergency_stop", "paga", "cctv", "communication"],
                "automated_actions": [
                    "trigger_fire_alarm",
                    "activate_suppression",
                    "emergency_stop_affected_zones",
                    "announce_evacuation",
                    "focus_cameras",
                    "notify_authorities"
                ],
                "escalation_levels": {
                    "level_1": "Local alarm and suppression",
                    "level_2": "Zone evacuation and emergency stop",
                    "level_3": "Ship-wide emergency and external assistance"
                }
            },
            "emergency_stop": {
                "name": "Emergency Stop Response Protocol",
                "priority": "critical",
                "response_time": 15,
                "systems_involved": ["emergency_stop", "paga", "cctv", "communication"],
                "automated_actions": [
                    "shutdown_machinery",
                    "announce_emergency_stop",
                    "focus_cameras_on_zones",
                    "notify_bridge_crew",
                    "prepare_emergency_power"
                ]
            },
            "man_overboard": {
                "name": "Man Overboard Response Protocol",
                "priority": "critical",
                "response_time": 10,
                "systems_involved": ["paga", "communication", "cctv"],
                "automated_actions": [
                    "sound_mob_alarm",
                    "send_distress_call",
                    "focus_cameras_overboard",
                    "activate_mob_equipment",
                    "record_position"
                ]
            },
            "general_emergency": {
                "name": "General Emergency Response Protocol",
                "priority": "high",
                "response_time": 45,
                "systems_involved": ["paga", "cctv", "communication", "compliance"],
                "automated_actions": [
                    "sound_general_alarm",
                    "muster_announcement",
                    "emergency_lighting",
                    "notify_authorities",
                    "document_emergency"
                ]
            }
        }
    
    async def initialize(self):
        """Initialize all safety systems and their integrations."""
        logger.info("🚀 Initializing Safety System Integration")
        
        # Register integration callbacks with all systems
        systems = [
            self.emergency_stop,
            self.fire_detection,
            self.cctv_system,
            self.paga_system,
            self.communication,
            self.compliance_monitor
        ]
        
        for system in systems:
            await system.register_integration_callback(self._handle_system_event)
        
        self.integration_active = True
        logger.info("✅ All safety systems integrated and callbacks registered")
        
        # Perform initial system status check
        await self._perform_initial_system_check()
        
        # Start background compliance monitoring
        asyncio.create_task(self._continuous_compliance_monitoring())
        
        logger.info("🎯 Safety System Manager fully operational")
    
    async def _perform_initial_system_check(self):
        """Perform initial check of all systems."""
        logger.info("🔍 Performing initial system status check")
        
        system_status = await self.get_system_status()
        
        # Check for any immediate issues
        issues = []
        for system_name, system_data in system_status.items():
            if system_name == "integration_status":
                continue
                
            if system_data.get("status") != "normal":
                issues.append(f"{system_name}: {system_data.get('status')}")
            
            performance = system_data.get("performance_score", 100)
            if performance < 80:
                issues.append(f"{system_name}: Low performance ({performance}%)")
        
        if issues:
            logger.warning(f"⚠️ Initial system check found {len(issues)} issues")
            for issue in issues:
                logger.warning(f"   - {issue}")
        else:
            logger.info("✅ All systems operational - No issues detected")
        
        self.last_system_check = datetime.utcnow()
    
    async def _handle_system_event(self, source_system: SystemType, event_type: str, event_data: Dict):
        """
        Handle events from integrated safety systems.
        
        Args:
            source_system: System that generated the event
            event_type: Type of event
            event_data: Event details
        """
        logger.info(f"🔄 Processing event from {source_system.value}: {event_type}")
        
        # Create system event record
        system_event = {
            "id": f"EVT-{int(datetime.utcnow().timestamp())}",
            "source_system": source_system.value,
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.utcnow(),
            "processed": False,
            "response_actions": []
        }
        
        self.system_events.append(system_event)
        
        # Queue for processing
        await self.event_queue.put(system_event)
        
        # Broadcast event to connected clients
        await self._broadcast_event_update(system_event)
    
    async def start_monitoring(self):
        """Start continuous monitoring and event processing."""
        logger.info("🔍 Starting continuous safety system monitoring")
        
        # Start event processing task
        asyncio.create_task(self._process_events())
        
        # Start periodic system checks
        asyncio.create_task(self._periodic_system_checks())
        
        # Start performance monitoring
        asyncio.create_task(self._monitor_performance())
    
    async def _process_events(self):
        """Process events from the event queue."""
        while True:
            try:
                # Get event from queue
                event = await self.event_queue.get()
                
                # Process the event
                await self._process_single_event(event)
                
                # Mark as processed
                event["processed"] = True
                event["processed_at"] = datetime.utcnow()
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                await asyncio.sleep(1)
    
    async def _process_single_event(self, event: Dict):
        """Process a single system event and coordinate response."""
        source_system = event["source_system"]
        event_type = event["event_type"]
        event_data = event["event_data"]
        
        logger.info(f"🎯 Processing {event_type} from {source_system}")
        
        response_actions = []
        
        # Determine response based on event type
        if event_type == "fire_alarm":
            response_actions = await self._handle_fire_emergency(event_data)
        elif event_type == "emergency_stop":
            response_actions = await self._handle_emergency_stop(event_data)
        elif event_type == "man_overboard":
            response_actions = await self._handle_man_overboard(event_data)
        elif event_type == "system_fault":
            response_actions = await self._handle_system_fault(event_data)
        elif event_type in ["alarm_activated", "emergency_response"]:
            response_actions = await self._handle_general_emergency(event_data)
        
        # Record response actions
        event["response_actions"] = response_actions
        
        # Log integration event
        logger.info(f"✅ Event processed: {len(response_actions)} automated responses")
    
    async def _handle_fire_emergency(self, event_data: Dict) -> List[str]:
        """Handle fire emergency with coordinated system response."""
        logger.critical("🔥 COORDINATING FIRE EMERGENCY RESPONSE")
        
        actions = []
        zone = event_data.get("zone", "unknown")
        
        # 1. Emergency Stop for affected areas
        if zone != "unknown":
            try:
                from .emergency_stop import EmergencyStopZone
                if zone == "engine_room":
                    await self.emergency_stop.trigger_emergency_stop(
                        EmergencyStopZone.ENGINE_ROOM, 
                        f"Fire alarm in {zone}"
                    )
                    actions.append(f"Emergency stop activated for {zone}")
            except Exception as e:
                logger.error(f"Error triggering emergency stop: {e}")
        
        # 2. PAGA announcement
        try:
            from .paga_system import AlarmType
            await self.paga_system.trigger_alarm(
                AlarmType.FIRE_ALARM,
                zones=["all_zones"]
            )
            actions.append("Fire alarm sounded ship-wide")
        except Exception as e:
            logger.error(f"Error triggering PAGA alarm: {e}")
        
        # 3. CCTV focus on fire zone
        try:
            await self.cctv_system.handle_emergency_event("fire_alarm", event_data)
            actions.append(f"CCTV cameras focused on {zone}")
        except Exception as e:
            logger.error(f"Error focusing CCTV: {e}")
        
        # 4. Communication to authorities
        try:
            message = f"FIRE ALARM ACTIVATED IN {zone.upper()}"
            await self.communication.send_safety_message(
                message, 
                ["coast_guard", "port_authority"],
                self.communication.CommunicationPriority.URGENCY
            )
            actions.append("Authorities notified of fire emergency")
        except Exception as e:
            logger.error(f"Error sending communications: {e}")
        
        # Update system status
        self.status = SystemStatus.EMERGENCY
        
        return actions
    
    async def _handle_emergency_stop(self, event_data: Dict) -> List[str]:
        """Handle emergency stop event coordination."""
        logger.critical("🚨 COORDINATING EMERGENCY STOP RESPONSE")
        
        actions = []
        
        # 1. PAGA announcement
        try:
            from .paga_system import AlarmType
            await self.paga_system.trigger_alarm(
                AlarmType.GENERAL_ALARM,
                zones=["all_zones"]
            )
            actions.append("General alarm sounded for emergency stop")
        except Exception as e:
            logger.error(f"Error triggering PAGA: {e}")
        
        # 2. CCTV monitoring
        try:
            await self.cctv_system.handle_emergency_event("emergency_stop", event_data)
            actions.append("CCTV monitoring activated for emergency zones")
        except Exception as e:
            logger.error(f"Error activating CCTV: {e}")
        
        # 3. Communication
        try:
            reason = event_data.get("reason", "Unknown reason")
            message = f"EMERGENCY STOP ACTIVATED - {reason}"
            await self.communication.send_safety_message(
                message,
                ["coast_guard", "shipping_company"]
            )
            actions.append("Emergency stop notification sent")
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
        
        self.status = SystemStatus.EMERGENCY
        return actions
    
    async def _handle_man_overboard(self, event_data: Dict) -> List[str]:
        """Handle man overboard emergency."""
        logger.critical("🆘 COORDINATING MAN OVERBOARD RESPONSE")
        
        actions = []
        
        # 1. PAGA alarm
        try:
            from .paga_system import AlarmType
            await self.paga_system.trigger_alarm(
                AlarmType.MAN_OVERBOARD,
                zones=["all_zones"]
            )
            actions.append("Man overboard alarm sounded")
        except Exception as e:
            logger.error(f"Error triggering MOB alarm: {e}")
        
        # 2. Distress call
        try:
            position = event_data.get("position", {})
            await self.communication.send_distress_call("MAN OVERBOARD", position)
            actions.append("Distress call transmitted")
        except Exception as e:
            logger.error(f"Error sending distress call: {e}")
        
        # 3. CCTV tracking
        try:
            await self.cctv_system.handle_emergency_event("man_overboard", event_data)
            actions.append("CCTV cameras positioned for search")
        except Exception as e:
            logger.error(f"Error positioning CCTV: {e}")
        
        self.status = SystemStatus.EMERGENCY
        return actions
    
    async def _handle_system_fault(self, event_data: Dict) -> List[str]:
        """Handle system fault events."""
        logger.warning("⚠️ HANDLING SYSTEM FAULT")
        
        actions = []
        system_name = event_data.get("system", "unknown")
        
        # Log fault for compliance
        try:
            await self.compliance_monitor.perform_compliance_check(
                self.compliance_monitor.ComplianceStandard.ISM,
                await self.get_system_status()
            )
            actions.append("System fault logged for compliance")
        except Exception as e:
            logger.error(f"Error logging compliance: {e}")
        
        return actions
    
    async def _handle_general_emergency(self, event_data: Dict) -> List[str]:
        """Handle general emergency situations."""
        logger.warning("🚨 HANDLING GENERAL EMERGENCY")
        
        actions = []
        
        # Basic emergency response
        try:
            await self.cctv_system.apply_camera_preset("emergency_stop")
            actions.append("Emergency camera preset activated")
        except Exception as e:
            logger.error(f"Error setting camera preset: {e}")
        
        return actions
    
    async def trigger_emergency_stop(self) -> Dict:
        """Trigger coordinated emergency stop across all systems."""
        logger.critical("🚨 TRIGGERING COORDINATED EMERGENCY STOP")
        
        # Trigger emergency stop system
        result = await self.emergency_stop.trigger_emergency_stop()
        
        return result
    
    async def trigger_fire_alarm(self, zone: str) -> Dict:
        """Trigger coordinated fire alarm response."""
        logger.critical(f"🔥 TRIGGERING COORDINATED FIRE ALARM: {zone}")
        
        # Trigger fire detection system
        result = await self.fire_detection.trigger_fire_alarm(zone)
        
        return result
    
    async def reset_all_systems(self) -> Dict:
        """Reset all safety systems to normal operation."""
        logger.info("🔄 RESETTING ALL SAFETY SYSTEMS")
        
        reset_results = {}
        
        # Reset each system
        try:
            # Reset emergency stop
            emergency_result = await self.emergency_stop.reset_emergency_stop()
            reset_results["emergency_stop"] = emergency_result
            
            # Reset fire alarms (get active alarms first)
            fire_status = await self.fire_detection.get_system_status()
            active_alarms = fire_status.get("alarm_details", {})
            for alarm_id in active_alarms.keys():
                await self.fire_detection.reset_fire_alarm(alarm_id)
            reset_results["fire_detection"] = {"alarms_reset": len(active_alarms)}
            
            # Reset CCTV to normal preset
            cctv_result = await self.cctv_system.apply_camera_preset("normal_operations")
            reset_results["cctv"] = cctv_result
            
            # Stop active PAGA announcements
            paga_status = await self.paga_system.get_system_status()
            active_announcements = paga_status.get("announcement_details", {})
            for ann_id in active_announcements.keys():
                if active_announcements[ann_id].get("status") == "playing":
                    await self.paga_system.stop_announcement(ann_id)
            reset_results["paga"] = {"announcements_stopped": len(active_announcements)}
            
            # Reset system status
            self.status = SystemStatus.NORMAL
            
            logger.info("✅ All safety systems reset to normal operation")
            
        except Exception as e:
            logger.error(f"Error resetting systems: {e}")
            reset_results["error"] = str(e)
        
        return {
            "success": True,
            "timestamp": datetime.utcnow().isoformat(),
            "systems_reset": list(reset_results.keys()),
            "details": reset_results
        }
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive status of all integrated safety systems."""
        try:
            # Get status from all systems
            status_data = {}
            
            status_data["emergency_stop"] = await self.emergency_stop.get_system_status()
            status_data["fire_detection"] = await self.fire_detection.get_system_status()
            status_data["cctv"] = await self.cctv_system.get_system_status()
            status_data["paga"] = await self.paga_system.get_system_status()
            status_data["communication"] = await self.communication.get_system_status()
            status_data["compliance"] = await self.compliance_monitor.get_system_status()
            
            # Add integration status
            status_data["integration_status"] = {
                "manager_status": self.status.value,
                "integration_active": self.integration_active,
                "total_events_processed": len(self.system_events),
                "recent_events": len([e for e in self.system_events 
                                    if e["timestamp"] > datetime.utcnow() - timedelta(hours=1)]),
                "last_system_check": self.last_system_check.isoformat() if self.last_system_check else None,
                "performance_metrics": self.performance_metrics
            }
            
            return status_data
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    async def get_recent_events(self, hours: int = 24) -> Dict:
        """Get recent system events."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_events = [
            {
                "id": event["id"],
                "source_system": event["source_system"],
                "event_type": event["event_type"],
                "timestamp": event["timestamp"].isoformat(),
                "processed": event["processed"],
                "response_actions": len(event.get("response_actions", []))
            }
            for event in self.system_events
            if event["timestamp"] > cutoff_time
        ]
        
        return {
            "events": sorted(recent_events, key=lambda x: x["timestamp"], reverse=True),
            "total_events": len(recent_events),
            "timeframe_hours": hours
        }
    
    async def get_compliance_status(self) -> Dict:
        """Get current compliance status."""
        try:
            # Generate compliance report
            report = await self.compliance_monitor.generate_compliance_report()
            
            # Get certificate status
            cert_status = await self.compliance_monitor.check_certificate_validity()
            
            return {
                "compliance_report": report,
                "certificate_status": cert_status,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance status: {e}")
            return {"error": str(e)}
    
    async def _continuous_compliance_monitoring(self):
        """Continuous compliance monitoring background task."""
        while True:
            try:
                # Perform compliance checks every 24 hours
                await asyncio.sleep(24 * 3600)
                
                logger.info("⚖️ Performing scheduled compliance check")
                
                # Get current system status
                system_status = await self.get_system_status()
                
                # Perform SOLAS compliance check
                await self.compliance_monitor.perform_compliance_check(
                    self.compliance_monitor.ComplianceStandard.SOLAS,
                    system_status
                )
                
                # Check certificate validity
                await self.compliance_monitor.check_certificate_validity()
                
            except Exception as e:
                logger.error(f"Error in compliance monitoring: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    async def _periodic_system_checks(self):
        """Perform periodic system health checks."""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                logger.info("🔍 Performing periodic system health check")
                
                # Update last check time
                self.last_system_check = datetime.utcnow()
                
                # Get system status and check for issues
                status = await self.get_system_status()
                
                # Check system performance
                for system_name, system_data in status.items():
                    if system_name == "integration_status":
                        continue
                    
                    performance = system_data.get("performance_score", 100)
                    if performance < 70:
                        logger.warning(f"⚠️ Low performance detected: {system_name} ({performance}%)")
                
            except Exception as e:
                logger.error(f"Error in periodic system check: {e}")
    
    async def _monitor_performance(self):
        """Monitor system performance metrics."""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Calculate performance metrics
                current_status = await self.get_system_status()
                
                # Update performance metrics
                self.performance_metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "overall_health": self._calculate_overall_health(current_status),
                    "events_per_hour": len([e for e in self.system_events 
                                          if e["timestamp"] > datetime.utcnow() - timedelta(hours=1)]),
                    "integration_uptime": "99.9%",  # Simulated
                    "response_time_avg": "0.5s"  # Simulated
                }
                
            except Exception as e:
                logger.error(f"Error monitoring performance: {e}")
    
    def _calculate_overall_health(self, status_data: Dict) -> float:
        """Calculate overall system health score."""
        scores = []
        
        for system_name, system_data in status_data.items():
            if system_name == "integration_status":
                continue
            
            score = system_data.get("performance_score", 100)
            scores.append(score)
        
        return sum(scores) / len(scores) if scores else 0
    
    async def _broadcast_event_update(self, event: Dict):
        """Broadcast event update to connected clients."""
        try:
            message = {
                "type": "system_event",
                "data": {
                    "event_id": event["id"],
                    "source_system": event["source_system"],
                    "event_type": event["event_type"],
                    "timestamp": event["timestamp"].isoformat(),
                    "processed": event["processed"]
                }
            }
            
            await self.connection_manager.broadcast(message)
            
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}")
    
    async def shutdown(self):
        """Gracefully shutdown the safety system manager."""
        logger.info("🛑 Shutting down Safety System Manager")
        
        self.integration_active = False
        
        # Reset all systems to normal before shutdown
        try:
            await self.reset_all_systems()
        except Exception as e:
            logger.error(f"Error resetting systems during shutdown: {e}")
        
        logger.info("✅ Safety System Manager shutdown complete") 