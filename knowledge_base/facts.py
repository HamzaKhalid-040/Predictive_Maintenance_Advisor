"""
Fact Schema for HVAC Predictive Maintenance Expert System

This module defines all input facts (sensor readings, equipment info, maintenance history)
that feed into the inference engine. These facts are declared by the user via the GUI,
and the expert system reasons over them to produce diagnoses.

Structure:
- SensorReading: All continuous measurements from equipment sensors
- EquipmentInfo: Static metadata about the equipment
- MaintenanceHistory: Historical service and performance data
- DiagnosisResult: Structure for conclusions (internal use)
"""

from experta import Fact, Field


class SensorReading(Fact):
    """
    Continuous sensor measurements from HVAC equipment.
    
    User provides these values via the Streamlit interface. All fields have
    reasonable defaults to allow partial sensor input (e.g., not all sensors present).
    """
    
    # Equipment Classification
    equipment_type = Field(str, mandatory=True)
    
    # Temperature Measurements (Critical for diagnosis)
    temp_outdoor = Field(float, default=20.0)
    temp_indoor_setpoint = Field(float, default=22.0)
    temp_indoor_actual = Field(float, default=22.0)
    temp_evaporator_outlet = Field(float, default=5.0)
    temp_condenser_outlet = Field(float, default=45.0)
    temp_suction_line = Field(float, default=0.0)
    temp_discharge_line = Field(float, default=70.0)
    temp_liquid_line = Field(float, default=35.0)
    
    # Pressure Measurements (Critical for diagnosis)
    pressure_suction = Field(float, default=2.5)
    pressure_discharge = Field(float, default=20.0)
    
    # Refrigerant System
    refrigerant_charge_percent = Field(float, default=100.0)
    refrigerant_type = Field(str, default="R410A")
    
    # Airflow & Fan Performance
    airflow_rate = Field(float, default=200.0)
    evaporator_temperature_rise = Field(float, default=10.0)
    condenser_temperature_drop = Field(float, default=15.0)
    
    # Electrical Measurements
    compressor_current_draw = Field(float, default=20.0)
    compressor_voltage = Field(float, default=230.0)
    
    # Lubrication & Fluid Quality
    oil_level_percent = Field(float, default=100.0)
    oil_acid_number = Field(float, default=0.5)
    oil_color = Field(str, default="clear")
    
    # Qualitative Observations
    noise_level = Field(str, default="normal")
    odor_present = Field(str, default="none")
    frost_condition = Field(str, default="none")
    
    # Boiler-Specific (for furnace/boiler equipment)
    water_level_percent = Field(float, default=100.0)
    water_condition = Field(str, default="clear")
    boiler_pressure = Field(float, default=1.5)
    
    # Compressor Runtime & Duty
    compressor_runtime_hours = Field(float, default=5000.0)
    
    # System Status Flags
    system_cycles_per_hour = Field(float, default=5.0)
    system_runtime_percent = Field(float, default=50.0)
    
    # Equipment Age (moved from EquipmentInfo for convenience)
    equipment_age_years = Field(float, default=5.0)
    last_service_days_ago = Field(int, default=30)


class EquipmentInfo(Fact):
    """
    Static metadata about the equipment being diagnosed.
    Provides context for rules (e.g., a 20-year-old unit behaves differently than new).
    """
    
    equipment_id = Field(str, mandatory=True)
    equipment_type = Field(str, mandatory=True)
    manufacturer = Field(str, default="Unknown")
    model_number = Field(str, default="Unknown")
    installation_year = Field(int, default=2020)
    equipment_age_years = Field(float, default=3.0)
    nameplate_capacity_kw = Field(float, default=5.0)
    refrigerant_charge_kg = Field(float, default=2.0)
    compressor_type = Field(str, default="reciprocating")
    service_interval_months = Field(int, default=12)
    design_operating_temp_min = Field(float, default=-10.0)
    design_operating_temp_max = Field(float, default=50.0)


