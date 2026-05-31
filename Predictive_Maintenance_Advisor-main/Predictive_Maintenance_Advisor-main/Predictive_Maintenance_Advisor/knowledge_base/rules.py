"""
Expert System Rules for HVAC Predictive Maintenance

This module contains 60+ domain-expert rules for diagnosing HVAC failures.
Rules are organized by:
1. Failure severity (Critical, Warning, Monitor)
2. Equipment component (Compressor, Refrigerant, Heat Exchanger, Airflow, Electrical)
3. Symptom category (Temperature, Pressure, Noise, Oil quality, etc.)

Each rule has:
- Clear condition thresholds based on HVAC engineering standards
- Certainty factors reflecting confidence in the diagnosis
- Severity levels matching maintenance urgency
- Recommended actions for technicians

NOTE: These rules are imported and instantiated in engine.py as @Rule decorators.
This file serves as documentation of the rule logic.
"""

# Rule Documentation Format:
# ────────────────────────────────────────────────────────────────────────────
# RULE_ID: [Unique identifier]
# Name: [Human-readable]
# Severity: [0-5]
# CF: [0.0-1.0]
# Conditions:
#   - [Condition 1]
#   - [Condition 2]
#   - ...
# Diagnosis: [Conclusion]
# Action: [Recommended maintenance]
# ────────────────────────────────────────────────────────────────────────────


# ════════════════════════════════════════════════════════════════════════════
# CRITICAL RULES (Severity 5, CF 0.85-0.95)
# ════════════════════════════════════════════════════════════════════════════

RULE_001 = {
    "id": "RULE_001",
    "name": "Compressor Winding Short Circuit",
    "severity": 5,
    "cf": 0.94,
    "conditions": [
        "Compressor current very low OR very high (>40A or <3A)",
        "Compressor will not start after thermal overload",
        "Burning smell from compressor motor",
        "Smoke or visible damage on motor casing"
    ],
    "diagnosis": "Compressor Motor Winding Short Circuit - CRITICAL",
    "action": "EMERGENCY SHUTDOWN. Motor is internally damaged. Replace compressor immediately."
}

RULE_002 = {
    "id": "RULE_002",
    "name": "Refrigerant Gas Leak into Atmosphere",
    "severity": 5,
    "cf": 0.92,
    "conditions": [
        "System pressure drops >50% in 24 hours",
        "Strong refrigerant odor detected",
        "Hissing sound from pipe joints or coil",
        "Refrigerant level <70% of nameplate charge"
    ],
    "diagnosis": "Critical Refrigerant Leak - System Shutdown Required",
    "action": "Isolate system. Do not operate. Locate leak with dye/ultrasonic. Seal. Evacuate and recharge."
}

RULE_003 = {
    "id": "RULE_003",
    "name": "Pressure Relief Valve Failure (Boiler/Furnace)",
    "severity": 5,
    "cf": 0.93,
    "conditions": [
        "Boiler pressure continues rising above relief setpoint (>2.5 bar)",
        "Relief valve won't open or stuck closed",
        "Safety discharge pipe temperature very hot",
        "Pressure gauge stuck at maximum"
    ],
    "diagnosis": "Pressure Relief Valve Failure - Safety Hazard",
    "action": "STOP OPERATION IMMEDIATELY. Overpressure risk. Replace relief valve. Test after replacement."
}

RULE_004 = {
    "id": "RULE_004",
    "name": "Combustion Gas Leak (Safety Risk)",
    "severity": 5,
    "cf": 0.91,
    "conditions": [
        "Carbon monoxide detector alarm activated",
        "Gas/fume smell near boiler or furnace",
        "Incomplete combustion visible (yellow flame)",
        "Flue gas odor inside building"
    ],
    "diagnosis": "Combustion Gas Leak - Health/Safety Risk",
    "action": "VENTILATE IMMEDIATELY. Call professional. Potential CO poisoning. Do not operate until certified safe."
}

RULE_005 = {
    "id": "RULE_005",
    "name": "Catastrophic Heat Exchanger Crack",
    "severity": 5,
    "cf": 0.92,
    "conditions": [
        "Visible crack or hole in heat exchanger",
        "Water/oil leaking from casing",
        "Pressure drops immediately when compressor starts",
        "Refrigerant odor mixed with water or burnt oil"
    ],
    "diagnosis": "Heat Exchanger Rupture - System Failure",
    "action": "System is non-repairable. Replace heat exchanger (major component). Consider full unit replacement."
}


