"""
HVAC Equipment Ontology - Equipment Classification and Failure Mode Taxonomy

This module defines:
1. Equipment types and their classifications
2. Common failure modes for each equipment type
3. Typical threshold values for different equipment
4. Operating parameters and diagnostic limits

Used by the inference engine to contextualize rules based on equipment type.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Set


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT TYPE ENUMERATION
# ─────────────────────────────────────────────────────────────────────────────

class EquipmentType(Enum):
    """HVAC equipment categories"""
    AIR_CONDITIONER = "air_conditioner"
    HEAT_PUMP = "heat_pump"
    FURNACE = "furnace"
    BOILER = "boiler"
    CHILLER = "chiller"


class CoolingRefrigerant(Enum):
    """Common refrigerants in use"""
    R410A = "R410A"      # Modern standard, non-toxic, efficient
    R22 = "R22"          # Legacy, being phased out
    R32 = "R32"          # Eco-friendly, lower GWP
    R290 = "R290"        # Propane-based, low toxicity
    R407C = "R407C"      # R22 replacement


# ─────────────────────────────────────────────────────────────────────────────
# FAILURE MODE CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────

class FailureCategory(Enum):
    """Hierarchical failure categories"""
    COMPRESSOR = "compressor_failure"
    REFRIGERANT_SYSTEM = "refrigerant_system"
    HEAT_EXCHANGER = "heat_exchanger"
    AIRFLOW_FAN = "airflow_fan"
    ELECTRICAL = "electrical"
    CONTROL = "control"
    BOILER_FURNACE = "boiler_furnace"
    LUBRICATION = "lubrication"
    MECHANICAL = "mechanical"


# ─────────────────────────────────────────────────────────────────────────────
# SEVERITY & URGENCY LEVELS
# ─────────────────────────────────────────────────────────────────────────────

class SeverityLevel(Enum):
    """Failure severity classification"""
    OK = 0                          # Equipment normal
    MONITOR = (1, 2)               # Minor issue, schedule maintenance
    WARNING = (3, 4)               # Elevated risk, should service soon
    CRITICAL = 5                   # Immediate failure risk, shutdown may occur


class MaintenanceUrgency(Enum):
    """When to perform maintenance"""
    ROUTINE = "routine"            # Next scheduled service (>30 days)
    SOON = "soon"                  # Within 2 weeks
    URGENT = "urgent"              # Within 3 days
    IMMEDIATE = "immediate"        # Do not operate, service now


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT-SPECIFIC PARAMETERS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class OperatingLimits:
    """Normal operating parameter ranges for equipment"""
    min_discharge_temp: float       # Minimum discharge temperature (°C)
    max_discharge_temp: float       # Maximum discharge temperature (°C)
    min_suction_temp: float         # Minimum suction temperature (°C)
    max_suction_temp: float         # Maximum suction temperature (°C)
    min_discharge_pressure: float   # Minimum discharge pressure (bar)
    max_discharge_pressure: float   # Maximum discharge pressure (bar)
    min_suction_pressure: float     # Minimum suction pressure (bar)
    max_suction_pressure: float     # Maximum suction pressure (bar)
    normal_superheat_celsius: float # Normal refrigerant superheat (°C)
    max_current_draw: float         # Maximum safe motor current (A)
    normal_runtime_percent: float   # Typical compressor on-time (%)


OPERATING_LIMITS = {
    EquipmentType.AIR_CONDITIONER: OperatingLimits(
        min_discharge_temp=60, max_discharge_temp=90,
        min_suction_temp=-5, max_suction_temp=10,
        min_discharge_pressure=15, max_discharge_pressure=28,
        min_suction_pressure=2.0, max_suction_pressure=4.5,
        normal_superheat_celsius=10.0,
        max_current_draw=30,
        normal_runtime_percent=60
    ),
    
    EquipmentType.HEAT_PUMP: OperatingLimits(
        min_discharge_temp=65, max_discharge_temp=95,
        min_suction_temp=-10, max_suction_temp=5,
        min_discharge_pressure=16, max_discharge_pressure=32,
        min_suction_pressure=1.5, max_suction_pressure=4.0,
        normal_superheat_celsius=8.0,
        max_current_draw=35,
        normal_runtime_percent=70
    ),
    
    EquipmentType.CHILLER: OperatingLimits(
        min_discharge_temp=70, max_discharge_temp=100,
        min_suction_temp=-8, max_suction_temp=8,
        min_discharge_pressure=18, max_discharge_pressure=35,
        min_suction_pressure=2.0, max_suction_pressure=5.0,
        normal_superheat_celsius=6.0,
        max_current_draw=80,
        normal_runtime_percent=75
    ),
    
    EquipmentType.FURNACE: OperatingLimits(
        min_discharge_temp=60, max_discharge_temp=90,
        min_suction_temp=-5, max_suction_temp=10,
        min_discharge_pressure=15, max_discharge_pressure=28,
        min_suction_pressure=2.0, max_suction_pressure=4.5,
        normal_superheat_celsius=10.0,
        max_current_draw=25,
        normal_runtime_percent=50
    ),
    
    EquipmentType.BOILER: OperatingLimits(
        min_discharge_temp=80, max_discharge_temp=120,
        min_suction_temp=10, max_suction_temp=40,
        min_discharge_pressure=1.0, max_discharge_pressure=3.0,
        min_suction_pressure=0.5, max_suction_pressure=2.0,
        normal_superheat_celsius=0.0,  # N/A for boilers
        max_current_draw=15,
        normal_runtime_percent=40
    )
}


# ─────────────────────────────────────────────────────────────────────────────
# FAILURE MODE TAXONOMY BY EQUIPMENT TYPE
# ─────────────────────────────────────────────────────────────────────────────

EQUIPMENT_FAILURE_MODES: Dict[EquipmentType, Dict[FailureCategory, List[str]]] = {
    
    EquipmentType.AIR_CONDITIONER: {
        FailureCategory.COMPRESSOR: [
            "bearing_wear",
            "valve_failure",
            "burnout",
            "oil_slugging",
            "liquid_slugging",
            "thermal_overload",
            "winding_short"
        ],
        FailureCategory.REFRIGERANT_SYSTEM: [
            "refrigerant_leak_minor",
            "refrigerant_leak_major",
            "refrigerant_overcharge",
            "refrigerant_undercharge",
            "moisture_contamination",
            "air_contamination",
            "oil_contamination",
            "expansion_device_blockage"
        ],
        FailureCategory.HEAT_EXCHANGER: [
            "evaporator_fouling",
            "condenser_fouling",
            "evaporator_freeze",
            "condenser_freeze",
            "tube_leak",
            "fin_damage"
        ],
        FailureCategory.AIRFLOW_FAN: [
            "evaporator_fan_failure",
            "condenser_fan_failure",
            "air_filter_clogged",
            "ductwork_obstruction",
            "ductwork_leak"
        ],
        FailureCategory.ELECTRICAL: [
            "capacitor_failure",
            "contactor_failure",
            "low_voltage_transformer_failure",
            "thermostat_battery_failure"
        ],
        FailureCategory.CONTROL: [
            "thermostat_calibration_error",
            "airflow_sensor_malfunction",
            "safety_thermostat_nuisance_trip"
        ]
    },
    
    EquipmentType.HEAT_PUMP: {
        FailureCategory.COMPRESSOR: [
            "bearing_wear",
            "valve_failure",
            "burnout",
            "oil_slugging",
            "liquid_slugging",
            "thermal_overload",
            "winding_short"
        ],
        FailureCategory.REFRIGERANT_SYSTEM: [
            "refrigerant_leak_minor",
            "refrigerant_leak_major",
            "refrigerant_overcharge",
            "refrigerant_undercharge",
            "moisture_contamination",
            "reversing_valve_malfunction",
            "check_valve_leakage",
            "expansion_device_blockage"
        ],
        FailureCategory.HEAT_EXCHANGER: [
            "evaporator_fouling",
            "condenser_fouling",
            "indoor_coil_freeze",
            "outdoor_coil_freeze",
            "tube_leak"
        ],
        FailureCategory.AIRFLOW_FAN: [
            "indoor_fan_failure",
            "outdoor_fan_failure",
            "air_filter_clogged",
            "ductwork_leak",
            "airflow_sensor_malfunction"
        ],
        FailureCategory.ELECTRICAL: [
            "capacitor_failure",
            "contactor_failure",
            "defrost_heater_failure"
        ],
        FailureCategory.CONTROL: [
            "reversing_valve_control_failure",
            "defrost_thermostat_malfunction"
        ]
    },
    
    EquipmentType.CHILLER: {
        FailureCategory.COMPRESSOR: [
            "bearing_wear",
            "bearing_failure",
            "valve_failure",
            "burnout",
            "oil_slugging",
            "thermal_overload",
            "liquid_slugging"
        ],
        FailureCategory.REFRIGERANT_SYSTEM: [
            "refrigerant_leak_minor",
            "refrigerant_leak_major",
            "refrigerant_overcharge",
            "refrigerant_undercharge",
            "moisture_contamination",
            "oil_contamination",
            "expansion_device_blockage",
            "non_condensable_gases",
            "oil_separator_failure"
        ],
        FailureCategory.HEAT_EXCHANGER: [
            "evaporator_tube_fouling",
            "condenser_tube_fouling",
            "evaporator_tube_leak",
            "condenser_tube_leak",
            "evaporator_freeze",
            "tube_corrosion_internal",
            "tube_corrosion_external"
        ],
        FailureCategory.AIRFLOW_FAN: [
            "condenser_fan_failure",
            "cooling_tower_fan_failure"
        ],
        FailureCategory.ELECTRICAL: [
            "motor_bearing_failure",
            "motor_winding_short",
            "power_supply_failure"
        ],
        FailureCategory.LUBRICATION: [
            "oil_breakdown",
            "oil_level_low",
            "oil_contamination"
        ]
    },
    
    EquipmentType.FURNACE: {
        FailureCategory.COMPRESSOR: [
            "bearing_wear",
            "valve_failure",
            "thermal_overload"
        ],
        FailureCategory.REFRIGERANT_SYSTEM: [
            "refrigerant_leak",
            "expansion_device_malfunction"
        ],
        FailureCategory.HEAT_EXCHANGER: [
            "evaporator_fouling",
            "secondary_heat_exchanger_corrosion"
        ],
        FailureCategory.AIRFLOW_FAN: [
            "blower_fan_failure",
            "air_filter_clogged",
            "ductwork_leak"
        ],
        FailureCategory.ELECTRICAL: [
            "ignition_failure",
            "flame_sensor_failure",
            "blower_motor_failure"
        ],
        FailureCategory.BOILER_FURNACE: [
            "gas_leak",
            "incomplete_combustion",
            "heat_exchanger_crack"
        ]
    },
    
    EquipmentType.BOILER: {
        FailureCategory.BOILER_FURNACE: [
            "scale_buildup",
            "internal_corrosion",
            "external_corrosion",
            "pressure_relief_valve_stuck",
            "water_level_low",
            "air_in_system",
            "combustion_gas_leak",
            "ignition_failure"
        ],
        FailureCategory.MECHANICAL: [
            "pump_cavitation",
            "pump_failure",
            "valve_blockage",
            "thermostatic_valve_malfunction"
        ],
        FailureCategory.ELECTRICAL: [
            "ignition_control_failure",
            "low_voltage_transformer_failure"
        ],
        FailureCategory.CONTROL: [
            "thermostat_failure",
            "pressure_gauge_failure"
        ]
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# FAILURE SEVERITY BY CATEGORY
# ─────────────────────────────────────────────────────────────────────────────

FAILURE_SEVERITY: Dict[FailureCategory, int] = {
    FailureCategory.COMPRESSOR: 4,              # Very high severity
    FailureCategory.BOILER_FURNACE: 5,          # Critical - safety risk
    FailureCategory.REFRIGERANT_SYSTEM: 4,      # High - system may fail
    FailureCategory.HEAT_EXCHANGER: 3,          # Medium-high - efficiency loss
    FailureCategory.ELECTRICAL: 3,              # Medium-high - loss of operation
    FailureCategory.AIRFLOW_FAN: 2,             # Medium - comfort loss
    FailureCategory.LUBRICATION: 4,             # High - leads to compressor damage
    FailureCategory.CONTROL: 2,                 # Medium - erratic operation
    FailureCategory.MECHANICAL: 3               # Medium-high
}


# ─────────────────────────────────────────────────────────────────────────────
# EQUIPMENT AGE-BASED RISK ASSESSMENT
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EquipmentAgeProfile:
    """Risk factors based on equipment age"""
    age_years: float
    expected_lifespan_years: int
    risk_multiplier: float       # Multiplier for failure certainty
    typical_failure_modes: List[str]
    maintenance_urgency: str


AGE_PROFILES = {
    (0, 5): EquipmentAgeProfile(
        age_years=2.5,
        expected_lifespan_years=15,
        risk_multiplier=0.6,
        typical_failure_modes=["manufacturing_defect", "installation_fault"],
        maintenance_urgency="routine"
    ),
    (5, 10): EquipmentAgeProfile(
        age_years=7.5,
        expected_lifespan_years=15,
        risk_multiplier=1.0,
        typical_failure_modes=["normal_wear", "seal_degradation"],
        maintenance_urgency="routine"
    ),
    (10, 15): EquipmentAgeProfile(
        age_years=12.5,
        expected_lifespan_years=15,
        risk_multiplier=1.5,
        typical_failure_modes=["accelerated_wear", "bearing_fatigue", "corrosion"],
        maintenance_urgency="soon"
    ),
    (15, 20): EquipmentAgeProfile(
        age_years=17.5,
        expected_lifespan_years=20,
        risk_multiplier=2.0,
        typical_failure_modes=["multiple_component_failure", "major_overhaul_needed"],
        maintenance_urgency="urgent"
    ),
    (20, 100): EquipmentAgeProfile(
        age_years=25.0,
        expected_lifespan_years=20,
        risk_multiplier=3.0,
        typical_failure_modes=["end_of_life", "replacement_recommended"],
        maintenance_urgency="immediate"
    )
}


def get_age_profile(age_years: float) -> EquipmentAgeProfile:
    """Return age profile for given equipment age"""
    for (min_age, max_age), profile in AGE_PROFILES.items():
        if min_age <= age_years < max_age:
            return profile
    # Default to oldest category
    return list(AGE_PROFILES.values())[-1]


# ─────────────────────────────────────────────────────────────────────────────
# REFRIGERANT PROPERTIES (for diagnosis)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RefrigerantProperties:
    """Physical properties for refrigerant diagnostics"""
    name: str
    gwp: float                     # Global Warming Potential
    ozone_depletion: float         # ODP - Ozone Depletion Potential
    toxicity_level: str            # 'none', 'low', 'medium', 'high'
    flammability: str              # 'none', 'low', 'medium', 'high'
    critical_pressure_bar: float   # Compressor shutdown limit
    critical_temp_celsius: float   # System temperature limit


REFRIGERANT_PROPERTIES = {
    CoolingRefrigerant.R410A: RefrigerantProperties(
        name="R-410A", gwp=2088, ozone_depletion=0.0,
        toxicity_level="none", flammability="none",
        critical_pressure_bar=49.2, critical_temp_celsius=70.1
    ),
    CoolingRefrigerant.R22: RefrigerantProperties(
        name="R-22", gwp=1810, ozone_depletion=0.055,
        toxicity_level="low", flammability="none",
        critical_pressure_bar=49.7, critical_temp_celsius=96.1
    ),
    CoolingRefrigerant.R32: RefrigerantProperties(
        name="R-32", gwp=675, ozone_depletion=0.0,
        toxicity_level="low", flammability="high",
        critical_pressure_bar=57.8, critical_temp_celsius=78.1
    ),
    CoolingRefrigerant.R290: RefrigerantProperties(
        name="R-290 (Propane)", gwp=20, ozone_depletion=0.0,
        toxicity_level="none", flammability="high",
        critical_pressure_bar=42.4, critical_temp_celsius=96.7
    )
}


# ─────────────────────────────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_operating_limits(equipment_type: str) -> OperatingLimits:
    """Get normal operating limits for equipment type"""
    try:
        eq_type = EquipmentType(equipment_type)
        return OPERATING_LIMITS.get(eq_type)
    except ValueError:
        return None


def get_failure_modes_for_equipment(equipment_type: str) -> Set[str]:
    """Get all possible failure modes for given equipment type"""
    try:
        eq_type = EquipmentType(equipment_type)
        failure_dict = EQUIPMENT_FAILURE_MODES.get(eq_type, {})
        all_modes = set()
        for modes_list in failure_dict.values():
            all_modes.update(modes_list)
        return all_modes
    except ValueError:
        return set()


def get_failure_severity(failure_category: str) -> int:
    """Get typical severity level for failure category (0-5)"""
    try:
        category = FailureCategory(failure_category)
        return FAILURE_SEVERITY.get(category, 2)
    except ValueError:
        return 2


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE (for testing)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Example: Check limits for air conditioner
    limits = get_operating_limits("air_conditioner")
    print(f"AC Normal Discharge Temp: {limits.min_discharge_temp}°C - {limits.max_discharge_temp}°C")
    
    # Example: Get failure modes
    modes = get_failure_modes_for_equipment("chiller")
    print(f"Chiller possible failures: {modes}")
    
    # Example: Age risk assessment
    profile = get_age_profile(18)
    print(f"18-year-old equipment risk multiplier: {profile.risk_multiplier}")