class MaintenanceHistory(Fact):
    """
    Historical data about maintenance and performance.
    Used by rules to detect trends and plan preventive actions.
    """
    
    last_service_days_ago = Field(int, default=30)
    last_service_type = Field(str, default="routine")
    recent_repairs = Field(str, default="none")
    compressor_failure_count = Field(int, default=0)
    refrigerant_recharge_count = Field(int, default=0)
    oil_change_count = Field(int, default=0)
    coil_cleaning_count = Field(int, default=0)
    overhaul_due = Field(bool, default=False)


class DiagnosisResult(Fact):
    """
    Internal fact: stores conclusions from rules.
    Rules append to a list of these diagnoses, which are then ranked by severity + certainty.
    
    NOT declared by user; created by rules firing.
    """
    
    diagnosis_name = Field(
        str,
        mandatory=True,
        description="Human-readable diagnosis (e.g., 'Bearing Failure - Critical')"
    )
    
    certainty_factor = Field(
        float,
        mandatory=True,
        description="Confidence in this diagnosis, range 0.0 to 1.0"
    )
    
    severity_level = Field(
        int,
        mandatory=True,
        description="Severity: 0=OK, 1-2=Monitor, 3-4=Warning, 5=Critical"
    )
    
    rule_name = Field(
        str,
        mandatory=True,
        description="Which rule fired to generate this diagnosis"
    )
    
    reasoning = Field(
        str,
        default="",
        description="Brief explanation of why this rule fired"
    )
    
    recommended_action = Field(
        str,
        default="Continue routine maintenance",
        description="Maintenance action recommended"
    )
    
    emergency_shutdown_count = Field(
        int,
        default=0,
        description="Number of safety shutdowns (thermal overload, pressure cutout) in past 30 days"
    )
    
    performance_trend = Field(
        str,
        default="stable",
        description="Historical trend: 'stable', 'declining', 'improving', 'erratic'"
    )


# ────────────────────────────────────────────────────────────────────────────
# Helper Functions for Fact Validation
# ────────────────────────────────────────────────────────────────────────────

def validate_temperature_sensors(sensor_reading):
    """
    Validate that temperature measurements are physically consistent.
    Returns tuple (is_valid, error_message)
    """
    # Discharge temp should always be > suction temp
    if sensor_reading.temp_discharge_line <= sensor_reading.temp_suction_line:
        return False, "Discharge temp must be > suction temp (compressor physics violation)"
    
    # Evaporator outlet should be below indoor temp
    if sensor_reading.temp_evaporator_outlet > sensor_reading.temp_indoor_actual:
        return False, "Evaporator outlet must be below room temperature"
    
    # Condenser outlet should be above outdoor temp (heat rejection)
    if sensor_reading.temp_condenser_outlet < sensor_reading.temp_outdoor:
        return False, "Condenser outlet must be above outdoor temperature"
    
    return True, ""


def validate_pressure_sensors(sensor_reading):
    """
    Validate that pressure measurements are physically consistent.
    Returns tuple (is_valid, error_message)
    """
    # Discharge pressure must be > suction pressure
    if sensor_reading.pressure_discharge <= sensor_reading.pressure_suction:
        return False, "Discharge pressure must be > suction pressure"
    
    # Typical pressure ratio for HVAC is 2:1 to 5:1
    ratio = sensor_reading.pressure_discharge / max(sensor_reading.pressure_suction, 0.1)
    if ratio < 1.5 or ratio > 8.0:
        return False, f"Pressure ratio {ratio:.1f} is unusual; check sensor calibration"
    
    return True, ""


def validate_superheat_subcooling(sensor_reading):
    """
    Calculate refrigerant superheat and subcooling (diagnostic indicators).
    Superheat = suction_line_temp - evaporator_outlet_temp
    Subcooling = liquid_line_temp - condensing_temp (estimated from discharge pressure)
    """
    superheat = sensor_reading.temp_suction_line - sensor_reading.temp_evaporator_outlet
    # For diagnostic purposes, return as dict
    return {
        'superheat_celsius': superheat,
        'superheat_status': 'normal' if 5 <= superheat <= 15 else ('too_high' if superheat > 15 else 'too_low')
    }