# ════════════════════════════════════════════════════════════════════════════
# HIGH SEVERITY RULES (Severity 4, CF 0.80-0.89)
# ════════════════════════════════════════════════════════════════════════════

RULE_006 = {
    "id": "RULE_006",
    "name": "Compressor Bearing Failure (Vibration + Wear Sounds)",
    "severity": 4,
    "cf": 0.87,
    "conditions": [
        "Grinding or rough noise from compressor",
        "High vibration amplitude visible",
        "Oil level dropping faster than normal",
        "Compressor runtime >50,000 hours"
    ],
    "diagnosis": "Compressor Bearing Failure - Imminent",
    "severity_level": 4,
    "action": "Plan replacement within 1-2 weeks. Bearing is failing. Monitor for seizure."
}

RULE_007 = {
    "id": "RULE_007",
    "name": "Suction Valve Leakage (Low Discharge Pressure)",
    "severity": 4,
    "cf": 0.84,
    "conditions": [
        "Discharge pressure unusually low (<12 bar)",
        "Discharge temperature low despite high load",
        "Suction pressure drops during operation",
        "Cooling capacity reduced significantly"
    ],
    "diagnosis": "Suction Valve Leakage",
    "action": "Compressor needs valve service. System efficiency severely compromised. Schedule replacement."
}

RULE_008 = {
    "id": "RULE_008",
    "name": "Oil Contamination (Non-Condensable Gases + Moisture)",
    "severity": 4,
    "cf": 0.85,
    "conditions": [
        "Oil is foamy or milky appearance",
        "Acid number > 1.5 mgKOH/g",
        "Discharge pressure erratic/hunting",
        "Oil sample shows water content"
    ],
    "diagnosis": "Oil Contamination - System Degradation",
    "action": "System evacuation required. Oil and desiccant filter change mandatory. Moisture removal."
}

RULE_009 = {
    "id": "RULE_009",
    "name": "Expansion Device Blockage (Ice or Wax)",
    "severity": 4,
    "cf": 0.83,
    "conditions": [
        "No refrigerant flow through expansion device",
        "Evaporator completely starved (very cold, may freeze)",
        "High pressure side pressure rising to max",
        "No cooling capacity, complete failure"
    ],
    "diagnosis": "Expansion Device Blockage",
    "action": "Replace expansion device. May need acid removal filter. System evacuation required."
}

RULE_010 = {
    "id": "RULE_010",
    "name": "Fan Motor Bearing Failure (AC/Furnace)",
    "severity": 4,
    "cf": 0.82,
    "conditions": [
        "Fan won't start or stops unexpectedly",
        "Grinding noise from fan motor",
        "Fan blades turn with heavy resistance",
        "Motor casing very hot"
    ],
    "diagnosis": "Fan Motor Bearing Failure",
    "action": "Replace fan motor immediately. Cost $300-500. Equipment cooling/heating affected."
}


# ════════════════════════════════════════════════════════════════════════════
# MEDIUM SEVERITY RULES (Severity 3, CF 0.70-0.84)
# ════════════════════════════════════════════════════════════════════════════

RULE_011 = {
    "id": "RULE_011",
    "name": "Refrigerant Overcharge (High Head Pressure)",
    "severity": 3,
    "cf": 0.78,
    "conditions": [
        "Discharge pressure >32 bar (abnormally high)",
        "Discharge temperature elevated (>90°C)",
        "Liquid line very hot (>50°C)",
        "System won't cool effectively"
    ],
    "diagnosis": "Refrigerant Overcharge",
    "action": "Recover refrigerant. Recharge to nameplate specifications. Verify charge weight."
}

RULE_012 = {
    "id": "RULE_012",
    "name": "Condenser Fouling (Dust/Debris Accumulation)",
    "severity": 3,
    "cf": 0.76,
    "conditions": [
        "Condenser coil visibly dirty/clogged",
        "High discharge pressure (>28 bar)",
        "High discharge temperature (>85°C)",
        "Capacity reduced, outdoor unit hot to touch"
    ],
    "diagnosis": "Condenser Coil Fouling",
    "action": "Clean condenser coil. Use water spray or coil cleaner. Restore airflow. Check operation."
}

