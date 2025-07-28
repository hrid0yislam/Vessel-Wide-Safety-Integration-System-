"""
Compliance Monitor
Maritime safety standards compliance monitoring and reporting system.

This system demonstrates understanding of:
- SOLAS (Safety of Life at Sea) regulations
- DNV (Det Norske Veritas) classification standards
- Maritime safety compliance requirements
- Automated compliance checking and reporting
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

from loguru import logger
from database.models import SystemType, SystemStatus, EventSeverity

class ComplianceStandard(str, Enum):
    SOLAS = "solas"
    DNV = "dnv"
    MARPOL = "marpol"
    ISM = "ism"
    ISPS = "isps"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    WARNING = "warning"
    PENDING = "pending"

class ComplianceMonitor:
    """
    Compliance Monitor for maritime safety standards.
    
    Monitors and reports compliance with international maritime
    safety standards including SOLAS, DNV, and other regulations.
    """
    
    def __init__(self):
        self.system_type = SystemType.COMPLIANCE
        self.status = SystemStatus.NORMAL
        self.standards = self._initialize_compliance_standards()
        self.compliance_checks = {}
        self.violations = []
        self.audit_trail = []
        self.certification_status = self._initialize_certifications()
        self.last_audit = None
        self.integration_callbacks = []
        
        logger.info("⚖️ Compliance Monitor initialized")
    
    def _initialize_compliance_standards(self) -> Dict[str, Dict]:
        """Initialize compliance standards and requirements."""
        return {
            ComplianceStandard.SOLAS: {
                "name": "Safety of Life at Sea Convention",
                "authority": "IMO",
                "chapters": {
                    "II-2": {
                        "name": "Fire Protection, Detection and Extinction",
                        "requirements": [
                            "fire_detection_coverage",
                            "fire_suppression_systems",
                            "escape_routes",
                            "fire_drills",
                            "fire_control_plans"
                        ]
                    },
                    "III": {
                        "name": "Life-Saving Appliances",
                        "requirements": [
                            "lifeboat_capacity",
                            "life_jacket_availability",
                            "emergency_signals",
                            "abandon_ship_drills"
                        ]
                    },
                    "IV": {
                        "name": "Radio Communications",
                        "requirements": [
                            "vhf_radio_coverage",
                            "distress_communication",
                            "bridge_communication",
                            "emergency_frequencies"
                        ]
                    },
                    "V": {
                        "name": "Safety of Navigation",
                        "requirements": [
                            "navigation_equipment",
                            "watchkeeping",
                            "voyage_planning",
                            "weather_routing"
                        ]
                    }
                },
                "inspection_frequency": 365,  # days
                "certification_validity": 1825  # 5 years
            },
            ComplianceStandard.DNV: {
                "name": "Det Norske Veritas Classification",
                "authority": "DNV GL",
                "categories": {
                    "hull_structure": {
                        "name": "Hull and Structure",
                        "requirements": [
                            "hull_integrity",
                            "watertight_bulkheads",
                            "structural_strength",
                            "corrosion_protection"
                        ]
                    },
                    "machinery": {
                        "name": "Machinery and Systems",
                        "requirements": [
                            "engine_reliability",
                            "power_systems",
                            "steering_gear",
                            "emergency_power"
                        ]
                    },
                    "safety_systems": {
                        "name": "Safety and Emergency Systems",
                        "requirements": [
                            "fire_safety_systems",
                            "emergency_shutdown",
                            "alarm_systems",
                            "emergency_equipment"
                        ]
                    }
                },
                "inspection_frequency": 365,
                "certification_validity": 1825
            },
            ComplianceStandard.ISM: {
                "name": "International Safety Management Code",
                "authority": "IMO",
                "elements": {
                    "safety_policy": "Safety and environmental protection policy",
                    "responsibilities": "Company responsibilities and authority",
                    "designated_person": "Designated person ashore",
                    "master_responsibility": "Master's responsibility and authority",
                    "resources": "Resources and personnel",
                    "ship_operations": "Plans for shipboard operations",
                    "emergency_preparedness": "Emergency preparedness",
                    "non_conformity": "Reports and analysis of non-conformities",
                    "maintenance": "Maintenance of ship and equipment",
                    "documentation": "Documentation",
                    "company_verification": "Company verification and review",
                    "certification": "Certification and periodic verification"
                },
                "audit_frequency": 1095,  # 3 years
                "certification_validity": 1825
            }
        }
    
    def _initialize_certifications(self) -> Dict[str, Dict]:
        """Initialize current certification status."""
        return {
            "safety_management_certificate": {
                "standard": ComplianceStandard.ISM,
                "issued_date": datetime(2023, 1, 15),
                "expiry_date": datetime(2028, 1, 15),
                "status": ComplianceStatus.COMPLIANT,
                "issuing_authority": "Maritime Authority",
                "certificate_number": "SMC-2023-001"
            },
            "safety_radio_certificate": {
                "standard": ComplianceStandard.SOLAS,
                "issued_date": datetime(2023, 3, 10),
                "expiry_date": datetime(2024, 3, 10),
                "status": ComplianceStatus.WARNING,  # Expires soon
                "issuing_authority": "Telecommunications Authority",
                "certificate_number": "SRC-2023-045"
            },
            "class_certificate": {
                "standard": ComplianceStandard.DNV,
                "issued_date": datetime(2022, 8, 20),
                "expiry_date": datetime(2027, 8, 20),
                "status": ComplianceStatus.COMPLIANT,
                "issuing_authority": "DNV GL",
                "certificate_number": "DNV-2022-789"
            },
            "fire_safety_certificate": {
                "standard": ComplianceStandard.SOLAS,
                "issued_date": datetime(2023, 6, 5),
                "expiry_date": datetime(2024, 6, 5),
                "status": ComplianceStatus.COMPLIANT,
                "issuing_authority": "Port State Control",
                "certificate_number": "FSC-2023-123"
            }
        }
    
    async def register_integration_callback(self, callback):
        """Register callback for system integration."""
        self.integration_callbacks.append(callback)
        logger.debug(f"Integration callback registered: {callback.__name__}")
    
    async def perform_compliance_check(self, standard: ComplianceStandard,
                                     system_data: Dict = None) -> Dict:
        """
        Perform compliance check against specified standard.
        
        Args:
            standard: Compliance standard to check against
            system_data: Current system status data
            
        Returns:
            Dict with compliance check results
        """
        logger.info(f"⚖️ Performing compliance check: {standard.value}")
        
        check_id = f"CHK-{standard.value.upper()}-{int(datetime.utcnow().timestamp())}"
        check_results = []
        overall_status = ComplianceStatus.COMPLIANT
        
        if standard == ComplianceStandard.SOLAS:
            check_results = await self._check_solas_compliance(system_data)
        elif standard == ComplianceStandard.DNV:
            check_results = await self._check_dnv_compliance(system_data)
        elif standard == ComplianceStandard.ISM:
            check_results = await self._check_ism_compliance(system_data)
        
        # Determine overall status
        if any(result["status"] == ComplianceStatus.NON_COMPLIANT for result in check_results):
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif any(result["status"] == ComplianceStatus.WARNING for result in check_results):
            overall_status = ComplianceStatus.WARNING
        
        # Store compliance check
        self.compliance_checks[check_id] = {
            "standard": standard,
            "timestamp": datetime.utcnow(),
            "overall_status": overall_status,
            "check_results": check_results,
            "system_data_snapshot": system_data
        }
        
        # Log violations if any
        violations = [r for r in check_results if r["status"] != ComplianceStatus.COMPLIANT]
        if violations:
            await self._log_violations(standard, violations, check_id)
        
        # Log compliance check
        await self._log_event(
            event_type="COMPLIANCE_CHECK_COMPLETED",
            severity=EventSeverity.INFO if overall_status == ComplianceStatus.COMPLIANT else EventSeverity.WARNING,
            message=f"Compliance check completed: {standard.value} - {overall_status.value}",
            additional_data=json.dumps({
                "check_id": check_id,
                "violations_count": len(violations),
                "overall_status": overall_status.value
            })
        )
        
        return {
            "check_id": check_id,
            "standard": standard.value,
            "overall_status": overall_status.value,
            "total_checks": len(check_results),
            "violations": len(violations),
            "check_results": check_results,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_solas_compliance(self, system_data: Dict) -> List[Dict]:
        """Check SOLAS compliance requirements."""
        results = []
        
        # Chapter II-2: Fire Protection, Detection and Extinction
        fire_system = system_data.get("fire_detection", {}) if system_data else {}
        
        # Fire detection coverage
        fire_zones = fire_system.get("zones", {})
        required_zones = ["engine_room", "bridge", "crew_quarters", "cargo_hold"]
        covered_zones = [zone for zone in required_zones if zone in fire_zones]
        
        results.append({
            "requirement": "fire_detection_coverage",
            "description": "Fire detection system coverage in all required areas",
            "status": ComplianceStatus.COMPLIANT if len(covered_zones) == len(required_zones) else ComplianceStatus.NON_COMPLIANT,
            "details": f"Coverage: {len(covered_zones)}/{len(required_zones)} zones",
            "chapter": "II-2"
        })
        
        # Fire suppression systems
        suppression_systems = fire_system.get("suppression_systems", {})
        results.append({
            "requirement": "fire_suppression_systems",
            "description": "Adequate fire suppression systems installed",
            "status": ComplianceStatus.COMPLIANT if len(suppression_systems) >= 3 else ComplianceStatus.WARNING,
            "details": f"Systems installed: {len(suppression_systems)}",
            "chapter": "II-2"
        })
        
        # Chapter IV: Radio Communications
        comm_system = system_data.get("communication", {}) if system_data else {}
        radios = comm_system.get("radios", {})
        
        # VHF radio requirement
        vhf_radios = [r for r in radios.values() if r.get("type") == "vhf"]
        results.append({
            "requirement": "vhf_radio_coverage",
            "description": "VHF radio communication capability",
            "status": ComplianceStatus.COMPLIANT if len(vhf_radios) >= 2 else ComplianceStatus.NON_COMPLIANT,
            "details": f"VHF radios: {len(vhf_radios)}",
            "chapter": "IV"
        })
        
        # Distress communication
        emergency_radios = [r for r in radios.values() if r.get("emergency_capable")]
        results.append({
            "requirement": "distress_communication",
            "description": "Emergency distress communication capability",
            "status": ComplianceStatus.COMPLIANT if len(emergency_radios) >= 3 else ComplianceStatus.WARNING,
            "details": f"Emergency capable radios: {len(emergency_radios)}",
            "chapter": "IV"
        })
        
        return results
    
    async def _check_dnv_compliance(self, system_data: Dict) -> List[Dict]:
        """Check DNV classification compliance."""
        results = []
        
        # Safety and Emergency Systems
        emergency_system = system_data.get("emergency_stop", {}) if system_data else {}
        
        # Emergency shutdown capability
        emergency_zones = emergency_system.get("zone_status", {})
        results.append({
            "requirement": "emergency_shutdown",
            "description": "Emergency shutdown systems for all critical zones",
            "status": ComplianceStatus.COMPLIANT if len(emergency_zones) >= 5 else ComplianceStatus.WARNING,
            "details": f"Emergency stop zones: {len(emergency_zones)}",
            "category": "safety_systems"
        })
        
        # Fire safety systems integration
        fire_system = system_data.get("fire_detection", {}) if system_data else {}
        active_alarms = fire_system.get("active_alarms", 0)
        
        results.append({
            "requirement": "fire_safety_systems",
            "description": "Fire safety systems operational and integrated",
            "status": ComplianceStatus.COMPLIANT if active_alarms == 0 else ComplianceStatus.WARNING,
            "details": f"Active fire alarms: {active_alarms}",
            "category": "safety_systems"
        })
        
        # Alarm systems
        paga_system = system_data.get("paga", {}) if system_data else {}
        total_speakers = paga_system.get("total_speakers", 0)
        
        results.append({
            "requirement": "alarm_systems",
            "description": "General alarm and public address systems",
            "status": ComplianceStatus.COMPLIANT if total_speakers >= 30 else ComplianceStatus.WARNING,
            "details": f"Total speakers: {total_speakers}",
            "category": "safety_systems"
        })
        
        return results
    
    async def _check_ism_compliance(self, system_data: Dict) -> List[Dict]:
        """Check ISM Code compliance."""
        results = []
        
        # Safety and environmental protection policy
        results.append({
            "requirement": "safety_policy",
            "description": "Safety and environmental protection policy implemented",
            "status": ComplianceStatus.COMPLIANT,
            "details": "Policy documented and communicated",
            "element": "safety_policy"
        })
        
        # Emergency preparedness
        emergency_system = system_data.get("emergency_stop", {}) if system_data else {}
        performance_score = emergency_system.get("performance_score", 0)
        
        results.append({
            "requirement": "emergency_preparedness",
            "description": "Emergency preparedness procedures and drills",
            "status": ComplianceStatus.COMPLIANT if performance_score >= 85 else ComplianceStatus.WARNING,
            "details": f"Emergency system performance: {performance_score}%",
            "element": "emergency_preparedness"
        })
        
        # Maintenance of ship and equipment
        # Check system test frequencies
        systems_tested = 0
        total_systems = 5
        
        if system_data:
            for system_name in ["emergency_stop", "fire_detection", "cctv", "paga", "communication"]:
                system_info = system_data.get(system_name, {})
                if system_info.get("last_test"):
                    systems_tested += 1
        
        results.append({
            "requirement": "maintenance",
            "description": "Maintenance of ship and equipment according to schedule",
            "status": ComplianceStatus.COMPLIANT if systems_tested >= 4 else ComplianceStatus.WARNING,
            "details": f"Systems with recent tests: {systems_tested}/{total_systems}",
            "element": "maintenance"
        })
        
        return results
    
    async def _log_violations(self, standard: ComplianceStandard, violations: List[Dict], check_id: str):
        """Log compliance violations."""
        for violation in violations:
            violation_record = {
                "check_id": check_id,
                "standard": standard,
                "requirement": violation["requirement"],
                "description": violation["description"],
                "status": violation["status"],
                "details": violation["details"],
                "timestamp": datetime.utcnow(),
                "resolved": False
            }
            
            self.violations.append(violation_record)
            
            logger.warning(f"⚖️ Compliance violation: {standard.value} - {violation['requirement']}")
    
    async def check_certificate_validity(self) -> Dict:
        """Check validity of all certificates."""
        logger.info("⚖️ Checking certificate validity")
        
        certificate_status = {}
        warnings = []
        
        for cert_name, cert_info in self.certification_status.items():
            days_to_expiry = (cert_info["expiry_date"] - datetime.utcnow()).days
            
            if days_to_expiry < 0:
                status = ComplianceStatus.NON_COMPLIANT
                warnings.append(f"{cert_name} expired {abs(days_to_expiry)} days ago")
            elif days_to_expiry < 30:
                status = ComplianceStatus.WARNING
                warnings.append(f"{cert_name} expires in {days_to_expiry} days")
            else:
                status = ComplianceStatus.COMPLIANT
            
            certificate_status[cert_name] = {
                "status": status,
                "days_to_expiry": days_to_expiry,
                "expiry_date": cert_info["expiry_date"].isoformat(),
                "certificate_number": cert_info["certificate_number"]
            }
        
        # Log warnings if any
        if warnings:
            await self._log_event(
                event_type="CERTIFICATE_VALIDITY_WARNING",
                severity=EventSeverity.WARNING,
                message=f"Certificate validity warnings: {len(warnings)} certificates need attention",
                additional_data=json.dumps({"warnings": warnings})
            )
        
        return {
            "check_completed": True,
            "timestamp": datetime.utcnow().isoformat(),
            "certificates": certificate_status,
            "warnings": warnings,
            "total_certificates": len(certificate_status),
            "expired_certificates": len([c for c in certificate_status.values() 
                                       if c["status"] == ComplianceStatus.NON_COMPLIANT])
        }
    
    async def generate_compliance_report(self, standards: List[ComplianceStandard] = None) -> Dict:
        """Generate comprehensive compliance report."""
        if standards is None:
            standards = list(ComplianceStandard)
        
        logger.info("⚖️ Generating compliance report")
        
        report = {
            "report_id": f"RPT-{int(datetime.utcnow().timestamp())}",
            "generated_at": datetime.utcnow().isoformat(),
            "standards_checked": [s.value for s in standards],
            "certificate_status": await self.check_certificate_validity(),
            "recent_checks": [],
            "violations": [],
            "recommendations": []
        }
        
        # Get recent compliance checks
        recent_checks = sorted(
            [check for check in self.compliance_checks.values() 
             if check["timestamp"] > datetime.utcnow() - timedelta(days=30)],
            key=lambda x: x["timestamp"],
            reverse=True
        )[:10]
        
        report["recent_checks"] = [
            {
                "standard": check["standard"].value,
                "timestamp": check["timestamp"].isoformat(),
                "status": check["overall_status"].value,
                "violations": len([r for r in check["check_results"] 
                                 if r["status"] != ComplianceStatus.COMPLIANT])
            }
            for check in recent_checks
        ]
        
        # Get recent violations
        recent_violations = sorted(
            [v for v in self.violations if not v["resolved"] 
             and v["timestamp"] > datetime.utcnow() - timedelta(days=90)],
            key=lambda x: x["timestamp"],
            reverse=True
        )
        
        report["violations"] = [
            {
                "standard": v["standard"].value,
                "requirement": v["requirement"],
                "description": v["description"],
                "timestamp": v["timestamp"].isoformat(),
                "details": v["details"]
            }
            for v in recent_violations
        ]
        
        # Generate recommendations
        if recent_violations:
            report["recommendations"].append(
                "Address outstanding compliance violations to maintain certification status"
            )
        
        expiring_certs = [name for name, cert in report["certificate_status"]["certificates"].items()
                         if cert["days_to_expiry"] < 60]
        if expiring_certs:
            report["recommendations"].append(
                f"Renew certificates expiring soon: {', '.join(expiring_certs)}"
            )
        
        # Log report generation
        await self._log_event(
            event_type="COMPLIANCE_REPORT_GENERATED",
            severity=EventSeverity.INFO,
            message=f"Compliance report generated: {len(recent_violations)} violations, {len(expiring_certs)} expiring certificates",
            additional_data=json.dumps({
                "report_id": report["report_id"],
                "standards": [s.value for s in standards]
            })
        )
        
        return report
    
    async def get_system_status(self) -> Dict:
        """Get current compliance monitor status."""
        recent_checks = len([c for c in self.compliance_checks.values() 
                           if c["timestamp"] > datetime.utcnow() - timedelta(days=7)])
        unresolved_violations = len([v for v in self.violations if not v["resolved"]])
        
        return {
            "system_type": self.system_type.value,
            "status": self.status.value,
            "standards_monitored": [s.value for s in ComplianceStandard],
            "total_compliance_checks": len(self.compliance_checks),
            "recent_checks": recent_checks,
            "unresolved_violations": unresolved_violations,
            "certification_status": self.certification_status,
            "last_audit": self.last_audit.isoformat() if self.last_audit else None,
            "performance_score": self._calculate_performance_score()
        }
    
    def _calculate_performance_score(self) -> float:
        """Calculate compliance performance score."""
        base_score = 100.0
        
        # Reduce score for unresolved violations
        unresolved_violations = len([v for v in self.violations if not v["resolved"]])
        base_score -= unresolved_violations * 10
        
        # Reduce score for expired certificates
        expired_certs = len([cert for cert in self.certification_status.values()
                           if cert["expiry_date"] < datetime.utcnow()])
        base_score -= expired_certs * 25
        
        # Reduce score for certificates expiring soon
        expiring_soon = len([cert for cert in self.certification_status.values()
                           if 0 < (cert["expiry_date"] - datetime.utcnow()).days < 30])
        base_score -= expiring_soon * 10
        
        return max(0, base_score)
    
    async def _notify_integrated_systems(self, event_type: str, data: Dict):
        """Notify other systems of compliance events."""
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