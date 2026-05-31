"""
Predictive Maintenance Expert System Engine

Core inference engine using Experta (forward-chaining expert system framework).

This engine:
1. Declares sensor facts provided by the user
2. Fires rules based on conditions matching those facts
3. Aggregates diagnoses from all fired rules
4. Resolves conflicts between competing diagnoses
5. Returns the most likely diagnosis with certainty and severity

Architecture:
- Facts: SensorReading, EquipmentInfo, MaintenanceHistory
- Rules: 60-80 expert rules defined in rules.py
- Inference: Forward chaining (data-driven)
- Conflict Resolution: By severity + certainty factor
"""

from experta import KnowledgeEngine, Rule, MATCH, TEST, NOT
from typing import List, Tuple, Optional
from knowledge_base.facts import SensorReading, EquipmentInfo, MaintenanceHistory
from knowledge_base.ontology import OperatingLimits, OPERATING_LIMITS
from inference.certainity import CertaintyFactorCalculator, ConfidenceThresholds
from inference.conflict_resolver import ConflictResolver, DiagnosisConclusion
from explanation.tracer import Tracer


class PredictiveMaintenanceEngine(KnowledgeEngine):
    """
    Main expert system for HVAC predictive maintenance.
    
    Usage:
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        engine.declare(SensorReading(...))
        engine.declare(EquipmentInfo(...))
        engine.run()
        diagnosis = engine.get_top_diagnosis()
        explanation = engine.tracer.get_explanation()
    """
    
    def __init__(self):
        super().__init__()
        self.cf_calculator = CertaintyFactorCalculator()
        self.conflict_resolver = ConflictResolver()
        self.tracer = Tracer()
        self.all_diagnoses: List[DiagnosisConclusion] = []
        self.session_log: List[str] = []
    
    def log_session(self, message: str):
        """Log internal engine messages for debugging"""
        self.session_log.append(message)
    
    # ─────────────────────────────────────────────────────────────────────────
    # NORMAL OPERATION RULES (Severity 0, CF >= 0.95)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(equipment_type=MATCH.eq_type,
                        temp_discharge_line=MATCH.t_dis,
                        temp_suction_line=MATCH.t_suc,
                        pressure_discharge=MATCH.p_dis,
                        pressure_suction=MATCH.p_suc,
                        compressor_current_draw=MATCH.current,
                        oil_level_percent=MATCH.oil_level,
                        noise_level=MATCH.noise,
                        equipment_age_years=MATCH.age),
          TEST(lambda eq_type, t_dis, t_suc, p_dis, p_suc, current, oil_level, noise, age:
               # Check ALL conditions for "normal operation"
               (60 <= t_dis <= 90) and           # Discharge temp normal
               (-5 <= t_suc <= 10) and           # Suction temp normal
               (15 <= p_dis <= 28) and           # Discharge pressure normal
               (2.0 <= p_suc <= 4.5) and         # Suction pressure normal
               (current <= 25) and               # Current draw normal
               (50 <= oil_level <= 90) and       # Oil level adequate
               (noise == 'normal') and           # No abnormal noise
               (age < 15)                         # Newer equipment
               ))
    def equipment_operating_normally(self, eq_type, t_dis, t_suc, p_dis, p_suc, current, oil_level, noise, age):
        """All systems normal - equipment operating within design parameters"""
        cf = 0.98
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Equipment Operating Normally",
            certainty_factor=cf,
            severity_level=0,
            rules_fired=["equipment_operating_normally"],
            evidence_strength=8.0,
            recommended_action="Continue routine maintenance schedule. No immediate issues."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'equipment_operating_normally',
            f'All parameters within normal ranges (Tdis={t_dis}°C, Psuc={p_suc} bar, I={current}A)',
            'Equipment Operating Normally',
            cf
        )
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # CRITICAL FAILURE RULES (Severity 5, CF 0.85-0.95)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(temp_discharge_line=MATCH.t_dis,
                        noise_level=MATCH.noise,
                        oil_color=MATCH.oil_color),
          TEST(lambda t_dis, noise, oil_color:
               (t_dis > 110) and                    # Extreme discharge temp
               (noise in ['grinding', 'knocking']) and  # Failure sounds
               (oil_color in ['brown', 'black'])        # Oil degraded
               ))
    def compressor_burnout_critical(self, t_dis, noise, oil_color):
        """
        CRITICAL: Compressor approaching burnout.
        Multiple extreme symptoms indicate imminent motor failure.
        """
        cf = 0.94
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Compressor Burnout - CRITICAL",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["compressor_burnout_critical"],
            evidence_strength=3.0,
            recommended_action="EMERGENCY SHUTDOWN. Replace compressor immediately. Risk of fire/explosion."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'compressor_burnout_critical',
            f'Discharge temp={t_dis}°C (>110), Noise={noise}, Oil={oil_color}',
            'Compressor Burnout - CRITICAL',
            cf
        )
    
    @Rule(SensorReading(pressure_discharge=MATCH.p_dis,
                        temp_discharge_line=MATCH.t_dis,
                        compressor_current_draw=MATCH.current),
          TEST(lambda p_dis, t_dis, current:
               (p_dis > 35) and                 # Extreme discharge pressure
               (t_dis > 100) and                # Very high discharge temp
               (current > 35)                   # Motor overloaded
               ))
    def compressor_thermal_overload_critical(self, p_dis, t_dis, current):
        """CRITICAL: Compressor experiencing thermal overload from over-pressurization"""
        cf = 0.90
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Compressor Thermal Overload - CRITICAL",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["compressor_thermal_overload_critical"],
            evidence_strength=3.0,
            recommended_action="Reduce outdoor temperature exposure, verify refrigerant charge, shutdown if temp > 120°C"
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'compressor_thermal_overload_critical',
            f'Pdis={p_dis} bar (>35), Tdis={t_dis}°C (>100), Current={current}A (>35)',
            'Compressor Thermal Overload - CRITICAL',
            cf
        )
    
    @Rule(SensorReading(temp_suction_line=MATCH.t_suc,
                        pressure_suction=MATCH.p_suc,
                        noise_level=MATCH.noise),
          TEST(lambda t_suc, p_suc, noise:
               (t_suc < -15) and                # Extreme suction superheat
               (p_suc < 1.2) and                # Very low suction pressure
               (noise in ['hissing', 'loud'])   # Severe noise
               ))
    def liquid_slugging_critical(self, t_suc, p_suc, noise):
        """CRITICAL: Liquid slugging detected - immediate compressor damage risk"""
        cf = 0.91
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Liquid Slugging - CRITICAL",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["liquid_slugging_critical"],
            evidence_strength=3.0,
            recommended_action="STOP IMMEDIATELY. Severe damage to compressor. Requires emergency service."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'liquid_slugging_critical',
            f'Suction temp={t_suc}°C (<-15), Suction pressure={p_suc} bar (<1.2), Noise={noise}',
            'Liquid Slugging - CRITICAL',
            cf
        )
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # HIGH SEVERITY RULES (Severity 4, CF 0.80-0.89)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(temp_discharge_line=MATCH.t_dis,
                        pressure_discharge=MATCH.p_dis,
                        compressor_current_draw=MATCH.current),
          TEST(lambda t_dis, p_dis, current:
               (t_dis > 95) and                 # High discharge temp
               (p_dis > 30) and                 # High pressure
               (current > 30)                   # High current
               ))
    def condenser_fouling_with_overcharge(self, t_dis, p_dis, current):
        """High pressure and temp: likely condenser fouling + overcharge"""
        cf = 0.85
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Condenser Fouling with Overcharge",
            certainty_factor=cf,
            severity_level=4,
            rules_fired=["condenser_fouling_with_overcharge"],
            evidence_strength=3.0,
            recommended_action="Clean condenser coil. Recover and recharge refrigerant to nameplate. Check fan operation."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'condenser_fouling_with_overcharge',
            f'Tdis={t_dis}°C (>95), Pdis={p_dis} bar (>30), Current={current}A (>30)',
            'Condenser Fouling with Overcharge',
            cf
        )
    
    @Rule(SensorReading(pressure_suction=MATCH.p_suc,
                        temp_suction_line=MATCH.t_suc,
                        refrigerant_charge_percent=MATCH.charge),
          TEST(lambda p_suc, t_suc, charge:
               (p_suc < 1.5) and                # Low suction pressure
               (t_suc < -10) and                # Low suction temp (high superheat)
               (charge < 85)                    # Undercharged
               ))
    def refrigerant_leak_significant(self, p_suc, t_suc, charge):
        """Significant refrigerant leak with capacity loss"""
        cf = 0.88
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Significant Refrigerant Leak",
            certainty_factor=cf,
            severity_level=4,
            rules_fired=["refrigerant_leak_significant"],
            evidence_strength=3.0,
            recommended_action="Locate leak using dye or ultrasonic. Seal leak. Evacuate and recharge system."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'refrigerant_leak_significant',
            f'Psuc={p_suc} bar (<1.5), Tsuc={t_suc}°C (<-10), Charge={charge}% (<85)',
            'Significant Refrigerant Leak',
            cf
        )
    
    @Rule(SensorReading(oil_level_percent=MATCH.oil_level,
                        oil_color=MATCH.oil_color,
                        noise_level=MATCH.noise,
                        compressor_runtime_hours=MATCH.runtime),
          TEST(lambda oil_level, oil_color, noise, runtime:
               (oil_level < 30) and            # Very low oil
               (oil_color == 'black') and       # Degraded oil
               (noise == 'grinding') and        # Bearing wear sounds
               (runtime > 50000)                # High hours
               ))
    def bearing_failure_imminent(self, oil_level, oil_color, noise, runtime):
        """Bearing failure imminent from lack of lubrication and wear"""
        cf = 0.87
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Bearing Failure - Imminent",
            certainty_factor=cf,
            severity_level=4,
            rules_fired=["bearing_failure_imminent"],
            evidence_strength=4.0,
            recommended_action="Plan compressor replacement within 1 week. Bearing is critically worn."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'bearing_failure_imminent',
            f'Oil={oil_level}% (<30), Color={oil_color}, Noise={noise}, Runtime={runtime}h (>50k)',
            'Bearing Failure - Imminent',
            cf
        )
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # MEDIUM SEVERITY RULES (Severity 3-4, CF 0.70-0.84)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(temp_discharge_line=MATCH.t_dis,
                        pressure_discharge=MATCH.p_dis),
          TEST(lambda t_dis, p_dis:
               (85 <= t_dis < 100) and         # Elevated discharge temp
               (25 <= p_dis <= 32)              # Elevated discharge pressure
               ))
    def high_discharge_temperature_warning(self, t_dis, p_dis):
        """Discharge temperature elevated - monitor condenser and outdoor temp"""
        cf = 0.76
        diagnosis = DiagnosisConclusion(
            diagnosis_name="High Discharge Temperature - Warning",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["high_discharge_temperature_warning"],
            evidence_strength=2.0,
            recommended_action="Check condenser fouling. Verify outdoor temperature. Monitor trending."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'high_discharge_temperature_warning',
            f'Tdis={t_dis}°C (85-100), Pdis={p_dis} bar (25-32)',
            'High Discharge Temperature - Warning',
            cf
        )
    
    @Rule(SensorReading(pressure_suction=MATCH.p_suc,
                        temp_suction_line=MATCH.t_suc),
          TEST(lambda p_suc, t_suc:
               (1.5 <= p_suc < 2.0) and        # Low suction pressure
               (-12 <= t_suc < -5)              # Low suction temp (high superheat)
               ))
    def refrigerant_undercharge_warning(self, p_suc, t_suc):
        """System appears undercharged or has minor leak"""
        cf = 0.72
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Refrigerant Undercharge - Warning",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["refrigerant_undercharge_warning"],
            evidence_strength=2.0,
            recommended_action="Check for leaks. If no leaks, recharge to nameplate. Monitor capacity."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'refrigerant_undercharge_warning',
            f'Psuc={p_suc} bar (1.5-2.0), Tsuc={t_suc}°C (-12 to -5)',
            'Refrigerant Undercharge - Warning',
            cf
        )
    
    @Rule(SensorReading(oil_level_percent=MATCH.oil_level,
                        oil_acid_number=MATCH.tan),
          TEST(lambda oil_level, tan:
               (30 <= oil_level < 50) and      # Low oil level
               (tan > 0.8)                      # Oil degraded
               ))
    def oil_quality_deterioration_warning(self, oil_level, tan):
        """Oil is degraded and level is dropping - change oil soon"""
        cf = 0.71
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Oil Quality Deterioration - Warning",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["oil_quality_deterioration_warning"],
            evidence_strength=2.0,
            recommended_action="Change compressor oil. Use POE (polyol ester) synthetic oil. Add acid removal filter."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'oil_quality_deterioration_warning',
            f'Oil level={oil_level}% (30-50), Acid number={tan} (>0.8)',
            'Oil Quality Deterioration - Warning',
            cf
        )
    
    @Rule(SensorReading(temp_indoor_setpoint=MATCH.setpoint,
                        temp_indoor_actual=MATCH.actual,
                        system_runtime_percent=MATCH.runtime_pct),
          TEST(lambda setpoint, actual, runtime_pct:
               (abs(actual - setpoint) > 3.0) and  # Poor temperature control
               (runtime_pct > 80)                   # Running continuously
               ))
    def loss_of_capacity_warning(self, setpoint, actual, runtime_pct):
        """Significant capacity loss - cannot reach setpoint"""
        cf = 0.74
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Loss of Cooling Capacity - Warning",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["loss_of_capacity_warning"],
            evidence_strength=2.0,
            recommended_action="Check for refrigerant undercharge, evaporator fouling, or airflow blockage."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'loss_of_capacity_warning',
            f'Setpoint={setpoint}°C, Actual={actual}°C (diff={abs(actual-setpoint)}), Runtime={runtime_pct}%',
            'Loss of Cooling Capacity - Warning',
            cf
        )
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # MONITORING RULES (Severity 1-2, CF 0.50-0.69)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(noise_level=MATCH.noise))
    def abnormal_noise_monitor(self, noise):
        """Monitor abnormal operating sounds"""
        if noise == 'normal':
            return  # Skip normal noise
        
        cf_map = {
            'elevated': 0.55,
            'loud': 0.65,
            'grinding': 0.80,
            'knocking': 0.75,
            'hissing': 0.60,
            'bubbling': 0.50
        }
        
        cf = cf_map.get(noise, 0.50)
        diagnosis_map = {
            'elevated': 'Elevated Operating Noise - Monitor',
            'loud': 'Loud Operating Noise - Warning',
            'grinding': 'Grinding Noise - Critical Bearing Wear',
            'knocking': 'Knocking Noise - Check Compressor',
            'hissing': 'Hissing Noise - Possible Refrigerant Leak',
            'bubbling': 'Bubbling Noise - Air in System'
        }
        
        severity_map = {
            'elevated': 1,
            'loud': 2,
            'grinding': 5,
            'knocking': 4,
            'hissing': 3,
            'bubbling': 2
        }
        
        diag_name = diagnosis_map.get(noise, 'Abnormal Noise Detected')
        severity = severity_map.get(noise, 1)
        
        diagnosis = DiagnosisConclusion(
            diagnosis_name=diag_name,
            certainty_factor=cf,
            severity_level=severity,
            rules_fired=["abnormal_noise_monitor"],
            evidence_strength=1.0,
            recommended_action="Investigate source of noise. May indicate bearing wear, compressor damage, or loose components."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'abnormal_noise_monitor',
            f'Noise level: {noise}',
            diag_name,
            cf
        )
    
    @Rule(SensorReading(last_service_days_ago=MATCH.days_since_service),
          TEST(lambda days_since_service: days_since_service > 365))
    def overdue_maintenance_monitor(self, days_since_service):
        """Preventive maintenance overdue"""
        cf = 0.80
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Overdue Maintenance - Schedule Service",
            certainty_factor=cf,
            severity_level=2,
            rules_fired=["overdue_maintenance_monitor"],
            evidence_strength=1.0,
            recommended_action="Schedule routine maintenance within next 2 weeks. Replace filters, check pressures, verify charge."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'overdue_maintenance_monitor',
            f'Last service {days_since_service} days ago (>365)',
            'Overdue Maintenance - Schedule Service',
            cf
        )
    
    @Rule(SensorReading(equipment_age_years=MATCH.age),
          TEST(lambda age: age > 18))
    def aging_equipment_monitor(self, age):
        """Equipment approaching end of design life"""
        cf = 0.72
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Aging Equipment - Plan Replacement",
            certainty_factor=cf,
            severity_level=2,
            rules_fired=["aging_equipment_monitor"],
            evidence_strength=1.0,
            recommended_action="Equipment is 18+ years old. Plan replacement within 2-3 years. Increased failure risk."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'aging_equipment_monitor',
            f'Equipment age: {age} years (>18)',
            'Aging Equipment - Plan Replacement',
            cf
        )
    
    @Rule(SensorReading(system_cycles_per_hour=MATCH.cycles))
    def short_cycling_monitor(self, cycles):
        """Monitor for short-cycling (excessive on-off cycling)"""
        if cycles <= 8:  # Normal 4-8 cycles/hr
            return
        
        cf = 0.60 if cycles <= 15 else 0.75
        severity = 1 if cycles <= 15 else 3
        
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Short-Cycling Detected" if cycles <= 15 else "Excessive Short-Cycling - Warning",
            certainty_factor=cf,
            severity_level=severity,
            rules_fired=["short_cycling_monitor"],
            evidence_strength=1.0,
            recommended_action="Check thermostat calibration. Verify refrigerant charge. May indicate oversizing or control malfunction."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'short_cycling_monitor',
            f'Cycles per hour: {cycles} (normal 4-8)',
            diagnosis.diagnosis_name,
            cf
        )
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # COMBINED MULTI-SYMPTOM RULES (Higher certainty from evidence)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(temp_discharge_line=MATCH.t_dis,
                        pressure_discharge=MATCH.p_dis,
                        compressor_current_draw=MATCH.current,
                        oil_color=MATCH.oil_color,
                        noise_level=MATCH.noise),
          TEST(lambda t_dis, p_dis, current, oil_color, noise:
               (t_dis > 100) and               # High discharge temp
               (p_dis > 32) and                # High pressure
               (current > 32) and              # High current
               (oil_color == 'black') and      # Oil burnt
               (noise in ['loud', 'grinding'])  # Failure sounds
               ))
    def compressor_stress_multiple_symptoms(self, t_dis, p_dis, current, oil_color, noise):
        """Multiple stress indicators point to compressor failure risk"""
        # Start with base CFs and combine
        cf_temp = 0.75
        cf_pressure = 0.75
        cf_current = 0.70
        cf_oil = 0.70
        cf_noise = 0.80
        
        combined_cf = self.cf_calculator.combine_certainty_factors(
            [cf_temp, cf_pressure, cf_current, cf_oil, cf_noise]
        )
        
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Compressor Distress - Multiple Symptoms",
            certainty_factor=min(0.95, combined_cf),  # Cap at 0.95
            severity_level=4,
            rules_fired=["compressor_stress_multiple_symptoms"],
            evidence_strength=5.0,
            recommended_action="Immediate professional inspection required. High probability of compressor failure within days."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'compressor_stress_multiple_symptoms',
            f'Multiple symptoms: Tdis={t_dis}°C, Pdis={p_dis} bar, I={current}A, Oil={oil_color}, Noise={noise}',
            diagnosis.diagnosis_name,
            diagnosis.certainty_factor
        )
    
    @Rule(SensorReading(temp_evaporator_outlet=MATCH.t_evo,
                        temp_suction_line=MATCH.t_suc,
                        pressure_suction=MATCH.p_suc,
                        airflow_rate=MATCH.airflow),
          TEST(lambda t_evo, t_suc, p_suc, airflow:
               (t_evo < -8) and                # Evaporator very cold
               (t_suc < -10) and               # High superheat
               (p_suc < 1.8) and               # Low suction pressure
               (airflow < 80)                   # Restricted airflow
               ))
    def evaporator_blockage_multiple_symptoms(self, t_evo, t_suc, p_suc, airflow):
        """Evaporator fouling with multiple indicators"""
        cf_list = [0.75, 0.75, 0.70, 0.80]
        combined_cf = self.cf_calculator.combine_certainty_factors(cf_list)
        
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Evaporator Fouling - Multiple Symptoms",
            certainty_factor=combined_cf,
            severity_level=3,
            rules_fired=["evaporator_blockage_multiple_symptoms"],
            evidence_strength=4.0,
            recommended_action="Clean evaporator coil chemically. Check air filter. Restore airflow. Verify charge."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log(
            'evaporator_blockage_multiple_symptoms',
            f'Multiple indicators: Tevo={t_evo}°C, Tsuc={t_suc}°C, Psuc={p_suc} bar, Airflow={airflow} m³/min',
            diagnosis.diagnosis_name,
            combined_cf
        )
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # ADDITIONAL RULES - REFRIGERANT SYSTEM (Rules 19-30)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(pressure_discharge=MATCH.p_dis,
                        pressure_suction=MATCH.p_suc),
          TEST(lambda p_dis, p_suc:
               (p_dis < 15) and (p_suc < 1.5)))
    def complete_refrigerant_loss(self, p_dis, p_suc):
        """System has lost most refrigerant - emergency"""
        cf = 0.92
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Critical Refrigerant Loss - System Inoperable",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["complete_refrigerant_loss"],
            evidence_strength=2.0,
            recommended_action="DO NOT OPERATE. System has virtually no refrigerant. Leak must be found and sealed before recharge."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('complete_refrigerant_loss', f'Pdis={p_dis}, Psuc={p_suc}', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(temp_suction_line=MATCH.t_suc),
          TEST(lambda t_suc: t_suc > 15))
    def suction_line_too_warm_loss_of_cooling(self, t_suc):
        """Suction line warm indicates loss of evaporator cooling"""
        cf = 0.78
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Loss of Evaporator Cooling - Expansion Device or Charge Issue",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["suction_line_too_warm_loss_of_cooling"],
            evidence_strength=1.0,
            recommended_action="Check expansion device operation. Verify refrigerant charge. Check evaporator restriction."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('suction_line_too_warm_loss_of_cooling', f'Suction temp={t_suc}°C (>15)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(temp_liquid_line=MATCH.t_liquid,
                        temp_outdoor=MATCH.t_out),
          TEST(lambda t_liquid, t_out:
               (t_liquid - t_out) > 10))
    def high_subcooling_indication(self, t_liquid, t_out):
        """Excessive subcooling indicates overcharge or condenser fouling"""
        cf = 0.72
        diagnosis = DiagnosisConclusion(
            diagnosis_name="High Subcooling - Possible Overcharge",
            certainty_factor=cf,
            severity_level=2,
            rules_fired=["high_subcooling_indication"],
            evidence_strength=1.0,
            recommended_action="Reduce refrigerant charge slightly. Verify condenser is clean. Check liquid line restriction."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('high_subcooling_indication', f'Subcooling={(t_liquid-t_out)}°C (>10)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(refrigerant_charge_percent=MATCH.charge,
                        pressure_discharge=MATCH.p_dis),
          TEST(lambda charge, p_dis:
               (charge > 120) and (p_dis > 32)))
    def system_overcharge_critical(self, charge, p_dis):
        """System dangerously overcharged"""
        cf = 0.86
        diagnosis = DiagnosisConclusion(
            diagnosis_name="System Overcharge - High Pressure Risk",
            certainty_factor=cf,
            severity_level=4,
            rules_fired=["system_overcharge_critical"],
            evidence_strength=2.0,
            recommended_action="Recover excess refrigerant immediately. Discharge pressure >32 bar is dangerous."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('system_overcharge_critical', f'Charge={charge}% (>120), Pdis={p_dis} bar (>32)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(odor_present=MATCH.odor))
    def refrigerant_leak_by_smell(self, odor):
        """Refrigerant leak detected by smell"""
        if odor != 'refrigerant_leak':
            return
        cf = 0.85
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Refrigerant Leak - Odorant Detected",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["refrigerant_leak_by_smell"],
            evidence_strength=1.0,
            recommended_action="Use UV dye or ultrasonic to locate leak. Seal. Evacuate and recharge."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('refrigerant_leak_by_smell', 'Refrigerant odor detected', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(frost_condition=MATCH.frost))
    def frost_on_evaporator_coil_warning(self, frost):
        """Frost formation on outdoor coil (heat pump) or indoor coil (AC)"""
        if frost == 'none':
            return
        cf_map = {'minor': 0.50, 'moderate': 0.70, 'severe': 0.85}
        cf = cf_map.get(frost, 0.50)
        severity_map = {'minor': 1, 'moderate': 2, 'severe': 3}
        severity = severity_map.get(frost, 1)
        
        diagnosis = DiagnosisConclusion(
            diagnosis_name=f"Evaporator Frost - {frost.capitalize()} (Check Airflow/Charge)",
            certainty_factor=cf,
            severity_level=severity,
            rules_fired=["frost_on_evaporator_coil_warning"],
            evidence_strength=1.0,
            recommended_action="Check airflow, clean filter, verify refrigerant charge. Frost risk = system instability."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('frost_on_evaporator_coil_warning', f'Frost condition: {frost}', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(airflow_rate=MATCH.airflow,
                        equipment_type=MATCH.eq_type),
          TEST(lambda airflow, eq_type:
               (airflow < 100) and eq_type in ['air_conditioner', 'heat_pump']))
    def airflow_restriction_warning(self, airflow, eq_type):
        """Airflow significantly restricted"""
        cf = 0.75
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Airflow Restriction - Check Filter & Coil",
            certainty_factor=cf,
            severity_level=2,
            rules_fired=["airflow_restriction_warning"],
            evidence_strength=1.0,
            recommended_action="Replace air filter. Clean evaporator coil. Check ductwork for blockage."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('airflow_restriction_warning', f'Airflow={airflow} m³/min (<100)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(system_runtime_percent=MATCH.runtime_pct),
          TEST(lambda runtime_pct: runtime_pct > 85))
    def continuous_operation_warning(self, runtime_pct):
        """System running almost continuously"""
        cf = 0.68
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Continuous Operation - Inadequate Cooling/Heating",
            certainty_factor=cf,
            severity_level=2,
            rules_fired=["continuous_operation_warning"],
            evidence_strength=1.0,
            recommended_action="Check thermostat setpoint. Verify refrigerant charge. System may be undersized."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('continuous_operation_warning', f'Runtime={runtime_pct}% (>85)', diagnosis.diagnosis_name, cf)
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # ELECTRICAL & CONTROL ISSUES (Rules 31-38)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(compressor_current_draw=MATCH.current,
                        compressor_voltage=MATCH.voltage))
    def low_voltage_condition(self, current, voltage):
        """Supply voltage too low for safe operation"""
        if voltage >= 200:
            return
        cf = 0.80
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Low Supply Voltage - Electrical Issue",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["low_voltage_condition"],
            evidence_strength=1.0,
            recommended_action="Check electrical service panel. Voltage should be 220-240V. Call electrician if low."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('low_voltage_condition', f'Voltage={voltage}V (<200)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(compressor_current_draw=MATCH.current,
                        compressor_voltage=MATCH.voltage),
          TEST(lambda current, voltage:
               (current > 50) and (voltage > 220)))
    def extremely_high_motor_current(self, current, voltage):
        """Motor current dangerously high"""
        cf = 0.88
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Extremely High Motor Current - Imminent Burnout",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["extremely_high_motor_current"],
            evidence_strength=1.0,
            recommended_action="Shutdown immediately. Compressor overload. Check for mechanical jam or electrical short."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('extremely_high_motor_current', f'Current={current}A (>50), Voltage={voltage}V', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(odor_present=MATCH.odor))
    def burning_smell_electrical_hazard(self, odor):
        """Burning smell indicates electrical/thermal hazard"""
        if odor != 'burning':
            return
        cf = 0.90
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Burning Smell - Electrical Hazard - CRITICAL",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["burning_smell_electrical_hazard"],
            evidence_strength=1.0,
            recommended_action="STOP IMMEDIATELY. Fire hazard. Do not operate. Call professional emergency service."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('burning_smell_electrical_hazard', 'Burning odor detected', diagnosis.diagnosis_name, cf)
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # OIL & LUBRICATION ISSUES (Rules 39-44)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(oil_level_percent=MATCH.oil_level))
    def oil_level_critical(self, oil_level):
        """Oil level dangerously low"""
        if oil_level >= 40:
            return
        cf = 0.82
        severity = 3 if oil_level > 20 else 5
        diagnosis = DiagnosisConclusion(
            diagnosis_name=f"Critical Oil Level - {'Bearing Damage Risk' if oil_level < 20 else 'Add Oil'}",
            certainty_factor=cf,
            severity_level=severity,
            rules_fired=["oil_level_critical"],
            evidence_strength=1.0,
            recommended_action="Add compressor oil immediately if >20%. If <20%, risk of bearing damage. Add oil of correct type."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('oil_level_critical', f'Oil level={oil_level}% (<40)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(oil_color=MATCH.oil_color))
    def oil_degradation_warning(self, oil_color):
        """Oil color indicates degradation"""
        if oil_color == 'clear':
            return
        cf_map = {'light_yellow': 0.55, 'brown': 0.75, 'black': 0.85, 'foamy': 0.80}
        cf = cf_map.get(oil_color, 0.50)
        severity_map = {'light_yellow': 1, 'brown': 2, 'black': 4, 'foamy': 3}
        severity = severity_map.get(oil_color, 1)
        
        diagnosis = DiagnosisConclusion(
            diagnosis_name=f"Oil Degradation - {oil_color.replace('_', ' ').title()} (Change Oil)",
            certainty_factor=cf,
            severity_level=severity,
            rules_fired=["oil_degradation_warning"],
            evidence_strength=1.0,
            recommended_action="Change compressor oil. Degraded oil indicates moisture, oxidation, or overheating."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('oil_degradation_warning', f'Oil color: {oil_color}', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(oil_acid_number=MATCH.tan))
    def high_oil_acidity_warning(self, tan):
        """Oil acid number (TAN) too high"""
        if tan <= 0.5:
            return
        cf = 0.70 if tan <= 1.0 else 0.85
        severity = 2 if tan <= 1.0 else 3
        diagnosis = DiagnosisConclusion(
            diagnosis_name="High Oil Acidity - Change Oil Soon",
            certainty_factor=cf,
            severity_level=severity,
            rules_fired=["high_oil_acidity_warning"],
            evidence_strength=1.0,
            recommended_action="Schedule oil change within 2 weeks. High acid = moisture/oxidation. Threatens bearing life."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('high_oil_acidity_warning', f'Oil TAN={tan} (>0.5)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(oil_level_percent=MATCH.oil_level,
                        oil_color=MATCH.oil_color,
                        compressor_runtime_hours=MATCH.runtime),
          TEST(lambda oil_level, oil_color, runtime:
               (oil_level < 50) and (oil_color != 'clear') and (runtime > 40000)))
    def lubrication_system_degraded(self, oil_level, oil_color, runtime):
        """Combined oil system degradation"""
        cf = 0.78
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Lubrication System Degraded - Oil Change & Top-Up Required",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["lubrication_system_degraded"],
            evidence_strength=3.0,
            recommended_action="Immediate oil service: drain old oil, clean filter, add fresh oil. High runtime + poor condition = bearing risk."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('lubrication_system_degraded', f'Oil level={oil_level}%, Color={oil_color}, Runtime={runtime}h', diagnosis.diagnosis_name, cf)
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # HEAT EXCHANGER & CONDENSER ISSUES (Rules 45-51)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(temp_liquid_line=MATCH.t_liquid,
                        temp_outdoor=MATCH.t_out),
          TEST(lambda t_liquid, t_out:
               (t_liquid - t_out) < 2))
    def condenser_fouling_low_subcooling(self, t_liquid, t_out):
        """Condenser fouling - insufficient subcooling"""
        cf = 0.73
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Condenser Fouling - Low Subcooling",
            certainty_factor=cf,
            severity_level=2,
            rules_fired=["condenser_fouling_low_subcooling"],
            evidence_strength=1.0,
            recommended_action="Clean condenser coil. Check fan motor. Remove debris and leaves from outdoor unit."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('condenser_fouling_low_subcooling', f'Subcooling={(t_liquid-t_out)}°C (<2)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(temp_discharge_line=MATCH.t_dis,
                        temp_outdoor=MATCH.t_out),
          TEST(lambda t_dis, t_out:
               (t_dis - t_out) > 50))
    def high_discharge_superheat_extreme(self, t_dis, t_out):
        """Extremely high discharge superheat - approaching critical"""
        cf = 0.82
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Extreme Discharge Superheat - Condenser Failure Risk",
            certainty_factor=cf,
            severity_level=4,
            rules_fired=["high_discharge_superheat_extreme"],
            evidence_strength=1.0,
            recommended_action="Check condenser fan operation. Clean coil. High superheat = reduced cooling capacity, compressor stress."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('high_discharge_superheat_extreme', f'Superheat={(t_dis-t_out)}°C (>50)', diagnosis.diagnosis_name, cf)
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # BOILER/FURNACE SPECIFIC RULES (Rules 52-56)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(equipment_type=MATCH.eq_type,
                        pressure_discharge=MATCH.pressure),
          TEST(lambda eq_type, pressure:
               (eq_type in ['boiler', 'furnace']) and (pressure > 2.5)))
    def boiler_overpressure_safety(self, eq_type, pressure):
        """Boiler pressure above safe limit"""
        cf = 0.91
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Boiler Overpressure - Safety Hazard",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["boiler_overpressure_safety"],
            evidence_strength=1.0,
            recommended_action="STOP BOILER. Check relief valve. Test pressure gauge. Overpressure = explosion risk."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('boiler_overpressure_safety', f'Boiler pressure={pressure} bar (>2.5)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(odor_present=MATCH.odor,
                        equipment_type=MATCH.eq_type),
          TEST(lambda odor, eq_type:
               (odor == 'gas_smell') and (eq_type in ['furnace', 'boiler'])))
    def gas_leak_furnace_critical(self, odor, eq_type):
        """Natural gas leak detected in furnace/boiler"""
        cf = 0.93
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Gas Leak - Furnace/Boiler - CRITICAL SAFETY",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["gas_leak_furnace_critical"],
            evidence_strength=1.0,
            recommended_action="EVACUATE. Call gas company. Do not operate equipment. Potential CO poisoning."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('gas_leak_furnace_critical', 'Gas odor in furnace/boiler', diagnosis.diagnosis_name, cf)
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # ADVANCED MULTI-PARAMETER RULES (Rules 57-60)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(pressure_discharge=MATCH.p_dis,
                        pressure_suction=MATCH.p_suc,
                        compressor_current_draw=MATCH.current),
          TEST(lambda p_dis, p_suc, current:
               ((p_dis / p_suc) > 8.0) and current > 25))
    def high_compression_ratio_motor_stress(self, p_dis, p_suc, current):
        """High compression ratio causing motor stress"""
        cf = 0.76
        diagnosis = DiagnosisConclusion(
            diagnosis_name="High Compression Ratio - Motor Stress",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["high_compression_ratio_motor_stress"],
            evidence_strength=2.0,
            recommended_action="Verify refrigerant charge. Check suction line for restrictions. Reduce load or outdoor temp."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        cr = p_dis / p_suc
        self.tracer.log('high_compression_ratio_motor_stress', f'Compression ratio={cr:.1f} (>8.0)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(temp_indoor_actual=MATCH.t_indoor_actual,
                        temp_indoor_setpoint=MATCH.t_setpoint,
                        system_runtime_percent=MATCH.runtime_pct),
          TEST(lambda t_indoor_actual, t_setpoint, runtime_pct:
               (abs(t_indoor_actual - t_setpoint) > 5) and (runtime_pct > 70)))
    def poor_temperature_control(self, t_indoor_actual, t_setpoint, runtime_pct):
        """System unable to maintain setpoint despite running long"""
        cf = 0.70
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Poor Temperature Control - Low Capacity",
            certainty_factor=cf,
            severity_level=2,
            rules_fired=["poor_temperature_control"],
            evidence_strength=2.0,
            recommended_action="Check thermostat calibration. Verify refrigerant charge. May be undersized or air leak in ductwork."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        diff = abs(t_indoor_actual - t_setpoint)
        self.tracer.log('poor_temperature_control', f'Temp error={diff}°C (>5), Runtime={runtime_pct}% (>70)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(compressor_runtime_hours=MATCH.runtime,
                        equipment_age_years=MATCH.age,
                        last_service_days_ago=MATCH.days_service),
          TEST(lambda runtime, age, days_service:
               (runtime > 60000) and (age > 15) and (days_service > 180)))
    def end_of_life_approaching(self, runtime, age, days_service):
        """Equipment reaching end of design life"""
        cf = 0.80
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Equipment Approaching End of Life - Plan Replacement",
            certainty_factor=cf,
            severity_level=2,
            rules_fired=["end_of_life_approaching"],
            evidence_strength=3.0,
            recommended_action="Plan replacement within 12 months. Equipment is 15+ years old, 60k+ hours, overdue maintenance."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('end_of_life_approaching', f'Runtime={runtime}h, Age={age}y, Service overdue {days_service}d', diagnosis.diagnosis_name, cf)
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # ADDITIONAL CRITICAL RULES (Rules 61-71)
    # ─────────────────────────────────────────────────────────────────────────
    
    @Rule(SensorReading(pressure_suction=MATCH.p_suc,
                        pressure_discharge=MATCH.p_dis),
          TEST(lambda p_suc, p_dis:
               (p_suc > 0.5) and (p_dis < 10)))
    def vacuum_line_rupture_critical(self, p_suc, p_dis):
        """System has lost pressure - vacuum rupture"""
        cf = 0.89
        diagnosis = DiagnosisConclusion(
            diagnosis_name="System Vacuum Rupture - Critical Air Leak",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["vacuum_line_rupture_critical"],
            evidence_strength=2.0,
            recommended_action="EMERGENCY SERVICE. Vacuum rupture allows air into system. Moisture/acid damage. Find leak."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('vacuum_line_rupture_critical', f'Psuc={p_suc}, Pdis={p_dis}', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(temp_discharge_line=MATCH.t_dis,
                        temp_suction_line=MATCH.t_suc),
          TEST(lambda t_dis, t_suc:
               (t_dis < 60) and (t_suc > 5)))
    def system_not_cooling_complete_failure(self, t_dis, t_suc):
        """System completely failed to cool"""
        cf = 0.88
        diagnosis = DiagnosisConclusion(
            diagnosis_name="System Not Cooling - Complete Failure",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["system_not_cooling_complete_failure"],
            evidence_strength=2.0,
            recommended_action="System is completely inoperable. Check compressor operation, refrigerant charge, electrical."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('system_not_cooling_complete_failure', f'Tdis={t_dis}°C, Tsuc={t_suc}°C', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(compressor_current_draw=MATCH.current),
          TEST(lambda current: current < 2))
    def compressor_not_running_no_current(self, current):
        """Compressor not running - no electrical current"""
        cf = 0.91
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Compressor Not Running - Electrical Issue",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["compressor_not_running_no_current"],
            evidence_strength=1.0,
            recommended_action="Check power supply, contactor, compressor motor windings. May have blown fuse/breaker."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('compressor_not_running_no_current', f'Current={current}A (<2)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(system_runtime_percent=MATCH.runtime_pct),
          TEST(lambda runtime_pct: runtime_pct == 0))
    def system_not_cycling_control_issue(self, runtime_pct):
        """System not cycling at all - thermostat or control issue"""
        cf = 0.85
        diagnosis = DiagnosisConclusion(
            diagnosis_name="System Not Cycling - Thermostat/Control Fault",
            certainty_factor=cf,
            severity_level=4,
            rules_fired=["system_not_cycling_control_issue"],
            evidence_strength=1.0,
            recommended_action="Check thermostat setpoint and sensor. Verify control circuit voltage. May need thermostat replacement."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('system_not_cycling_control_issue', 'Runtime=0%', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(temp_suction_line=MATCH.t_suc,
                        temp_evaporator_outlet=MATCH.t_evo),
          TEST(lambda t_suc, t_evo:
               (t_suc > t_evo + 8) and (t_suc > 10)))
    def high_superheat_expansion_device_issue(self, t_suc, t_evo):
        """Very high superheat - expansion device malfunction"""
        cf = 0.79
        diagnosis = DiagnosisConclusion(
            diagnosis_name="High Superheat - Expansion Device Fault",
            certainty_factor=cf,
            severity_level=3,
            rules_fired=["high_superheat_expansion_device_issue"],
            evidence_strength=1.0,
            recommended_action="Check expansion valve/TXV operation. Possible ice formation blocking flow. Replace if defective."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        superheat = t_suc - t_evo
        self.tracer.log('high_superheat_expansion_device_issue', f'Superheat={superheat}°C (>8)', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(temp_liquid_line=MATCH.t_liquid,
                        temp_discharge_line=MATCH.t_dis),
          TEST(lambda t_liquid, t_dis:
               (t_liquid > 60) and (t_dis > 100)))
    def condenser_completely_failed(self, t_liquid, t_dis):
        """Condenser has completely failed - no cooling occurring"""
        cf = 0.86
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Condenser Complete Failure - Cooling Loop Broken",
            certainty_factor=cf,
            severity_level=4,
            rules_fired=["condenser_completely_failed"],
            evidence_strength=2.0,
            recommended_action="Condenser fan not running or coil blocked/frozen. Check fan motor, verify airflow, clean coil."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('condenser_completely_failed', f'Tliq={t_liquid}°C, Tdis={t_dis}°C', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(airflow_rate=MATCH.airflow),
          TEST(lambda airflow: airflow == 0))
    def zero_airflow_complete_blockage(self, airflow):
        """Zero airflow - complete ductwork blockage"""
        cf = 0.93
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Zero Airflow - Ductwork Completely Blocked",
            certainty_factor=cf,
            severity_level=4,
            rules_fired=["zero_airflow_complete_blockage"],
            evidence_strength=1.0,
            recommended_action="Check for collapsed ductwork, blockage, or fan motor failure. System cannot function."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('zero_airflow_complete_blockage', 'Airflow=0 m³/min', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(equipment_type=MATCH.eq_type),
          TEST(lambda eq_type: eq_type not in ['air_conditioner', 'heat_pump', 'furnace', 'boiler', 'chiller']))
    def unknown_equipment_type(self, eq_type):
        """Unknown equipment type - cannot diagnose"""
        cf = 0.0
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Unknown Equipment Type - Cannot Diagnose",
            certainty_factor=cf,
            severity_level=0,
            rules_fired=["unknown_equipment_type"],
            evidence_strength=0.0,
            recommended_action="Equipment type not recognized. Please select from: AC, Heat Pump, Furnace, Boiler, or Chiller."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('unknown_equipment_type', f'Equipment type={eq_type}', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(oil_level_percent=MATCH.oil_level,
                        noise_level=MATCH.noise,
                        compressor_runtime_hours=MATCH.runtime),
          TEST(lambda oil_level, noise, runtime:
               (oil_level < 20) and (noise == 'grinding') and (runtime > 70000)))
    def catastrophic_bearing_failure(self, oil_level, noise, runtime):
        """Catastrophic bearing failure imminent - metal debris likely"""
        cf = 0.95
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Catastrophic Bearing Failure - Metal Debris Risk",
            certainty_factor=cf,
            severity_level=5,
            rules_fired=["catastrophic_bearing_failure"],
            evidence_strength=3.0,
            recommended_action="SHUTDOWN IMMEDIATELY. Bearing has catastrophic damage. Compressor replacement required."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('catastrophic_bearing_failure', f'Oil={oil_level}%, Noise={noise}, Runtime={runtime}h', diagnosis.diagnosis_name, cf)
    
    @Rule(SensorReading(temp_outdoor=MATCH.t_out,
                        temp_indoor_setpoint=MATCH.t_set,
                        system_runtime_percent=MATCH.runtime_pct),
          TEST(lambda t_out, t_set, runtime_pct:
               (t_out > 45) and (t_set < 25) and (runtime_pct > 95)))
    def outdoor_temp_exceeds_capacity(self, t_out, t_set, runtime_pct):
        """Outdoor temperature exceeds equipment capacity - running maximum"""
        cf = 0.72
        diagnosis = DiagnosisConclusion(
            diagnosis_name="Outdoor Temp Exceeds Equipment Capacity",
            certainty_factor=cf,
            severity_level=1,
            rules_fired=["outdoor_temp_exceeds_capacity"],
            evidence_strength=1.0,
            recommended_action="Normal condition. At extreme outdoor temps (>45°C), equipment cannot maintain setpoint. Reduce setpoint."
        )
        self.conflict_resolver.add_diagnosis(diagnosis)
        self.tracer.log('outdoor_temp_exceeds_capacity', f'Outdoor={t_out}°C, Setpoint={t_set}°C, Runtime={runtime_pct}%', diagnosis.diagnosis_name, cf)
    
    
    # ─────────────────────────────────────────────────────────────────────────
    # ENGINE CONTROL & RESULT AGGREGATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def get_top_diagnosis(self) -> Tuple[str, float, int]:
        """
        Get the top diagnosis from conflict resolution.
        
        Returns:
            Tuple of (diagnosis_name, certainty_factor, severity_level)
        """
        top = self.conflict_resolver.resolve()
        return (top.diagnosis_name, top.certainty_factor, top.severity_level)
    
    def get_top_n_diagnoses(self, n: int = 3) -> List[DiagnosisConclusion]:
        """
        Get top N diagnoses for displaying alternatives.
        
        Returns:
            List of DiagnosisConclusion objects
        """
        return self.conflict_resolver.resolve_top_n(n)
    
    def get_explanation(self) -> str:
        """Get full reasoning trace from tracer"""
        return self.tracer.get_explanation()
    
    def reset_session(self):
        """Clear diagnoses for new run"""
        self.conflict_resolver.clear()
        self.tracer.clear()
        self.all_diagnoses.clear()
        self.session_log.clear()


if __name__ == "__main__":
    # Test the engine
    engine = PredictiveMaintenanceEngine()
    engine.reset()
    
    # Declare test facts
    engine.declare(SensorReading(
        equipment_type='air_conditioner',
        temp_discharge_line=75,
        temp_suction_line=5,
        pressure_discharge=20,
        pressure_suction=2.5,
        compressor_current_draw=18,
        oil_level_percent=70,
        noise_level='normal',
        equipment_age_years=5
    ))
    
    # Run inference
    engine.run()
    
    # Get results
    diagnosis, cf, severity = engine.get_top_diagnosis()
    print(f"Diagnosis: {diagnosis}")
    print(f"Certainty: {cf*100:.0f}%")
    print(f"Severity: {severity}")
    print(f"\nReasoning:\n{engine.get_explanation()}")