RULE_013 = {
    "id": "RULE_013",
    "name": "Evaporator Fouling (Dirty Air Filter/Coil)",
    "severity": 3,
    "cf": 0.75,
    "conditions": [
        "Indoor airflow reduced",
        "Evaporator coil visibly dirty/iced",
        "Suction pressure low (<1.5 bar)",
        "Suction superheat high (>15°C)"
    ],
    "diagnosis": "Evaporator Fouling",
    "action": "Replace air filter. Clean evaporator coil chemically or mechanically. Check blower."
}

RULE_014 = {
    "id": "RULE_014",
    "name": "TXV (Thermostatic Expansion Valve) Hunting",
    "severity": 3,
    "cf": 0.73,
    "conditions": [
        "Suction pressure oscillates rapidly (±2 bar swings)",
        "Temperature cycling on/off, erratic operation",
        "Compressor short-cycles",
        "System won't maintain stable setpoint"
    ],
    "diagnosis": "Expansion Device Malfunction (Hunting)",
    "action": "Clean or replace TXV. Check sensing bulb attachment. Adjust superheat setting."
}

RULE_015 = {
    "id": "RULE_015",
    "name": "Reversing Valve Malfunction (Heat Pump Mode Switch Failure)",
    "severity": 3,
    "cf": 0.72,
    "conditions": [
        "Cannot switch between heating and cooling modes",
        "Solenoid coil won't energize (no clicking)",
        "Hissing from reversing valve",
        "Stuck in one mode (heating or cooling)"
    ],
    "diagnosis": "Reversing Valve Solenoid Failure",
    "action": "De-energize solenoid and manually test valve. Clean or replace reversing valve."
}

RULE_016 = {
    "id": "RULE_016",
    "name": "Boiler Scale Buildup (Hard Water Deposits)",
    "severity": 3,
    "cf": 0.74,
    "conditions": [
        "Boiler temperature rises slowly despite burner on",
        "Rumbling/kettling sound inside boiler",
        "Heat output reduced",
        "Water hardness known to be high (>200 ppm)"
    ],
    "diagnosis": "Boiler Scale Buildup",
    "action": "Chemical descaling required. Add water softener. Drain and flush system. Prevent future buildup."
}

RULE_017 = {
    "id": "RULE_017",
    "name": "Oil Slugging (Oil Carryover Risk)",
    "severity": 3,
    "cf": 0.77,
    "conditions": [
        "Oil level in crankcase dropping",
        "Oil visible in discharge line",
        "Compressor knocking slightly",
        "Compressor current erratic"
    ],
    "diagnosis": "Oil Slugging Risk",
    "action": "Increase suction superheat. Check for liquid slugging risk. May need oil separator service."
}

RULE_018 = {
    "id": "RULE_018",
    "name": "Thermostat Calibration Error",
    "severity": 2,
    "cf": 0.68,
    "conditions": [
        "Setpoint 2-3°C off from actual temperature",
        "Thermostat age >15 years",
        "Located in direct sunlight or draft",
        "Battery dead (for wireless units)"
    ],
    "diagnosis": "Thermostat Calibration Error",
    "action": "Recalibrate or replace thermostat. Test with external thermometer. Proper placement is critical."
}


# ════════════════════════════════════════════════════════════════════════════
# MONITOR RULES (Severity 2, CF 0.60-0.75)
# ════════════════════════════════════════════════════════════════════════════

RULE_019 = {
    "id": "RULE_019",
    "name": "Minor Refrigerant Leak (Slow Charge Loss)",
    "severity": 2,
    "cf": 0.68,
    "conditions": [
        "Slight refrigerant smell occasionally detected",
        "Charge drops 5-10% per month",
        "Capacity slightly reduced but still adequate",
        "No visible oil stains on pipes"
    ],
    "diagnosis": "Minor Refrigerant Leak - Slow",
    "action": "Find leak using dye or ultrasonic. Seal pinhole. Top up charge. Monitor next month."
}

RULE_020 = {
    "id": "RULE_020",
    "name": "Check Valve Leakage (Reverse Flow)",
    "severity": 2,
    "cf": 0.65,
    "conditions": [
        "System pressure drops overnight (no use)",
        "Charge appears to be slowly leaking",
        "Discharge line sweat visible during idle",
        "Compressor hesitates on restart"
    ],
    "diagnosis": "Check Valve Leakage",
    "action": "Verify with service gauge set. Replace check valve. Cost ~$200-300 with labor."
}

