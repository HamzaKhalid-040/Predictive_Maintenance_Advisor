"""
Test Scenarios for Predictive Maintenance Expert System

10+ test cases covering:
- Normal operation (baseline)
- Critical failures
- Warning conditions
- Edge cases
- Equipment age factors
- Refrigerant system issues

Each test declares sensor facts and verifies the diagnosis matches expected output.
Run with: python -m pytest tests/test_scenarios.py -v
"""

import sys
import os

# Add parent directory to path to allow imports from sibling packages
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from inference.engine import PredictiveMaintenanceEngine
from knowledge_base.facts import SensorReading, EquipmentInfo


class TestNormalOperation:
    """Test baseline normal operation scenarios"""
    
    def test_ac_normal_operation(self):
        """Air conditioner in perfect operating condition"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='air_conditioner',
            temp_outdoor=25.0,
            temp_indoor_setpoint=22.0,
            temp_indoor_actual=22.0,
            temp_discharge_line=75.0,
            temp_suction_line=5.0,
            temp_evaporator_outlet=5.0,
            pressure_discharge=20.0,
            pressure_suction=2.5,
            compressor_current_draw=18.0,
            compressor_voltage=230.0,
            compressor_runtime_hours=5000.0,
            refrigerant_charge_percent=100.0,
            oil_level_percent=70.0,
            oil_color='clear',
            noise_level='normal',
            equipment_age_years=3.0,
            last_service_days_ago=30
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        # Expected: Normal operation
        assert severity == 0, f"Expected severity 0, got {severity}"
        assert "normal" in diagnosis.lower(), f"Expected normal diagnosis, got {diagnosis}"
        assert cf >= 0.95, f"Expected high certainty (>=0.95), got {cf}"
    
    def test_heat_pump_normal_operation(self):
        """Heat pump in normal condition (heating mode)"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='heat_pump',
            temp_outdoor=-5.0,
            temp_indoor_setpoint=21.0,
            temp_indoor_actual=21.0,
            temp_discharge_line=80.0,
            temp_suction_line=0.0,
            temp_evaporator_outlet=0.0,
            pressure_discharge=22.0,
            pressure_suction=2.2,
            compressor_current_draw=20.0,
            compressor_voltage=230.0,
            compressor_runtime_hours=12000.0,
            refrigerant_charge_percent=100.0,
            oil_level_percent=65.0,
            oil_color='clear',
            noise_level='normal',
            equipment_age_years=6.0,
            last_service_days_ago=45
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        assert severity <= 2, f"Expected low severity, got {severity}"
        assert cf >= 0.60, f"Expected reasonable confidence, got {cf}"


class TestCriticalFailures:
    """Test critical failure scenarios (Severity 5)"""
    
    def test_compressor_burnout_critical(self):
        """Compressor burnout with multiple critical indicators"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='air_conditioner',
            temp_discharge_line=115.0,  # Extreme discharge temp
            temp_suction_line=2.0,
            pressure_discharge=28.0,
            pressure_suction=3.0,
            compressor_current_draw=45.0,  # Motor overloaded
            oil_color='black',  # Burned oil
            noise_level='grinding',  # Critical noise
            equipment_age_years=15.0,
            last_service_days_ago=200
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        assert severity == 5, f"Expected severity 5 (critical), got {severity}"
        assert cf >= 0.85, f"Expected high certainty for critical failure, got {cf}"
        print(f"✓ Burnout test passed: {diagnosis} (CF={cf*100:.0f}%)")
    
    def test_liquid_slugging_critical(self):
        """Liquid slugging - extreme risk of compressor damage"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='chiller',
            temp_suction_line=-18.0,  # Extreme superheat
            pressure_suction=0.8,  # Very low
            pressure_discharge=25.0,
            compressor_current_draw=25.0,
            noise_level='hissing',  # Severe noise
            equipment_age_years=8.0,
            last_service_days_ago=100
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        assert severity >= 4, f"Expected high severity (>=4), got {severity}"
        assert cf >= 0.80, f"Expected high certainty, got {cf}"
        print(f"✓ Liquid slugging test passed: {diagnosis} (CF={cf*100:.0f}%)")


