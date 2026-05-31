# Knowledge Acquisition and Rule Engineering

## Overview

This document describes how the 70+ expert rules were developed, validated, and integrated into the Predictive Maintenance Advisor system.

## Knowledge Sources

### Primary Sources
1. **HVAC Engineering Standards**
   - EPA 608 Certification Guidelines
   - ASHRAE Handbook - Fundamentals
   - Equipment manufacturer specifications

2. **Thermodynamic Principles**
   - Refrigeration cycle theory
   - Compressor operating limits
   - Heat transfer mechanisms

3. **Field Experience**
   - Real technician reports
   - Service call data
   - Failure mode analysis

4. **Industry Best Practices**
   - Preventive maintenance schedules
   - Diagnostic procedures
   - Root cause analysis methods

## Rule Development Process

### Step 1: Failure Mode Identification
For each equipment type, identified 20+ failure modes:
- Equipment type → AC, Heat Pump, Furnace, Boiler, Chiller
- Failure category → Compressor, Refrigerant, Heat Exchanger, Electrical, etc.
- Root causes → What conditions lead to this failure
- Symptoms → Observable indicators
- Consequences → Business impact

### Step 2: Sensor Threshold Determination

#### Temperature Thresholds
```
Discharge Temperature (°C):
  Normal: 60-90
  Warning: 90-100
  Critical: >100

Suction Temperature (°C):
  Normal: -5 to 10
  Undercharge: -12 to -5 (high superheat)
  Critical: <-15 (liquid slugging risk)
```

#### Pressure Thresholds
```
Discharge Pressure (bar):
  Normal: 15-28
  Warning: 28-32
  Critical: >32

Suction Pressure (bar):
  Normal: 2.0-4.5
  Low: 1.5-2.0 (undercharge)
  Critical: <1.2 (immediate failure risk)
```

#### Electrical Parameters
```
Compressor Current (A):
  Normal: 15-25 (AC), 20-30 (HP)
  Warning: 25-35
  Critical: >35

Supply Voltage (V):
  Normal: 220-240
  Warning: 200-220
  Critical: <200
```

### Step 3: Rule Certainty Factor Assignment

Used Dempster-Shafer theory to assign confidence levels:

```
Certainty Formula: CF_combined = CF1 + CF2 × (1 - CF1)

Example:
  Rule 1 (High Temp): CF = 0.70
  Rule 2 (High Pressure): CF = 0.80
  Combined: 0.70 + 0.80 × (1 - 0.70) = 0.94
```

### Step 4: Severity Level Mapping

| Severity | Level | Maintenance | Examples |
|----------|-------|-------------|----------|
| 0 | OK | None | Normal operation |
| 1-2 | Monitor | Schedule | Aging equipment, overdue service |
| 3-4 | Warning | Within 2 weeks | High temperature, bearing wear |
| 5 | Critical | Immediate | Burnout, gas leak, safety hazard |

### Step 5: Recommended Action Definition

Each rule includes technician-friendly guidance:
- What to check
- Diagnostic procedures
- Repair recommendations
- Safety warnings
- Cost implications

## Rule Categories (70+ Total)

### 1. Compressor Failures (15+ rules)
- Burnout (extreme heat + burnt oil)
- Thermal overload (high pressure + high temp)
- Bearing failure (grinding noise + low oil + hours)
- Valve damage (pressure imbalance)
- Winding short (current surge)
- Liquid slugging (extreme superheat + low pressure)

### 2. Refrigerant System (16+ rules)
- Leak detection (pressure drop + superheat + charge)
- Overcharge (high pressure + high current)
- Undercharge (low pressure + superheat)
- Complete loss (both pressures very low)
- Contamination (acid formation in oil)
- Expansion device blockage

### 3. Heat Exchanger (12+ rules)
- Condenser fouling (high discharge temp + pressure)
- Evaporator freeze-up (frost + low superheat)
- Tube leak (capacity loss)
- Corrosion (water contamination)
- Fan failure (no pressure drop)

### 4. Airflow & Fans (10+ rules)
- Filter clogged (high superheat + low superheat)
- Fan motor failure (no cooling)
- Ductwork leak (capacity loss)
- Blockage (zero airflow)
- Sensor malfunction

### 5. Electrical (8+ rules)
- Low voltage (less than 200V)
- High current (motor overload)
- Capacitor failure (won't start)
- Contactor failure (intermittent)
- Winding short (burning smell)

### 6. Control Systems (8+ rules)
- Thermostat malfunction (temperature error)
- Short-cycling (overshooting)
- Continuous operation (never cycles)
- Sensor failure (erratic readings)
- Control board failure (no response)

### 7. Boiler/Furnace (8+ rules)
- Gas leak (smell detection)
- Ignition failure (no heat)
- Scale buildup (pressure rise)
- Corrosion (internal leaks)
- Pressure relief stuck (overpressure)

## Validation Strategy

### Accuracy Testing
- 13 comprehensive test scenarios
- 100% pass rate requirement
- Multi-symptom validation
- Edge case handling

### Cross-Validation
- Real field data comparison
- Expert technician review
- Thermodynamic principle verification
- Safety standard compliance

## Rule Priority Resolution

When multiple rules fire:
1. **Severity First**: Higher severity diagnoses ranked higher
2. **Confidence Second**: Higher CF breaks severity ties
3. **Evidence Third**: More supporting rules increase priority

Example:
```
Diagnosis A: Bearing Failure, Severity 4, CF 0.92, 2 rules
Diagnosis B: High Temp, Severity 3, CF 0.85, 1 rule
→ Diagnosis A wins (higher severity)

Diagnosis A: Bearing Failure, Severity 4, CF 0.92
Diagnosis B: Compressor Burnout, Severity 4, CF 0.95
→ Diagnosis B wins (higher CF)
```

## Continuous Improvement

As new failure modes are discovered:
1. Document the failure mechanism
2. Identify sensor indicators
3. Assign certainty factor and severity
4. Create diagnostic rule
5. Add test case
6. Validate and deploy

## Future Enhancements

- [ ] Machine learning rule optimization
- [ ] Real-time sensor data integration
- [ ] Predictive forecasting (time-to-failure)
- [ ] Regional climate adaptation
- [ ] Equipment-specific customization
- [ ] Fuzzy logic membership functions
- [ ] Neural network confidence boosting

## References

- EPA Section 608 Certification Exam Study Guide
- ASHRAE Handbook - HVAC Systems and Equipment
- Danfoss Troubleshooting Guide
- Johnson Controls System Commissioning
- Field Service Reports (2023-2026)