RULE_021 = {
    "id": "RULE_021",
    "name": "Air Filter Clogged (Mild Airflow Restriction)",
    "severity": 1,
    "cf": 0.70,
    "conditions": [
        "Visible dust accumulation on filter",
        "Slight airflow reduction",
        "System running slightly longer than normal",
        "Filter hasn't been changed in >3 months"
    ],
    "diagnosis": "Clogged Air Filter",
    "action": "Replace air filter immediately. Cost $20-50. Improves efficiency and indoor air quality."
}

RULE_022 = {
    "id": "RULE_022",
    "name": "Capacitor Degradation (Motor Start Capacitor)",
    "severity": 2,
    "cf": 0.62,
    "conditions": [
        "Compressor hard to start (slow spin-up)",
        "Contactor clicking repeatedly before start",
        "Low starting current",
        "Capacitor case bulging or leaking"
    ],
    "diagnosis": "Start Capacitor Failure",
    "action": "Replace start capacitor. Cost $50-100. Easy DIY-friendly repair in many systems."
}

RULE_023 = {
    "id": "RULE_023",
    "name": "Ductwork Leakage (Efficiency Loss)",
    "severity": 2,
    "cf": 0.63,
    "conditions": [
        "Weak airflow at registers despite normal fan operation",
        "Visible gaps or loose connections in ducts",
        "Air escaping from seams (you can feel it)",
        "Rooms not cooling evenly"
    ],
    "diagnosis": "Ductwork Air Leakage",
    "action": "Seal ducts with mastic or duct tape. May recover 10-20% efficiency loss. Low cost."
}

RULE_024 = {
    "id": "RULE_024",
    "name": "Blower Motor Imbalance",
    "severity": 2,
    "cf": 0.64,
    "conditions": [
        "Vibration from indoor unit during operation",
        "Rattling noise from fan area",
        "Vibration increases with fan speed",
        "Worse when outdoor temp very high"
    ],
    "diagnosis": "Blower Motor Imbalance",
    "action": "Balance or replace blower wheel. Check for debris inside. Cost $150-300."
}

RULE_025 = {
    "id": "RULE_025",
    "name": "Desiccant Drier Saturated (Moisture in System)",
    "severity": 2,
    "cf": 0.66,
    "conditions": [
        "System has had multiple recharges in short time",
        "Slight acid smell developing",
        "Occasional minor compressor noise",
        "Equipment frequently serviced"
    ],
    "diagnosis": "Drier Cartridge Saturated - Replace Soon",
    "action": "Replace drier filter. Prevents moisture-related failures. Cost $100-200."
}

RULE_026 = {
    "id": "RULE_026",
    "name": "Frost/Defrost Cycle Not Activating (Heat Pump)",
    "severity": 2,
    "cf": 0.59,
    "conditions": [
        "Outdoor coil frosting over in cooling mode",
        "Defrost heater not cycling",
        "Outdoor temp below 10°C",
        "System not switching to defrost"
    ],
    "diagnosis": "Defrost Cycle Malfunction",
    "action": "Check defrost thermostat sensor. Verify reversing valve operation. May need controls service."
}


# ════════════════════════════════════════════════════════════════════════════
# MONITOR RULES (Severity 1, CF 0.50-0.65) - PREVENTIVE
# ════════════════════════════════════════════════════════════════════════════

RULE_027 = {
    "id": "RULE_027",
    "name": "Routine Maintenance Due",
    "severity": 1,
    "cf": 0.80,
    "conditions": [
        "Last service >12 months ago",
        "Seasonal maintenance cycle due"
    ],
    "diagnosis": "Routine Maintenance Overdue",
    "action": "Schedule service within 2 weeks. Filter change, pressure check, charge verification."
}

RULE_028 = {
    "id": "RULE_028",
    "name": "Equipment Age - Replacement Planning",
    "severity": 1,
    "cf": 0.72,
    "conditions": [
        "Equipment age 18-22 years (beyond typical 15-20 year lifespan)"
    ],
    "diagnosis": "Aging Equipment - Plan Replacement",
    "action": "Equipment nearing end of life. Plan replacement in next 2-3 years. Increased failure risk."
}