class TestWarningConditions:
    """Test warning conditions (Severity 3-4)"""
    
    def test_refrigerant_leak_warning(self):
        """Significant refrigerant leak reducing system capacity"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='air_conditioner',
            temp_suction_line=-12.0,  # High superheat
            pressure_suction=1.3,  # Low suction pressure
            pressure_discharge=18.0,  # Low discharge pressure
            compressor_current_draw=15.0,
            refrigerant_charge_percent=75.0,  # Undercharged
            equipment_age_years=5.0,
            last_service_days_ago=60
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        assert severity >= 3, f"Expected warning severity (>=3), got {severity}"
        assert "leak" in diagnosis.lower() or "charge" in diagnosis.lower(), \
            f"Expected refrigerant-related diagnosis, got {diagnosis}"
        print(f"✓ Refrigerant leak test passed: {diagnosis} (Severity={severity})")
    
    def test_high_discharge_temperature_warning(self):
        """High discharge temperature indicating cooling system stress"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='air_conditioner',
            temp_discharge_line=95.0,  # Elevated discharge temp
            pressure_discharge=30.0,  # Elevated pressure
            temp_outdoor=40.0,  # High outdoor temp
            compressor_current_draw=28.0,  # High current
            equipment_age_years=7.0,
            last_service_days_ago=120
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        assert severity >= 2, f"Expected warning severity (>=2), got {severity}"
        assert cf >= 0.60, f"Expected reasonable confidence, got {cf}"
        print(f"✓ High discharge temp test passed: {diagnosis} (CF={cf*100:.0f}%)")
    
    def test_bearing_wear_warning(self):
        """Compressor bearing wear from high hours and low oil"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='air_conditioner',
            compressor_runtime_hours=60000.0,  # High hours
            oil_level_percent=25.0,  # Very low oil
            oil_color='brown',  # Degraded
            noise_level='grinding',  # Wear noise
            equipment_age_years=18.0,  # Old equipment
            last_service_days_ago=200
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        assert severity >= 3, f"Expected warning/alert (>=3), got {severity}"
        assert "bearing" in diagnosis.lower() or "wear" in diagnosis.lower(), \
            f"Expected bearing-related diagnosis, got {diagnosis}"
        print(f"✓ Bearing wear test passed: {diagnosis} (Severity={severity})")


class TestMonitoringConditions:
    """Test monitoring/preventive conditions (Severity 1-2)"""
    
    def test_overdue_maintenance_monitor(self):
        """Equipment overdue for routine maintenance"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='furnace',
            temp_discharge_line=70.0,  # Normal
            pressure_discharge=20.0,  # Normal
            compressor_current_draw=15.0,  # Normal
            noise_level='normal',  # Normal
            last_service_days_ago=450,  # Overdue (>365 days)
            equipment_age_years=5.0
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        assert severity <= 2, f"Expected monitor severity (<=2), got {severity}"
        assert "maintenance" in diagnosis.lower() or "service" in diagnosis.lower(), \
            f"Expected maintenance reminder, got {diagnosis}"
        print(f"✓ Overdue maintenance test passed: {diagnosis}")
    
    def test_clogged_air_filter_monitor(self):
        """Clogged air filter reducing airflow"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='air_conditioner',
            airflow_rate=120.0,  # Reduced airflow (normal ~200)
            temp_suction_line=-8.0,  # Slightly elevated superheat
            pressure_suction=2.0,  # Slightly low
            system_runtime_percent=70.0,  # Running longer
            equipment_age_years=4.0,
            last_service_days_ago=120
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        assert severity <= 2, f"Expected low severity, got {severity}"
        print(f"✓ Clogged filter test passed: {diagnosis}")
    
    def test_aging_equipment_monitor(self):
        """Equipment 20 years old - approaching end of life"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='air_conditioner',
            temp_discharge_line=72.0,  # Normal
            pressure_discharge=20.0,  # Normal
            compressor_current_draw=16.0,  # Normal
            noise_level='normal',  # Normal
            equipment_age_years=22.0,  # Very old
            last_service_days_ago=90
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        assert severity <= 2, f"Expected monitor severity, got {severity}"
        assert "old" in diagnosis.lower() or "age" in diagnosis.lower() or "replacement" in diagnosis.lower(), \
            f"Expected age-related diagnosis, got {diagnosis}"
        print(f"✓ Aging equipment test passed: {diagnosis}")


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_borderline_high_temperature(self):
        """Temperature just above normal threshold"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='air_conditioner',
            temp_discharge_line=86.0,  # Just above normal (85°C threshold)
            pressure_discharge=27.0,  # Just above normal
            equipment_age_years=5.0,
            last_service_days_ago=60
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        # Should flag as warning/monitor, not critical
        assert severity <= 3, f"Expected moderate severity, got {severity}"
        print(f"✓ Borderline high temp test passed: {diagnosis}")
    
    def test_very_young_equipment(self):
        """Brand new equipment - should not trigger age-related issues"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='heat_pump',
            temp_discharge_line=75.0,
            pressure_discharge=21.0,
            equipment_age_years=0.5,  # 6 months old
            last_service_days_ago=0  # Just installed
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        # Should not show age-related warnings
        assert "old" not in diagnosis.lower(), f"Unexpected age warning for new equipment: {diagnosis}"
        print(f"✓ Young equipment test passed: {diagnosis}")


