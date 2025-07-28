# Vessel-Wide Safety Integration System

## 🚢 Maritime Safety Systems Engineering Platform

A comprehensive vessel-wide safety integration system demonstrating industrial automation, PLC programming, and maritime safety compliance. This project showcases the complete integration of safety-critical systems aboard specialized vessels, following SOLAS and DNV maritime regulations.

## 🎯 Project Overview

This system demonstrates the core competencies required for maritime electrical safety systems engineering, including:

- **Vessel-wide system integration** - Coordinated safety systems across multiple zones
- **PLC programming and automation** - CODESYS implementation with IEC 61131-3 standards
- **Maritime regulatory compliance** - SOLAS, DNV, and international safety standards
- **Real-time data processing** - Authentic maritime sensor simulation and monitoring
- **Emergency response coordination** - Automated safety protocols and fail-safe design

## ⚡ Key Safety Systems

### 🔴 Emergency Stop System
- Multi-zone emergency stop coordination
- Fail-safe logic with safety relay integration
- Zone-based isolation and recovery procedures
- Compliance with maritime safety standards

### 🔥 Fire Detection & Suppression
- Multi-zone fire detection with smoke, heat, and flame sensors
- Automated pre-alarm and suppression sequences
- Integration with vessel ventilation and door control systems
- Real-time fire spread monitoring and containment

### 📹 CCTV Surveillance System
- Vessel-wide camera network with zone coverage
- Motion detection and automated tracking
- Integration with emergency response protocols
- Remote monitoring and recording capabilities

### 📢 PAGA Communication System
- Public Address and General Alarm coordination
- Emergency evacuation announcements
- Zone-specific messaging and alerts
- Integration with bridge communication systems

### 📡 Communication Systems
- VHF and satellite radio integration
- Emergency communication protocols
- Distress signal automation
- Maritime traffic coordination

### 📋 Compliance Monitoring
- Real-time regulatory compliance checking
- Automated safety audit trails
- Performance metrics and reporting
- DNV and SOLAS standard verification

## 🛠️ Technology Stack

### Industrial Automation
- **CODESYS PLC Programming** - IEC 61131-3 compliant function blocks
- **Modbus TCP Communication** - Industrial protocol for system coordination
- **Safety Controller Integration** - Fail-safe logic and emergency circuits

### Backend Systems
- **FastAPI** - High-performance web framework for real-time APIs
- **SQLAlchemy** - Database ORM for event logging and system states
- **WebSockets** - Real-time communication to monitoring dashboard
- **Asyncio** - Asynchronous processing for concurrent safety operations

### Data Management
- **SQLite** - Embedded database for system events and historical data
- **NumPy** - Numerical processing for sensor data analysis
- **Time-series Analytics** - Historical performance monitoring and trends

### External Integration
- **Maritime APIs** - Real-time weather, vessel traffic, and port data
- **Sensor Simulation** - Realistic maritime sensor data generation
- **Environmental Effects** - Weather impact on system performance

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Safety Management Layer                  │
├─────────────────────────────────────────────────────────────┤
│  Emergency Stop │ Fire Detection │ CCTV │ PAGA │ Comm │ Comp │
├─────────────────────────────────────────────────────────────┤
│                  PLC Integration Layer                      │
│              (CODESYS + Modbus TCP)                        │
├─────────────────────────────────────────────────────────────┤
│                 Data Processing Layer                       │
│           (Real-time + Historical Analytics)               │
├─────────────────────────────────────────────────────────────┤
│                   Database Layer                           │
│              (Events + States + Compliance)                │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- CODESYS Development System (for PLC integration)
- Modbus TCP-enabled PLC (optional for hardware testing)

### Installation
```bash
# Clone the repository
git clone https://github.com/hrid0yislam/Vessel-Wide-Safety-Integration-System-.git
cd Vessel-Wide-Safety-Integration-System-

# Install dependencies
pip install -r requirements.txt

# Run the main application
python main.py
```