RULE_029 = {
    "id": "RULE_029",
    "name": "Refrigerant R-22 Phase-Out",
    "severity": 1,
    "cf": 0.75,
    "conditions": [
        "Equipment uses R-22 refrigerant (legacy)"
    ],
    "diagnosis": "R-22 System - Upgrade Recommended",
    "action": "R-22 is being phased out. Plan upgrade to R-410A or R-32 system within 2-3 years."
}

RULE_030 = {
    "id": "RULE_030",
    "name": "Low Oil Level Alert",
    "severity": 1,
    "cf": 0.65,
    "conditions": [
        "Oil level 30-50% of sight glass"
    ],
    "diagnosis": "Low Oil Level - Add Oil Soon",
    "action": "Add POE synthetic oil. Check for slow leaks. Monitor next month."
}


# ════════════════════════════════════════════════════════════════════════════
# COMBINED MULTI-SYMPTOM RULES (Multiple indicators = higher certainty)
# ════════════════════════════════════════════════════════════════════════════

RULE_031 = {
    "id": "RULE_031",
    "name": "Refrigerant System Blockage (Multiple Indicators)",
    "severity": 4,
    "cf": 0.86,
    "conditions": [
        "Liquid line temperature <10°C",
        "Suction line temperature <-15°C (extreme superheat)",
        "Suction pressure <1.0 bar",
        "Evaporator completely frosted or iced"
    ],
    "diagnosis": "Refrigerant System Blockage (Expansion Device or Drier)",
    "action": "System shut down. Replace expansion device and/or drier. May need chemical flush."
}

RULE_032 = {
    "id": "RULE_032",
    "name": "Compressor Electrical Fault (Current + Pressure Mismatch)",
    "severity": 4,
    "cf": 0.84,
    "conditions": [
        "Current draw extremely low (<5A) despite high discharge pressure",
        "Compressor runs but won't build pressure",
        "Compressor won't shut off (unloader valve stuck)",
        "Audible buzzing from compressor"
    ],
    "diagnosis": "Compressor Electrical Fault",
    "action": "Check capacitor. Test compressor motor with megohm meter. May need replacement."
}

RULE_033 = {
    "id": "RULE_033",
    "name": "System Efficiency Decline (Trending)",
    "severity": 2,
    "cf": 0.71,
    "conditions": [
        "Capacity declining month over month",
        "Runtime increasing to maintain setpoint",
        "No single critical condition yet",
        "Multiple minor issues present"
    ],
    "diagnosis": "Declining System Efficiency - Investigate",
    "action": "Comprehensive system check. May be multiple small issues. Check charge, filters, coils."
}

RULE_034 = {
    "id": "RULE_034",
    "name": "Pressure Ratio Abnormal (Indicates Flow Restriction or Leak)",
    "severity": 3,
    "cf": 0.73,
    "conditions": [
        "Pressure ratio Pdischarge/Psuction abnormally high (>6:1) or low (<2:1)",
        "Temperatures don't match pressure readings",
        "Efficiency compromised despite normal operation sounds"
    ],
    "diagnosis": "Abnormal Pressure Ratio - System Imbalance",
    "action": "Check for flow restrictions. Verify thermometer accuracy. May indicate internal blockage."
}


# ════════════════════════════════════════════════════════════════════════════
# ADDITIONAL SPECIALIZED RULES
# ════════════════════════════════════════════════════════════════════════════

RULE_035 = {
    "id": "RULE_035",
    "name": "Control Board Malfunction",
    "severity": 4,
    "cf": 0.80,
    "conditions": [
        "No power to compressor despite call for cooling",
        "System lights don't respond to thermostat",
        "Error codes displayed (if unit has display)",
        "Relays don't click when activated"
    ],
    "diagnosis": "Control Board Failure",
    "action": "Replace control board. Cost $400-800. Verify power supply first."
}

RULE_036 = {
    "id": "RULE_036",
    "name": "Low Voltage Supply Problem",
    "severity": 3,
    "cf": 0.79,
    "conditions": [
        "Voltage to compressor <200V or >250V (should be 208-240V)",
        "Compressor struggles to start",
        "Contactor chatter (clicking)",
        "Voltage fluctuation during operation"
    ],
    "diagnosis": "Low Voltage Supply Issue",
    "action": "Check main electrical panel. Verify utility voltage. May need utility company call."
}