class TestMultipleSymptoms:
    """Test combined multi-symptom scenarios"""
    
    def test_multiple_stress_indicators(self):
        """Multiple stress indicators pointing to same problem"""
        engine = PredictiveMaintenanceEngine()
        engine.reset()
        
        engine.declare(SensorReading(
            equipment_type='chiller',
            temp_discharge_line=105.0,  # High
            pressure_discharge=35.0,  # High
            compressor_current_draw=85.0,  # High
            oil_color='brown',  # Degraded
            noise_level='loud',  # Abnormal
            equipment_age_years=10.0,
            last_service_days_ago=180
        ))
        
        engine.run()
        diagnosis, cf, severity = engine.get_top_diagnosis()
        
        # Multiple indicators should increase confidence
        assert cf >= 0.80, f"Expected high confidence from multiple symptoms, got {cf}"
        assert severity >= 3, f"Expected warning/alert, got {severity}"
        print(f"✓ Multiple symptoms test passed: {diagnosis} (CF={cf*100:.0f}%)")


# ═════════════════════════════════════════════════════════════════════════════
# PYTEST CONFIGURATION & EXECUTION
# ═════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Run tests manually without pytest"""
    
    print("\n" + "="*80)
    print("PREDICTIVE MAINTENANCE EXPERT SYSTEM - TEST SUITE")
    print("="*80 + "\n")
    
    # Instantiate test classes
    test_classes = [
        TestNormalOperation(),
        TestCriticalFailures(),
        TestWarningConditions(),
        TestMonitoringConditions(),
        TestEdgeCases(),
        TestMultipleSymptoms()
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        class_name = test_class.__class__.__name__
        print(f"\n📋 {class_name}")
        print("-" * 80)
        
        # Get all test methods
        test_methods = [m for m in dir(test_class) if m.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(test_class, method_name)
                method()
                passed_tests += 1
            except AssertionError as e:
                print(f"✗ {method_name}: {e}")
                failed_tests += 1
            except Exception as e:
                print(f"✗ {method_name}: Unexpected error - {e}")
                failed_tests += 1
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total Tests: {total_tests}")
    print(f"✓ Passed: {passed_tests}")
    print(f"✗ Failed: {failed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.0f}%")
    print("="*80 + "\n")
    
    if failed_tests == 0:
        print("🎉 All tests passed! System is working correctly.")
    else:
        print(f"⚠ {failed_tests} test(s) failed. Review the output above.")
