#!/usr/bin/env python3
"""
PLC Communication Demo (No Real PLC Required)
Demonstrates how Python and CODESYS PLC would communicate

This script simulates the communication without needing a real PLC,
so you can see how it would work in practice.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any

class MockPLCData:
    """Simulates PLC data for demonstration"""
    
    def __init__(self):
        # Simulate PLC memory values
        self.plc_memory = {
            # Boolean values (Coils)
            "system_running": True,
            "emergency_active": False,
            "fire_alarm_active": False,
            "system_healthy": True,
            "emergency_light": False,
            "alarm_bell": False,
            "safety_relay": True,
            
            # Input commands from Python
            "sim_emergency_button": False,
            "sim_fire_detector": False,
            "sim_reset_button": False,
            "maintenance_mode": False,
            
            # String/Numeric values
            "operator_message": "Ship Safety System: ALL NORMAL",
            "remote_command": "",
            "system_runtime": 0,
            "event_counter": 0
        }
        
        self.start_time = time.time()
    
    def update_plc_logic(self):
        """Simulate PLC logic running"""
        # Update runtime
        self.plc_memory["system_runtime"] = int(time.time() - self.start_time)
        
        # Emergency Stop Logic (like our CODESYS function block)
        if self.plc_memory["sim_emergency_button"]:
            self.plc_memory["emergency_active"] = True
            self.plc_memory["system_healthy"] = False
            self.plc_memory["emergency_light"] = True
            self.plc_memory["safety_relay"] = False
            self.plc_memory["operator_message"] = "EMERGENCY STOP ACTIVATED!"
        
        # Fire Detection Logic
        elif self.plc_memory["sim_fire_detector"]:
            self.plc_memory["fire_alarm_active"] = True
            self.plc_memory["system_healthy"] = False
            self.plc_memory["alarm_bell"] = True
            self.plc_memory["emergency_light"] = True
            self.plc_memory["operator_message"] = "FIRE ALARM ACTIVE - EVACUATE!"
        
        # Reset Logic
        elif self.plc_memory["sim_reset_button"]:
            if not self.plc_memory["sim_emergency_button"] and not self.plc_memory["sim_fire_detector"]:
                # Reset all alarms
                self.plc_memory["emergency_active"] = False
                self.plc_memory["fire_alarm_active"] = False
                self.plc_memory["system_healthy"] = True
                self.plc_memory["emergency_light"] = False
                self.plc_memory["alarm_bell"] = False
                self.plc_memory["safety_relay"] = True
                self.plc_memory["operator_message"] = "System Reset Complete - ALL NORMAL"
                self.plc_memory["event_counter"] += 1
        
        # Maintenance Mode
        elif self.plc_memory["maintenance_mode"]:
            self.plc_memory["operator_message"] = "System in MAINTENANCE MODE"
        
        # Normal Operation
        else:
            if not self.plc_memory["emergency_active"] and not self.plc_memory["fire_alarm_active"]:
                self.plc_memory["system_healthy"] = True
                self.plc_memory["emergency_light"] = False
                self.plc_memory["alarm_bell"] = False
                self.plc_memory["safety_relay"] = True
                self.plc_memory["operator_message"] = "Ship Safety System: ALL NORMAL"

class PLCCommunicationDemo:
    """
    Demonstrates how Python would communicate with CODESYS PLC
    
    This shows the communication patterns without needing a real PLC
    """
    
    def __init__(self):
        self.mock_plc = MockPLCData()
        self.connected = False
        print("🎭 PLC Communication Demo (Simulated)")
        print("📝 This shows how Python ↔ CODESYS communication would work")
    
    async def connect_to_plc(self) -> bool:
        """Simulate connecting to PLC"""
        print("🔄 Connecting to PLC...")
        await asyncio.sleep(1)  # Simulate connection time
        
        self.connected = True
        print("✅ Connected to simulated PLC")
        return True
    
    async def read_plc_status(self) -> Dict[str, Any]:
        """Simulate reading data from PLC"""
        if not self.connected:
            return {"error": "Not connected to PLC"}
        
        # Update PLC logic first
        self.mock_plc.update_plc_logic()
        
        # Return current PLC status
        return {
            "system_running": self.mock_plc.plc_memory["system_running"],
            "emergency_active": self.mock_plc.plc_memory["emergency_active"],
            "fire_alarm_active": self.mock_plc.plc_memory["fire_alarm_active"],
            "system_healthy": self.mock_plc.plc_memory["system_healthy"],
            "emergency_light": self.mock_plc.plc_memory["emergency_light"],
            "alarm_bell": self.mock_plc.plc_memory["alarm_bell"],
            "safety_relay": self.mock_plc.plc_memory["safety_relay"],
            "operator_message": self.mock_plc.plc_memory["operator_message"],
            "system_runtime": self.mock_plc.plc_memory["system_runtime"],
            "event_counter": self.mock_plc.plc_memory["event_counter"]
        }
    
    async def send_command_to_plc(self, commands: Dict[str, Any]) -> bool:
        """Simulate sending commands to PLC"""
        if not self.connected:
            print("❌ Cannot send commands - not connected to PLC")
            return False
        
        print(f"📤 Sending commands to PLC: {commands}")
        
        # Update PLC memory with commands
        for cmd_name, value in commands.items():
            if cmd_name in self.mock_plc.plc_memory:
                self.mock_plc.plc_memory[cmd_name] = value
                print(f"   ✅ {cmd_name} = {value}")
            else:
                print(f"   ❌ Unknown command: {cmd_name}")
        
        return True
    
    async def emergency_stop_from_web(self):
        """Simulate emergency stop from web interface"""
        print("\n🚨 WEB INTERFACE: Emergency Stop Button Clicked!")
        await self.send_command_to_plc({
            "sim_emergency_button": True,
            "remote_command": "EMERGENCY_STOP"
        })
    
    async def fire_alarm_from_web(self, zone: str):
        """Simulate fire alarm from web interface"""
        print(f"\n🔥 WEB INTERFACE: Fire Alarm Triggered in {zone}!")
        await self.send_command_to_plc({
            "sim_fire_detector": True,
            "remote_command": f"FIRE_ALARM_{zone}"
        })
    
    async def reset_systems_from_web(self):
        """Simulate system reset from web interface"""
        print("\n🔄 WEB INTERFACE: System Reset Button Clicked!")
        await self.send_command_to_plc({
            "sim_reset_button": True,
            "sim_emergency_button": False,  # Release emergency button
            "sim_fire_detector": False,     # Clear fire detector
            "remote_command": "SYSTEM_RESET"
        })
    
    async def maintenance_mode_from_web(self, enable: bool):
        """Simulate maintenance mode toggle"""
        mode_text = "ENABLED" if enable else "DISABLED"
        print(f"\n🔧 WEB INTERFACE: Maintenance Mode {mode_text}!")
        await self.send_command_to_plc({
            "maintenance_mode": enable,
            "remote_command": f"MAINTENANCE_{mode_text}"
        })
    
    def print_status_table(self, status: Dict):
        """Print PLC status in a nice table format"""
        print("\n" + "="*60)
        print("📊 CURRENT PLC STATUS")
        print("="*60)
        
        print(f"🖥️  System Running:     {status.get('system_running', 'Unknown')}")
        print(f"🚨 Emergency Active:   {status.get('emergency_active', 'Unknown')}")
        print(f"🔥 Fire Alarm:         {status.get('fire_alarm_active', 'Unknown')}")
        print(f"💚 System Healthy:     {status.get('system_healthy', 'Unknown')}")
        print(f"💡 Emergency Light:    {status.get('emergency_light', 'Unknown')}")
        print(f"🔔 Alarm Bell:         {status.get('alarm_bell', 'Unknown')}")
        print(f"⚡ Safety Relay:       {status.get('safety_relay', 'Unknown')}")
        print(f"⏱️  Runtime:            {status.get('system_runtime', 0)} seconds")
        print(f"📝 Events:             {status.get('event_counter', 0)}")
        print(f"💬 Message:            {status.get('operator_message', 'No message')}")
        print("="*60)

async def run_communication_demo():
    """
    Complete demonstration of Python ↔ PLC communication
    
    This shows exactly how the web dashboard would control
    the CODESYS PLC in a real ship safety system.
    """
    
    print("🚢 Ship Safety System Communication Demo")
    print("=" * 50)
    
    # Create communication bridge
    bridge = PLCCommunicationDemo()
    
    # Connect to PLC
    if await bridge.connect_to_plc():
        
        print("\n🎬 Starting Communication Demo Sequence...")
        
        # === SCENARIO 1: Normal Operation ===
        print("\n📍 SCENARIO 1: Normal System Operation")
        await asyncio.sleep(1)
        status = await bridge.read_plc_status()
        bridge.print_status_table(status)
        
        # === SCENARIO 2: Emergency Stop from Web ===
        print("\n📍 SCENARIO 2: Emergency Stop Triggered from Web Dashboard")
        await bridge.emergency_stop_from_web()
        await asyncio.sleep(2)
        status = await bridge.read_plc_status()
        bridge.print_status_table(status)
        
        # === SCENARIO 3: Fire Alarm from Web ===
        print("\n📍 SCENARIO 3: Fire Alarm Triggered from Web Dashboard")
        await bridge.fire_alarm_from_web("Engine Room")
        await asyncio.sleep(2)
        status = await bridge.read_plc_status()
        bridge.print_status_table(status)
        
        # === SCENARIO 4: System Reset from Web ===
        print("\n📍 SCENARIO 4: System Reset from Web Dashboard")
        await bridge.reset_systems_from_web()
        await asyncio.sleep(3)
        status = await bridge.read_plc_status()
        bridge.print_status_table(status)
        
        # === SCENARIO 5: Maintenance Mode ===
        print("\n📍 SCENARIO 5: Enable Maintenance Mode")
        await bridge.maintenance_mode_from_web(True)
        await asyncio.sleep(2)
        status = await bridge.read_plc_status()
        bridge.print_status_table(status)
        
        # === SCENARIO 6: Return to Normal ===
        print("\n📍 SCENARIO 6: Disable Maintenance Mode - Return to Normal")
        await bridge.maintenance_mode_from_web(False)
        await asyncio.sleep(2)
        status = await bridge.read_plc_status()
        bridge.print_status_table(status)
        
        print("\n🎉 Communication Demo Complete!")
        print("\n💡 This demonstrates how your Python web system")
        print("   would control and monitor the CODESYS PLC in real-time!")
        
    else:
        print("❌ Could not establish communication")

if __name__ == "__main__":
    print("🎭 PLC Communication Demonstration")
    print("📚 Educational simulation - no real PLC required")
    print("🔄 Starting demo...")
    
    # Run the complete demo
    asyncio.run(run_communication_demo()) 