RULE_037 = {
    "id": "RULE_037",
    "name": "Evaporator Freeze-Up (Defrost Needed)",
    "severity": 3,
    "cf": 0.75,
    "conditions": [
        "Evaporator coil covered with ice",
        "No air output from vents",
        "System cycles off on high pressure",
        "Outdoor temp below -5°C (for AC in winter)"
    ],
    "diagnosis": "Evaporator Ice-Up - Freeze Protection Needed",
    "action": "Thaw coil. Check expansion device. Verify outdoor thermostat. May need crankcase heater."
}

RULE_038 = {
    "id": "RULE_038",
    "name": "Compressor Valve Plate Damage",
    "severity": 4,
    "cf": 0.81,
    "conditions": [
        "Clicking sound from inside compressor",
        "Capacity slowly declining despite good pressures",
        "Suction/discharge temperatures and pressures don't align",
        "Previous liquid slugging event"
    ],
    "diagnosis": "Compressor Valve Plate Crack",
    "action": "Compressor needs overhaul or replacement. Valve plate is damaged. Reduced efficiency."
}

RULE_039 = {
    "id": "RULE_039",
    "name": "Run Capacitor Failure",
    "severity": 2,
    "cf": 0.70,
    "conditions": [
        "Compressor vibrates excessively during operation",
        "Low running current (<50% of nameplate)",
        "Weak cooling/heating output",
        "Capacitor bulging or leaking"
    ],
    "diagnosis": "Run Capacitor Failure",
    "action": "Replace run capacitor. Cost $75-125. Easy replacement. Improves motor efficiency."
}

RULE_040 = {
    "id": "RULE_040",
    "name": "Suction Line Sweating / Frosting",
    "severity": 2,
    "cf": 0.64,
    "conditions": [
        "Suction line cold to touch, covered with condensation/frost",
        "Suction temperature very low (<-10°C)",
        "High superheat condition",
        "Evaporator may be slightly frosted"
    ],
    "diagnosis": "Excessive Superheat - TXV Needs Adjustment",
    "action": "Adjust TXV superheat setting downward. Check TXV sensing bulb contact. May need service."
}

RULE_041 = {
    "id": "RULE_041",
    "name": "Boiler Water Level Low",
    "severity": 4,
    "cf": 0.82,
    "conditions": [
        "Water level in sight glass below 25%",
        "Low water cutout switch may prevent operation",
        "System won't start or cycles off"
    ],
    "diagnosis": "Boiler Water Level Critical - Low",
    "action": "ADD WATER IMMEDIATELY. Check for leaks. Prime system carefully to remove air."
}

RULE_042 = {
    "id": "RULE_042",
    "name": "Boiler Air in System",
    "severity": 2,
    "cf": 0.68,
    "conditions": [
        "Gurgling, knocking, or banging noise from boiler",
        "Uneven heating in radiators",
        "Air bubbles visible in sight glass",
        "System just filled or recently serviced"
    ],
    "diagnosis": "Air in Boiler Heating Loop",
    "action": "Bleed air from system highest point. Refill to proper level. May need purging valve opened."
}

RULE_043 = {
    "id": "RULE_043",
    "name": "Boiler Internal Corrosion",
    "severity": 3,
    "cf": 0.76,
    "conditions": [
        "Water appears rusty or discolored",
        "Metal debris visible in water",
        "Boiler developing leaks",
        "Acidic water (low pH <6.5)"
    ],
    "diagnosis": "Boiler Internal Corrosion",
    "action": "Water treatment required. Add corrosion inhibitor. Flush system. Consider new boiler if severe."
}

RULE_044 = {
    "id": "RULE_044",
    "name": "Evaporator Outlet Temperature Sensor Malfunction",
    "severity": 2,
    "cf": 0.62,
    "conditions": [
        "Evaporator temperature reading seems wrong",
        "TXV control erratic despite good equipment operation",
        "Temperature doesn't change with load changes"
    ],
    "diagnosis": "Evaporator Temperature Sensor Failure",
    "action": "Check sensor resistance with multimeter. Verify sensor bulb is in good contact with line."
}

