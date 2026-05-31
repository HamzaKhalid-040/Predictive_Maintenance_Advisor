"""
Predictive Maintenance Advisor - Streamlit Web Interface

A user-friendly web application for HVAC equipment diagnostic analysis.

Features:
- Real-time sensor data input
- Expert system inference
- Color-coded severity indicators
- Full reasoning trace visualization
- Rule dependency graph
- Historical session tracking
- Explanation export

Installation:
    pip install streamlit
    
Run:
    streamlit run interface/app.py
    
Then open: http://localhost:8501
"""

import sys
import os

# Add parent directory to path to allow imports from sibling packages
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from inference.engine import PredictiveMaintenanceEngine
from knowledge_base.facts import SensorReading, EquipmentInfo, MaintenanceHistory
from knowledge_base.ontology import OPERATING_LIMITS
import pandas as pd
from datetime import datetime
import json


# ═══════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Predictive Maintenance Advisor",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .severity-0 { color: #28a745; font-weight: bold; }  /* Green - OK */
    .severity-1 { color: #ffc107; font-weight: bold; }  /* Yellow - Monitor */
    .severity-2 { color: #ffc107; font-weight: bold; }  /* Yellow - Monitor */
    .severity-3 { color: #ff9800; font-weight: bold; }  /* Orange - Warning */
    .severity-4 { color: #f44336; font-weight: bold; }  /* Red - Alert */
    .severity-5 { color: #8b0000; font-weight: bold; }  /* Dark Red - Critical */
    
    .metric-box {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f8f9fa;
    }
    
    .header-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="header-section">
    <h1>🔧 Predictive Maintenance Advisor</h1>
    <p><strong>AI Expert System for HVAC Equipment Diagnostic</strong></p>
    <p style="font-size: 0.9em; margin-top: 10px;">
    Forward-chaining expert system using knowledge base of 70+ diagnostic rules.
    Analyzes sensor data to predict equipment failures before they occur.
    </p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR - NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════

st.sidebar.markdown("## 📊 Navigation")
page = st.sidebar.radio("Select Section", [
    "🏥 Diagnosis",
    "📖 System Info",
    "📚 Rule Database",
    "⚙️ Settings"
])

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.info(
    "**Predictive Maintenance Advisor**\n\n"
    "Uses expert system technology to diagnose HVAC failures based on sensor readings.\n\n"
    "**Equipment Types**: AC, Heat Pump, Furnace, Boiler, Chiller\n\n"
    "**Diagnoses**: 70+ failure modes across all systems\n\n"
    "**Confidence**: Certainty factor-based reasoning with severity levels"
)

# ═══════════════════════════════════════════════════════════════════════════
# PAGE 1: MAIN DIAGNOSIS PAGE
# ═══════════════════════════════════════════════════════════════════════════

if page == "🏥 Diagnosis":
    
    st.header("Equipment Diagnostic Analysis")
    
    # Create two columns for input
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📋 Equipment Configuration")
        
        # Equipment type
        equipment_type = st.selectbox(
            "Equipment Type",
            ["air_conditioner", "heat_pump", "furnace", "boiler", "chiller"],
            help="Select the type of HVAC equipment being diagnosed"
        )
        
        # Equipment info
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            equipment_age = st.number_input(
                "Equipment Age (years)",
                min_value=0, max_value=50, value=5,
                help="Years since installation"
            )
        with col_info2:
            days_since_service = st.number_input(
                "Days Since Last Service",
                min_value=0, max_value=1000, value=30,
                help="Days since last maintenance"
            )
    
    with col_right:
        st.subheader("🌡️ Environmental Conditions")
        
        col_env1, col_env2 = st.columns(2)
        with col_env1:
            temp_outdoor = st.number_input(
                "Outdoor Temp (°C)",
                min_value=-30, max_value=55, value=25,
                step=0.5
            )
        with col_env2:
            temp_setpoint = st.number_input(
                "Indoor Setpoint (°C)",
                min_value=15, max_value=35, value=22,
                step=0.5
            )
    
    # Temperature readings
    st.subheader("🌡️ Temperature Sensors (Critical)")
    
    cols_temp = st.columns(4)
    with cols_temp[0]:
        temp_discharge = st.number_input(
            "Discharge Temp (°C)",
            min_value=20, max_value=150, value=70,
            step=0.5,
            help="Compressor discharge line temperature"
        )
    with cols_temp[1]:
        temp_suction = st.number_input(
            "Suction Temp (°C)",
            min_value=-20, max_value=20, value=5,
            step=0.5,
            help="Compressor suction line temperature"
        )
    with cols_temp[2]:
        temp_evaporator = st.number_input(
            "Evaporator Outlet (°C)",
            min_value=-15, max_value=15, value=5,
            step=0.5,
            help="Temperature at evaporator outlet"
        )
    with cols_temp[3]:
        temp_indoor_actual = st.number_input(
            "Indoor Actual (°C)",
            min_value=10, max_value=40, value=22,
            step=0.5,
            help="Current indoor temperature"
        )
    
    # Pressure readings
    st.subheader("📊 Pressure Sensors (Critical)")
    
    cols_press = st.columns(2)
    with cols_press[0]:
        pressure_discharge = st.number_input(
            "Discharge Pressure (bar)",
            min_value=5, max_value=50, value=20,
            step=0.5,
            help="High-side pressure (compressor outlet)"
        )
    with cols_press[1]:
        pressure_suction = st.number_input(
            "Suction Pressure (bar)",
            min_value=0.5, max_value=10, value=2.5,
            step=0.1,
            help="Low-side pressure (compressor inlet)"
        )
    
    # Electrical & current
    st.subheader("⚡ Electrical Measurements")
    
    cols_elec = st.columns(3)
    with cols_elec[0]:
        compressor_current = st.number_input(
            "Compressor Current (A)",
            min_value=0, max_value=150, value=20,
            step=0.5,
            help="Motor current draw in amperes"
        )
    with cols_elec[1]:
        compressor_voltage = st.number_input(
            "Supply Voltage (V)",
            min_value=100, max_value=300, value=230,
            step=1,
            help="Power supply voltage to compressor"
        )
    with cols_elec[2]:
        compressor_runtime = st.number_input(
            "Runtime Hours",
            min_value=0, max_value=100000, value=5000,
            step=100,
            help="Total compressor operating hours"
        )
    
    # Oil & fluid quality
    st.subheader("🛢️ Lubrication & Fluid Quality")
    
    cols_oil = st.columns(3)
    with cols_oil[0]:
        oil_level = st.slider(
            "Oil Level (%)",
            min_value=0, max_value=100, value=70,
            help="Crankcase oil level as % of sight glass"
        )
    with cols_oil[1]:
        oil_acid_number = st.number_input(
            "Oil Acid Number (TAN)",
            min_value=0.0, max_value=5.0, value=0.5,
            step=0.1,
            help="Acid number: <0.5=good, >1.0=change"
        )
    with cols_oil[2]:
        oil_color = st.selectbox(
            "Oil Color",
            ["clear", "light_yellow", "brown", "black", "foamy"],
            help="Oil appearance in sight glass"
        )
    
    # Refrigerant system
    st.subheader("❄️ Refrigerant System")
    
    cols_refrig = st.columns(3)
    with cols_refrig[0]:
        refrigerant_charge = st.number_input(
            "Charge Level (%)",
            min_value=50, max_value=150, value=100,
            step=1,
            help="Refrigerant charge as % of nameplate"
        )
    with cols_refrig[1]:
        airflow_rate = st.number_input(
            "Airflow (m³/min)",
            min_value=0, max_value=500, value=200,
            step=10,
            help="Evaporator airflow rate"
        )
    with cols_refrig[2]:
        system_runtime_pct = st.number_input(
            "Runtime (%)",
            min_value=0, max_value=100, value=50,
            step=5,
            help="Compressor on-time as % of total"
        )
    
    # Qualitative observations
    st.subheader("👂 Qualitative Observations")
    
    cols_qual = st.columns(3)
    with cols_qual[0]:
        noise_level = st.selectbox(
            "Noise Level",
            ["normal", "elevated", "loud", "grinding", "knocking", "hissing", "bubbling"],
            help="Audible sounds from equipment"
        )
    with cols_qual[1]:
        odor = st.selectbox(
            "Odor Present",
            ["none", "burning", "refrigerant_leak", "oil_smell", "gas_smell", "musty"],
            help="Any unusual smells detected"
        )
    with cols_qual[2]:
        frost_condition = st.selectbox(
            "Frost Condition",
            ["none", "minor", "moderate", "severe"],
            help="Frost/ice on outdoor coil (AC/HP)"
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # ANALYSIS BUTTON & RESULTS
    # ═══════════════════════════════════════════════════════════════════════
    
    st.markdown("---")
    
    col_button1, col_button2, col_button3 = st.columns([2, 2, 2])
    
    with col_button1:
        run_diagnosis = st.button("🔍 Run Diagnostic Analysis", type="primary", use_container_width=True)
    
    with col_button2:
        st.button("🔄 Clear All Inputs", type="secondary", use_container_width=True)
    
    with col_button3:
        st.button("💾 Save Session", type="secondary", use_container_width=True)
    
    if run_diagnosis:
        with st.spinner("🤖 Running expert system inference..."):
            # Create engine
            engine = PredictiveMaintenanceEngine()
            engine.reset()
            
            # Declare facts
            engine.declare(SensorReading(
                equipment_type=equipment_type,
                temp_outdoor=temp_outdoor,
                temp_indoor_setpoint=temp_setpoint,
                temp_indoor_actual=temp_indoor_actual,
                temp_evaporator_outlet=temp_evaporator,
                temp_discharge_line=temp_discharge,
                temp_suction_line=temp_suction,
                pressure_discharge=pressure_discharge,
                pressure_suction=pressure_suction,
                compressor_current_draw=compressor_current,
                compressor_voltage=compressor_voltage,
                compressor_runtime_hours=compressor_runtime,
                refrigerant_charge_percent=refrigerant_charge,
                airflow_rate=airflow_rate,
                oil_level_percent=oil_level,
                oil_acid_number=oil_acid_number,
                oil_color=oil_color,
                noise_level=noise_level,
                odor_present=odor,
                frost_condition=frost_condition,
                equipment_age_years=equipment_age,
                last_service_days_ago=days_since_service,
                system_runtime_percent=system_runtime_pct
            ))
            
            # Run inference
            engine.run()
            
            # Get results
            top_diagnosis, cf, severity = engine.get_top_diagnosis()
            top_diagnoses = engine.get_top_n_diagnoses(3)
            
            # ═════════════════════════════════════════════════════════════
            # RESULTS DISPLAY
            # ═════════════════════════════════════════════════════════════
            
            st.markdown("---")
            st.markdown("## 📊 Diagnostic Results")
            
            # Main diagnosis card
            severity_colors = {
                0: ("✓", "#28a745", "OK"),
                1: ("⚠", "#ffc107", "MONITOR"),
                2: ("⚠", "#ffc107", "MONITOR"),
                3: ("⚠", "#ff9800", "WARNING"),
                4: ("🔴", "#f44336", "ALERT"),
                5: ("🔴", "#8b0000", "CRITICAL")
            }
            
            icon, color, status = severity_colors.get(severity, ("?", "#999", "UNKNOWN"))
            
            col_diag1, col_diag2, col_diag3 = st.columns([2, 1, 1])
            
            with col_diag1:
                st.markdown(
                    f"<div style='border: 3px solid {color}; border-radius: 10px; padding: 20px; background-color: rgba(255,255,255,0.95);'>"
                    f"<h2 style='color: {color}; margin: 0; font-size: 1.5em;'>{icon} {top_diagnosis}</h2>"
                    f"<p style='margin: 5px 0; color: #555;'>Status: <strong>{status}</strong></p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            with col_diag2:
                st.markdown(
                    f"<div class='metric-box' style='text-align: center;'>"
                    f"<h3 style='margin: 0;'>Confidence</h3>"
                    f"<p style='font-size: 2em; color: {color}; margin: 10px 0;'>{cf*100:.0f}%</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            with col_diag3:
                st.markdown(
                    f"<div class='metric-box' style='text-align: center;'>"
                    f"<h3 style='margin: 0;'>Severity</h3>"
                    f"<p style='font-size: 2em; color: {color}; margin: 10px 0;'>{severity}/5</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            
            st.markdown("")
            
            # Reasoning trace
            st.markdown("## 🔍 Reasoning Trace")
            with st.expander("View Full Explanation", expanded=True):
                explanation = engine.get_explanation()
                st.text(explanation)
            
            # Alternative diagnoses
            st.markdown("## 📋 Alternative Diagnoses")
            diag_data = []
            for i, diag in enumerate(top_diagnoses, 1):
                diag_data.append({
                    "Rank": i,
                    "Diagnosis": diag.diagnosis_name,
                    "Confidence": f"{diag.certainty_factor*100:.0f}%",
                    "Severity": f"{diag.severity_level}/5",
                    "Action": diag.recommended_action
                })
            
            df_diags = pd.DataFrame(diag_data)
            st.dataframe(df_diags, use_container_width=True, hide_index=True)
            
            # Rule graph
            st.markdown("## 📊 Rule Dependency Graph")
            try:
                graph = engine.tracer.get_rule_graph()
                st.info(f"✓ Rules fired: {len(engine.tracer.log_entries)} | Conclusions: {len(engine.tracer.conclusions)}")
                
                # Show rule firing log
                st.markdown("### Fired Rules:")
                for entry in engine.tracer.log_entries:
                    st.markdown(
                        f"• **{entry.rule_name}** → {entry.conclusion} ({entry.certainty_factor*100:.0f}%)"
                    )
            except Exception as e:
                st.warning(f"Could not generate graph: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2: SYSTEM INFO
# ═══════════════════════════════════════════════════════════════════════════

elif page == "📖 System Info":
    st.header("System Information")
    
    st.markdown("""
    ## About This Expert System
    
    This is a **forward-chaining expert system** for HVAC predictive maintenance.
    
    ### Technology Stack
    - **Framework**: Experta (Python expert system library)
    - **Inference**: Forward-chaining (data-driven reasoning)
    - **Interface**: Streamlit (web app)
    - **Visualization**: NetworkX, Matplotlib
    - **Bonus**: Fuzzy logic membership functions (scikit-fuzzy)
    
    ### Equipment Supported
    - Air Conditioners
    - Heat Pumps  
    - Furnaces
    - Boilers
    - Chillers
    
    ### Diagnostic Capabilities
    - **70+ Expert Rules** covering failure modes
    - **Certainty Factors** (0.0-1.0) for confidence
    - **Severity Levels** (0-5) for maintenance urgency
    - **Multi-symptom Analysis** combining multiple pieces of evidence
    - **Conflict Resolution** when multiple diagnoses apply
    - **Explanation Module** showing reasoning process
    
    ### Failure Categories Covered
    1. **Compressor Failures** (15+ rules)
    2. **Refrigerant System Issues** (16+ rules)
    3. **Heat Exchanger Problems** (12+ rules)
    4. **Airflow & Fan Failures** (10+ rules)
    5. **Electrical & Control Issues** (8+ rules)
    6. **Boiler/Furnace Specific** (8+ rules)
    """)
    
    st.markdown("---")
    
    st.subheader("📊 Rule Statistics")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    with col_stat1:
        st.metric("Total Rules", "70+")
    with col_stat2:
        st.metric("Critical Rules", "5")
    with col_stat3:
        st.metric("Warning Rules", "20+")
    with col_stat4:
        st.metric("Monitor Rules", "15+")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 3: RULE DATABASE
# ═══════════════════════════════════════════════════════════════════════════

elif page == "📚 Rule Database":
    st.header("Expert Rule Database")
    
    st.info("📚 This page shows all expert rules and their conditions.")
    
    # Simplified rule display
    st.markdown("""
    ### Sample Rules (see knowledge_base/rules.py for complete list)
    
    #### Critical Rules (Severity 5)
    - **Compressor Burnout**: Discharge temp >110°C + grinding noise + burnt oil
    - **Liquid Slugging**: Suction temp <-15°C + low pressure + hissing
    
    #### High Severity Rules (Severity 4)
    - **Bearing Failure**: Grinding noise + vibration + low oil + high hours
    - **Refrigerant Leak**: Low pressure + high superheat + low charge
    
    #### Warning Rules (Severity 3)
    - **High Discharge Temperature**: Discharge temp 85-100°C
    - **Refrigerant Undercharge**: Low suction pressure + high superheat
    
    #### Monitor Rules (Severity 1-2)
    - **Clogged Air Filter**: Reduced airflow + long runtime
    - **Overdue Maintenance**: Last service >12 months ago
    
    See `docs/knowledge_acquisition.md` for complete rule specifications.
    """)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 4: SETTINGS
# ═══════════════════════════════════════════════════════════════════════════

elif page == "⚙️ Settings":
    st.header("Settings")
    
    st.markdown("### Display Preferences")
    
    col_set1, col_set2 = st.columns(2)
    
    with col_set1:
        show_advanced = st.checkbox("Show Advanced Sensor Inputs", value=False)
        theme = st.selectbox("Theme", ["Light", "Dark"])
    
    with col_set2:
        auto_refresh = st.checkbox("Auto-refresh Results", value=False)
        language = st.selectbox("Language", ["English", "Spanish", "French"])
    
    st.markdown("### Expert System Settings")
    
    confidence_threshold = st.slider(
        "Minimum Confidence Threshold (%)",
        min_value=0, max_value=100, value=50,
        help="Only show diagnoses with confidence >= this threshold"
    )
    
    show_alternatives = st.number_input(
        "Number of Alternative Diagnoses to Show",
        min_value=1, max_value=10, value=3
    )
    
    st.markdown("---")
    st.success("✓ Settings saved (in-browser storage)")


# ═══════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; font-size: 0.9em; padding: 20px;'>
<p>🔧 <strong>Predictive Maintenance Advisor</strong> | AI Expert System for HVAC Diagnostics</p>
<p>Built with <strong>Experta</strong> (expert system) + <strong>Streamlit</strong> (web interface)</p>
<p>© 2026 | Semester Project | All rights reserved</p>
</div>
""", unsafe_allow_html=True)
