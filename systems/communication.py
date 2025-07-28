"""
Communication System
Radio and telecommunication system for internal and external ship communications.

This system demonstrates understanding of:
- Maritime communication protocols
- Emergency communication procedures
- Multi-channel radio management
- Integration with safety systems
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

from loguru import logger
from database.models import SystemType, SystemStatus, EventSeverity

class RadioType(str, Enum):
    VHF = "vhf"
    HF = "hf"
    SATELLITE = "satellite"
    INTERNAL = "internal"
    EMERGENCY = "emergency"

class CommunicationPriority(str, Enum):
    ROUTINE = "routine"
    SAFETY = "safety"
    URGENCY = "urgency"
    DISTRESS = "distress"

class CommunicationSystem:
    """
    Communication System for ship radio and telecommunications.
    
    Provides comprehensive communication capabilities including
    VHF, HF, satellite, and internal communications with emergency protocols.
    """
    
    def __init__(self):
        self.system_type = SystemType.COMMUNICATION
        self.status = SystemStatus.NORMAL
        self.radios = self._initialize_radios()
        self.channels = self._initialize_channels()
        self.active_communications = {}
        self.emergency_contacts = self._initialize_emergency_contacts()
        self.message_log = []
        self.last_test = None
        self.integration_callbacks = []
        
        logger.info("📡 Communication System initialized")
    
    def _initialize_radios(self) -> Dict[str, Dict]:
        """Initialize radio equipment configuration."""
        return {
            "VHF_001": {
                "type": RadioType.VHF,
                "name": "VHF Main",
                "location": "Bridge",
                "frequency_range": "156-174 MHz",
                "power_output": "25W",
                "status": "online",
                "current_channel": 16,
                "scanning": True,
                "emergency_capable": True,
                "backup_power": True,
                "last_maintenance": None
            },
            "VHF_002": {
                "type": RadioType.VHF,
                "name": "VHF Portable",
                "location": "Bridge",
                "frequency_range": "156-174 MHz",
                "power_output": "5W",
                "status": "online",
                "current_channel": 6,
                "scanning": False,
                "emergency_capable": True,
                "backup_power": False,
                "last_maintenance": None
            },
            "HF_001": {
                "type": RadioType.HF,
                "name": "HF Transceiver",
                "location": "Radio Room",
                "frequency_range": "1.6-30 MHz",
                "power_output": "150W",
                "status": "online",
                "current_frequency": "8291 kHz",
                "antenna_tuning": "automatic",
                "emergency_capable": True,
                "backup_power": True,
                "last_maintenance": None
            },
            "SAT_001": {
                "type": RadioType.SATELLITE,
                "name": "Inmarsat C",
                "location": "Bridge",
                "service_provider": "Inmarsat",
                "status": "online",
                "signal_strength": 85,
                "data_rate": "600 bps",
                "emergency_capable": True,
                "backup_power": True,
                "last_maintenance": None
            },
            "INT_001": {
                "type": RadioType.INTERNAL,
                "name": "Internal Comms",
                "location": "Ship-wide",
                "channels": 8,
                "status": "online",
                "active_stations": 12,
                "emergency_capable": True,
                "backup_power": True,
                "last_maintenance": None
            },
            "EPB_001": {
                "type": RadioType.EMERGENCY,
                "name": "Emergency Position Beacon",
                "location": "Bridge",
                "frequency": "406 MHz",
                "status": "standby",
                "battery_level": 95,
                "gps_capable": True,
                "auto_activation": True,
                "last_test": None
            }
        }
    
    def _initialize_channels(self) -> Dict[str, Dict]:
        """Initialize communication channels configuration."""
        return {
            "vhf_channels": {
                "16": {"name": "Distress/Safety/Calling", "priority": "distress", "monitoring": True},
                "6": {"name": "Ship-to-Ship Safety", "priority": "safety", "monitoring": True},
                "13": {"name": "Bridge-to-Bridge", "priority": "safety", "monitoring": True},
                "9": {"name": "Port Operations", "priority": "routine", "monitoring": False},
                "12": {"name": "Port Operations", "priority": "routine", "monitoring": False},
                "14": {"name": "Port Operations", "priority": "routine", "monitoring": False},
                "67": {"name": "Ship-to-Ship", "priority": "routine", "monitoring": False},
                "70": {"name": "DSC (Digital Selective Calling)", "priority": "distress", "monitoring": True}
            },
            "hf_frequencies": {
                "2182": {"name": "Distress/Safety", "priority": "distress", "band": "MF"},
                "8291": {"name": "Safety/Working", "priority": "safety", "band": "HF"},
                "12290": {"name": "Safety/Working", "priority": "safety", "band": "HF"},
                "16420": {"name": "Safety/Working", "priority": "safety", "band": "HF"}
            },
            "internal_channels": {
                "1": {"name": "Bridge", "stations": ["Bridge Main", "Bridge Wing"]},
                "2": {"name": "Engine", "stations": ["Engine Control", "Engine Room"]},
                "3": {"name": "Deck", "stations": ["Deck House", "Deck Stations"]},
                "4": {"name": "Emergency", "stations": ["All Stations"]},
                "5": {"name": "Cargo", "stations": ["Cargo Control", "Cargo Holds"]},
                "6": {"name": "Galley", "stations": ["Galley", "Mess Hall"]},
                "7": {"name": "Security", "stations": ["Security Office", "Patrol"]},
                "8": {"name": "Medical", "stations": ["Medical Bay", "First Aid"]}
            }
        }
    
    def _initialize_emergency_contacts(self) -> Dict[str, Dict]:
        """Initialize emergency contact database."""
        return {
            "coast_guard": {
                "name": "Coast Guard",
                "vhf_channel": 16,
                "hf_frequency": "2182 kHz",
                "phone": "+1-xxx-xxx-xxxx",
                "priority": CommunicationPriority.DISTRESS,
                "response_time": "immediate",
                "coverage_area": "regional"
            },
            "port_authority": {
                "name": "Port Authority",
                "vhf_channel": 12,
                "phone": "+1-xxx-xxx-xxxx",
                "priority": CommunicationPriority.SAFETY,
                "response_time": "15 minutes",
                "coverage_area": "port"
            },
            "shipping_company": {
                "name": "Shipping Company Operations",
                "satellite_number": "+870-xxx-xxx-xxx",
                "email": "operations@company.com",
                "priority": CommunicationPriority.ROUTINE,
                "response_time": "30 minutes",
                "coverage_area": "global"
            },
            "medical_assistance": {
                "name": "Maritime Medical Advisory",
                "hf_frequency": "8291 kHz",
                "satellite_number": "+870-xxx-xxx-xxx",
                "priority": CommunicationPriority.URGENCY,
                "response_time": "immediate",
                "coverage_area": "global"
            },
            "search_rescue": {
                "name": "Search and Rescue",
                "vhf_channel": 16,
                "hf_frequency": "2182 kHz",
                "priority": CommunicationPriority.DISTRESS,
                "response_time": "immediate",
                "coverage_area": "regional"
            }
        }
    
    async def register_integration_callback(self, callback):
        """Register callback for system integration."""
        self.integration_callbacks.append(callback)
        logger.debug(f"Integration callback registered: {callback.__name__}")
    
    async def send_distress_call(self, nature_of_distress: str, position: Dict = None) -> Dict:
        """
        Send emergency distress call using multiple communication methods.
        
        Args:
            nature_of_distress: Description of the emergency
            position: Ship position (lat/lon)
            
        Returns:
            Dict with distress call result
        """
        logger.critical(f"📡 DISTRESS CALL INITIATED: {nature_of_distress}")
        
        # Update system status
        self.status = SystemStatus.EMERGENCY
        
        # Create distress message
        distress_message = self._create_distress_message(nature_of_distress, position)
        
        # Send on multiple channels for redundancy
        transmission_results = []
        
        # VHF Channel 16 (Primary distress frequency)
        vhf_result = await self._transmit_vhf_distress(distress_message)
        transmission_results.append(vhf_result)
        
        # HF 2182 kHz (Secondary distress frequency)
        hf_result = await self._transmit_hf_distress(distress_message)
        transmission_results.append(hf_result)
        
        # Satellite communication
        sat_result = await self._transmit_satellite_distress(distress_message)
        transmission_results.append(sat_result)
        
        # Activate EPIRB if available
        epirb_result = await self._activate_epirb()
        transmission_results.append(epirb_result)
        
        # Log distress call
        call_id = f"DIST-{int(datetime.utcnow().timestamp())}"
        
        self.active_communications[call_id] = {
            "type": "distress_call",
            "nature": nature_of_distress,
            "position": position,
            "start_time": datetime.utcnow(),
            "status": "transmitted",
            "transmission_results": transmission_results,
            "acknowledgments": []
        }
        
        # Notify integrated systems
        await self._notify_integrated_systems("distress_call", {
            "call_id": call_id,
            "nature": nature_of_distress,
            "position": position,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Log critical event
        await self._log_event(
            event_type="DISTRESS_CALL_SENT",
            severity=EventSeverity.EMERGENCY,
            message=f"Distress call sent: {nature_of_distress}",
            additional_data=json.dumps({
                "call_id": call_id,
                "transmissions": len(transmission_results),
                "position": position
            })
        )
        
        return {
            "success": True,
            "call_id": call_id,
            "nature_of_distress": nature_of_distress,
            "position": position,
            "transmission_results": transmission_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _create_distress_message(self, nature: str, position: Dict = None) -> str:
        """Create standardized distress message."""
        message_parts = [
            "MAYDAY MAYDAY MAYDAY",
            f"THIS IS MV SHIP_NAME MV SHIP_NAME MV SHIP_NAME",
            f"MAYDAY MV SHIP_NAME"
        ]
        
        if position:
            message_parts.append(f"POSITION {position.get('latitude', 'UNKNOWN')} {position.get('longitude', 'UNKNOWN')}")
        
        message_parts.extend([
            f"NATURE OF DISTRESS: {nature}",
            "REQUIRE IMMEDIATE ASSISTANCE",
            "OVER"
        ])
        
        return " ".join(message_parts)
    
    async def _transmit_vhf_distress(self, message: str) -> Dict:
        """Transmit distress call on VHF Channel 16."""
        radio = self.radios.get("VHF_001")
        if not radio or radio["status"] != "online":
            return {"method": "VHF Ch 16", "status": "failed", "reason": "Radio offline"}
        
        logger.critical("📡 Transmitting VHF distress call on Channel 16")
        
        # Switch to Channel 16 if not already
        radio["current_channel"] = 16
        
        # Simulate transmission
        await asyncio.sleep(2)
        
        return {
            "method": "VHF Channel 16",
            "status": "transmitted",
            "power": radio["power_output"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _transmit_hf_distress(self, message: str) -> Dict:
        """Transmit distress call on HF 2182 kHz."""
        radio = self.radios.get("HF_001")
        if not radio or radio["status"] != "online":
            return {"method": "HF 2182 kHz", "status": "failed", "reason": "Radio offline"}
        
        logger.critical("📡 Transmitting HF distress call on 2182 kHz")
        
        # Switch to distress frequency
        radio["current_frequency"] = "2182 kHz"
        
        # Simulate transmission
        await asyncio.sleep(3)
        
        return {
            "method": "HF 2182 kHz",
            "status": "transmitted",
            "power": radio["power_output"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _transmit_satellite_distress(self, message: str) -> Dict:
        """Transmit distress call via satellite."""
        satellite = self.radios.get("SAT_001")
        if not satellite or satellite["status"] != "online":
            return {"method": "Satellite", "status": "failed", "reason": "Satellite offline"}
        
        logger.critical("📡 Transmitting satellite distress message")
        
        # Simulate satellite transmission
        await asyncio.sleep(5)
        
        return {
            "method": "Inmarsat Satellite",
            "status": "transmitted",
            "signal_strength": satellite["signal_strength"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _activate_epirb(self) -> Dict:
        """Activate Emergency Position Indicating Radio Beacon."""
        epirb = self.radios.get("EPB_001")
        if not epirb:
            return {"method": "EPIRB", "status": "not_available", "reason": "EPIRB not installed"}
        
        logger.critical("📡 Activating Emergency Position Beacon (EPIRB)")
        
        epirb["status"] = "transmitting"
        
        return {
            "method": "EPIRB 406 MHz",
            "status": "activated",
            "frequency": epirb["frequency"],
            "gps_position": epirb["gps_capable"],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def send_safety_message(self, message: str, recipients: List[str] = None,
                                 priority: CommunicationPriority = CommunicationPriority.SAFETY) -> Dict:
        """
        Send safety message to specified recipients.
        
        Args:
            message: Safety message content
            recipients: List of recipient types
            priority: Message priority
            
        Returns:
            Dict with transmission result
        """
        if recipients is None:
            recipients = ["coast_guard"]
        
        logger.warning(f"📡 Sending safety message: {message[:50]}...")
        
        # Create message ID
        message_id = f"SAFE-{int(datetime.utcnow().timestamp())}"
        
        # Select appropriate communication method based on priority
        transmission_results = []
        
        for recipient in recipients:
            if recipient in self.emergency_contacts:
                contact = self.emergency_contacts[recipient]
                result = await self._send_to_contact(message, contact, priority)
                transmission_results.append(result)
        
        # Log message
        self.message_log.append({
            "message_id": message_id,
            "type": "safety",
            "content": message,
            "recipients": recipients,
            "priority": priority,
            "timestamp": datetime.utcnow(),
            "transmission_results": transmission_results
        })
        
        # Log event
        await self._log_event(
            event_type="SAFETY_MESSAGE_SENT",
            severity=EventSeverity.WARNING,
            message=f"Safety message sent: {message[:100]}",
            additional_data=json.dumps({
                "message_id": message_id,
                "recipients": recipients,
                "priority": priority.value
            })
        )
        
        return {
            "success": True,
            "message_id": message_id,
            "recipients": recipients,
            "transmission_results": transmission_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _send_to_contact(self, message: str, contact: Dict, 
                              priority: CommunicationPriority) -> Dict:
        """Send message to specific contact using appropriate method."""
        # Select communication method based on priority and availability
        if priority == CommunicationPriority.DISTRESS:
            if "vhf_channel" in contact:
                return await self._send_vhf_message(message, contact["vhf_channel"])
            elif "hf_frequency" in contact:
                return await self._send_hf_message(message, contact["hf_frequency"])
        
        elif priority in [CommunicationPriority.URGENCY, CommunicationPriority.SAFETY]:
            if "satellite_number" in contact:
                return await self._send_satellite_message(message, contact["satellite_number"])
            elif "vhf_channel" in contact:
                return await self._send_vhf_message(message, contact["vhf_channel"])
        
        # Default to routine communication
        if "phone" in contact:
            return await self._send_phone_message(message, contact["phone"])
        elif "email" in contact:
            return await self._send_email_message(message, contact["email"])
        
        return {"recipient": contact["name"], "status": "failed", "reason": "No available communication method"}
    
    async def _send_vhf_message(self, message: str, channel: int) -> Dict:
        """Send VHF radio message."""
        await asyncio.sleep(1)  # Simulate transmission time
        return {
            "method": f"VHF Channel {channel}",
            "status": "transmitted",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _send_hf_message(self, message: str, frequency: str) -> Dict:
        """Send HF radio message."""
        await asyncio.sleep(2)  # Simulate transmission time
        return {
            "method": f"HF {frequency}",
            "status": "transmitted",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _send_satellite_message(self, message: str, number: str) -> Dict:
        """Send satellite message."""
        await asyncio.sleep(3)  # Simulate transmission time
        return {
            "method": f"Satellite {number}",
            "status": "transmitted",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _send_phone_message(self, message: str, number: str) -> Dict:
        """Send phone message."""
        await asyncio.sleep(1)
        return {
            "method": f"Phone {number}",
            "status": "transmitted",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _send_email_message(self, message: str, email: str) -> Dict:
        """Send email message."""
        await asyncio.sleep(2)
        return {
            "method": f"Email {email}",
            "status": "transmitted",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_system_status(self) -> Dict:
        """Get current communication system status."""
        online_radios = sum(1 for r in self.radios.values() if r["status"] == "online")
        active_comms = len([c for c in self.active_communications.values() 
                          if c["status"] == "active"])
        
        return {
            "system_type": self.system_type.value,
            "status": self.status.value,
            "radios": self.radios,
            "total_radios": len(self.radios),
            "online_radios": online_radios,
            "active_communications": active_comms,
            "communication_details": self.active_communications,
            "emergency_contacts": self.emergency_contacts,
            "recent_messages": self.message_log[-10:],  # Last 10 messages
            "last_test": self.last_test.isoformat() if self.last_test else None,
            "performance_score": self._calculate_performance_score()
        }
    
    async def perform_system_test(self) -> Dict:
        """Perform communication system test."""
        logger.info("🧪 Performing communication system test")
        
        self.last_test = datetime.utcnow()
        test_results = {}
        
        # Test each radio
        for radio_id, radio in self.radios.items():
            # Simulate radio tests
            power_test = radio["status"] == "online"
            frequency_test = True  # Simulated
            reception_test = True  # Simulated
            backup_power_test = radio.get("backup_power", False)
            
            test_results[radio_id] = {
                "name": radio["name"],
                "type": radio["type"],
                "power_test": "PASS" if power_test else "FAIL",
                "frequency_test": "PASS" if frequency_test else "FAIL",
                "reception_test": "PASS" if reception_test else "FAIL",
                "backup_power_test": "PASS" if backup_power_test else "N/A",
                "overall": "PASS" if all([power_test, frequency_test, reception_test]) else "FAIL"
            }
        
        # Test emergency contacts
        contact_test_results = {}
        for contact_name, contact in self.emergency_contacts.items():
            # Simulate contact reachability test
            reachable = True  # Simulated
            response_time_ok = True  # Simulated
            
            contact_test_results[contact_name] = {
                "reachable": "PASS" if reachable else "FAIL",
                "response_time": "PASS" if response_time_ok else "FAIL",
                "priority": contact["priority"].value,
                "overall": "PASS" if reachable and response_time_ok else "FAIL"
            }
        
        # Log test completion
        await self._log_event(
            event_type="SYSTEM_TEST_COMPLETED",
            severity=EventSeverity.INFO,
            message="Communication system test completed",
            additional_data=json.dumps({
                "radio_results": test_results,
                "contact_results": contact_test_results
            })
        )
        
        return {
            "test_completed": True,
            "timestamp": self.last_test.isoformat(),
            "radio_results": test_results,
            "contact_results": contact_test_results,
            "overall_status": "PASS"
        }
    
    def _calculate_performance_score(self) -> float:
        """Calculate system performance score."""
        base_score = 100.0
        
        # Reduce score for offline radios
        offline_radios = sum(1 for r in self.radios.values() if r["status"] != "online")
        base_score -= offline_radios * 15
        
        # Reduce score if critical radios are offline
        critical_radios = ["VHF_001", "HF_001", "SAT_001"]
        for radio_id in critical_radios:
            if radio_id in self.radios and self.radios[radio_id]["status"] != "online":
                base_score -= 25
        
        # Reduce score if last test was too long ago
        if self.last_test:
            days_since_test = (datetime.utcnow() - self.last_test).days
            if days_since_test > 7:  # Weekly testing recommended
                base_score -= min(days_since_test - 7, 30)
        else:
            base_score -= 20  # No test performed
        
        return max(0, base_score)
    
    async def handle_emergency_event(self, event_type: str, event_data: Dict) -> Dict:
        """Handle emergency events with appropriate communication response."""
        logger.warning(f"📡 Communication system responding to emergency: {event_type}")
        
        # Determine communication response based on event type
        if event_type == "fire_alarm":
            message = f"FIRE ALARM ACTIVATED IN {event_data.get('zone', 'UNKNOWN LOCATION')}"
            return await self.send_safety_message(message, ["coast_guard", "port_authority"], 
                                                CommunicationPriority.URGENCY)
        
        elif event_type == "emergency_stop":
            message = f"EMERGENCY STOP ACTIVATED - {event_data.get('reason', 'UNKNOWN REASON')}"
            return await self.send_safety_message(message, ["coast_guard", "shipping_company"],
                                                CommunicationPriority.SAFETY)
        
        elif event_type == "man_overboard":
            position = event_data.get("position", {})
            return await self.send_distress_call("MAN OVERBOARD", position)
        
        elif event_type == "medical_emergency":
            message = f"MEDICAL EMERGENCY - REQUIRE MEDICAL ASSISTANCE"
            return await self.send_safety_message(message, ["medical_assistance", "coast_guard"],
                                                CommunicationPriority.URGENCY)
        
        # Default response for other emergencies
        message = f"EMERGENCY SITUATION: {event_type.upper()}"
        return await self.send_safety_message(message, ["coast_guard"], CommunicationPriority.SAFETY)
    
    async def _notify_integrated_systems(self, event_type: str, data: Dict):
        """Notify other systems of communication events."""
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