### Access the System
- **Web Dashboard:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **WebSocket Monitoring:** Real-time system status updates

## 📁 Project Structure

```
vessel-wide-safety-integration/
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
│
├── database/                        # Data management modules
│   ├── models.py                   # Database schemas and ORM models
│   ├── sensor_data_generator.py    # Maritime sensor simulation
│   ├── real_maritime_apis.py       # External API integration
│   ├── authentic_data_integrator.py # Real data coordination
│   ├── historical_data_manager.py  # Time-series analytics
│   └── realtime_enhancements.py    # Real-time data processing
│
├── systems/                         # Safety system modules
│   ├── safety_manager.py           # Central coordination hub
│   ├── emergency_stop.py           # Emergency stop system
│   ├── fire_detection.py           # Fire detection & alarm
│   ├── cctv_system.py             # Surveillance system
│   ├── paga_system.py             # Public announcement
│   ├── communication.py           # Radio systems
│   └── compliance_monitor.py      # Regulatory compliance
│
├── utils/                          # Utility modules
│   └── logger.py                  # System logging
│
├── integrate_authentic_data.py      # Real data integration demo
├── implement_realtime_enhancements.py # Enhancement instructions
└── plc_communication_demo.py       # PLC integration demo
```

## 🔧 Technical Highlights

### Maritime Engineering Excellence
- **Vessel-wide Integration:** Demonstrates complete safety system coordination
- **Regulatory Compliance:** SOLAS, DNV, and international maritime standards
- **Fail-safe Design:** Emergency circuits with redundancy and fault tolerance
- **Real-time Monitoring:** Continuous system health and performance tracking

### Industrial Automation Expertise
- **PLC Programming:** CODESYS function blocks with IEC 61131-3 standards
- **Communication Protocols:** Modbus TCP for industrial system integration
- **Safety Systems:** Emergency stop, fire suppression, and alarm coordination
- **Data Acquisition:** Precision sensor monitoring and control logic

### Software Engineering Skills
- **API Development:** RESTful services with real-time WebSocket communication
- **Database Design:** Optimized schemas for maritime operational data
- **Asynchronous Programming:** Concurrent processing for safety-critical operations
- **System Integration:** Seamless coordination between hardware and software layers

## 📊 Performance Features

- **Real-time Processing:** Sub-second response times for emergency scenarios
- **Scalable Architecture:** Modular design supporting vessel size variations
- **Historical Analytics:** Trend analysis and predictive maintenance insights
- **Compliance Reporting:** Automated audit trails and regulatory documentation

## 🌊 Maritime Applications

This system demonstrates capabilities essential for:
- **Offshore Vessels:** Oil & gas platforms, wind farms, research vessels
- **Commercial Ships:** Cargo vessels, cruise ships, ferry operations
- **Specialized Vessels:** Aquaculture ships, fishing vessels, naval applications
- **Port Operations:** Terminal safety systems, harbor management

## 🏆 Engineering Achievements

- **Comprehensive Safety Integration:** All major vessel safety systems coordinated
- **Standards Compliance:** Maritime regulatory requirements implementation
- **Real-world Simulation:** Authentic maritime sensor data and scenarios
- **Professional Documentation:** Complete system specifications and guides

## 🚀 Future Enhancements

- Integration with additional maritime APIs for enhanced authenticity
- Advanced predictive analytics for maintenance scheduling
- Mobile application for remote monitoring and control
- Integration with vessel management systems (VMS)
- Cybersecurity enhancements for maritime OT networks

## 📞 Contact

**Md Daudul Islam Bhuiyan Redoy**  
Electrical Engineer | Maritime Safety Systems Specialist  
📧 hridoyislam@hotmail.com  
🔗 [LinkedIn](http://www.linkedin.com/in/hrid0yislam) | [GitHub](https://github.com/hrid0yislam)

---

*This project demonstrates advanced maritime safety systems engineering capabilities, showcasing the integration of industrial automation, regulatory compliance, and vessel-wide safety coordination essential for modern shipbuilding and offshore operations.*