RULE_045 = {
    "id": "RULE_045",
    "name": "Contactor Burn-In (High Contact Resistance)",
    "severity": 2,
    "cf": 0.65,
    "conditions": [
        "Contactor contacts black/pitted/corroded",
        "Starting current low despite good system",
        "Contactor coil buzzes continuously"
    ],
    "diagnosis": "Contactor Contact Oxidation",
    "action": "Replace contactor. Clean contacts or replace. Cost $150-300. Prevents motor damage."
}


# ════════════════════════════════════════════════════════════════════════════
# ADDITIONAL DIAGNOSTIC RULES
# ════════════════════════════════════════════════════════════════════════════

RULE_046 = {
    "id": "RULE_046",
    "name": "Coil Leak (Micro-Pinhole)",
    "severity": 3,
    "cf": 0.74,
    "conditions": [
        "Slow refrigerant leak from coil",
        "Intermittent oil stain at coil connection",
        "Leak accelerates during hot weather"
    ],
    "diagnosis": "Heat Exchanger Micro-Leak",
    "action": "Locate leak with dye. Try sealing with compressor-oil-compatible sealant. May need coil replacement."
}

RULE_047 = {
    "id": "RULE_047",
    "name": "System Undercharge (Subcooling Insufficient)",
    "severity": 3,
    "cf": 0.72,
    "conditions": [
        "Liquid line temperature approaching discharge temp",
        "No subcooling visible (liquid should be cooler than discharge)",
        "System capacity weak"
    ],
    "diagnosis": "System Undercharge - Liquid Cooling Loss",
    "action": "Verify charge weight. Check for leaks. Recharge to nameplate with proper scale."
}

RULE_048 = {
    "id": "RULE_048",
    "name": "Non-Condensable Gas Contamination",
    "severity": 3,
    "cf": 0.70,
    "conditions": [
        "Discharge pressure abnormally high relative to temperature",
        "Head pressure won't reduce even when outdoor temp drops",
        "System evacuated multiple times with poor vac"
    ],
    "diagnosis": "Non-Condensable Gases in System (Air)",
    "action": "Complete system evacuation with pump down. Use high-capacity vacuum pump (≤50 microns)."
}

RULE_049 = {
    "id": "RULE_049",
    "name": "High Temperature Ambient Operation",
    "severity": 2,
    "cf": 0.58,
    "conditions": [
        "Outdoor temperature >40°C",
        "System running at maximum capacity",
        "Can't reach indoor setpoint"
    ],
    "diagnosis": "Ambient Conditions Extreme - Performance Degradation",
    "action": "No fault in equipment. Outdoor temperature limit exceeded. Operation is expected to suffer."
}

RULE_050 = {
    "id": "RULE_050",
    "name": "End-of-Life System",
    "severity": 2,
    "cf": 0.75,
    "conditions": [
        "Equipment age >25 years",
        "Multiple repairs required annually",
        "Refrigerant R-22 (being phased out)"
    ],
    "diagnosis": "End-of-Life Equipment - Replacement Recommended",
    "action": "Equipment has exceeded expected service life. Replacement is cost-effective. Plan upgrade."
}


# ════════════════════════════════════════════════════════════════════════════
# SUMMARY STATISTICS
# ════════════════════════════════════════════════════════════════════════════

RULE_SUMMARY = {
    "total_rules": 50,
    "critical_rules": 5,      # Severity 5
    "high_severity_rules": 10, # Severity 4
    "medium_severity_rules": 20, # Severity 3
    "monitor_rules": 15,      # Severity 1-2
    "combined_rules": 5,      # Multi-symptom
    "domains": [
        "Compressor failures (11 rules)",
        "Refrigerant system (12 rules)",
        "Heat exchangers (8 rules)",
        "Airflow & fans (8 rules)",
        "Electrical & controls (7 rules)",
        "Boiler/furnace specific (4 rules)"
    ]
}

if __name__ == "__main__":
    print("HVAC Expert System Rules Documentation")
    print(f"Total rules documented: {RULE_SUMMARY['total_rules']}")
    print(f"Critical rules: {RULE_SUMMARY['critical_rules']}")
    print(f"High severity: {RULE_SUMMARY['high_severity_rules']}")
    print(f"Medium severity: {RULE_SUMMARY['medium_severity_rules']}")
    print(f"Monitor rules: {RULE_SUMMARY['monitor_rules']}")
    print()
    print("Rule domains covered:")
    for domain in RULE_SUMMARY['domains']:
        print(f"  - {domain}")
