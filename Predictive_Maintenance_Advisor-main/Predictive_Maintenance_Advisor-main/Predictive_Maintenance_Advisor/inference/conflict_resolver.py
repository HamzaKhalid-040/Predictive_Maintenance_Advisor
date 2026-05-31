"""
Conflict Resolution Module

When multiple expert rules fire and produce conflicting diagnoses,
this module determines which diagnosis is most reliable by applying:
1. Severity level (higher severity = higher priority)
2. Certainty factor (higher confidence = higher priority)
3. Evidence count (more rules supporting diagnosis = more reliable)
4. Recency of symptoms (acute problems may override chronic issues)

Used by the inference engine to select the top diagnosis.
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class DiagnosisConclusion:
    """A single diagnosis produced by expert rules"""
    diagnosis_name: str
    certainty_factor: float        # 0.0 to 1.0
    severity_level: int            # 0 (OK) to 5 (Critical)
    rules_fired: List[str]         # Which rules produced this diagnosis
    evidence_strength: float       # Number of supporting rules / evidence count
    recommended_action: str        # What to do about this diagnosis
    
    def __lt__(self, other):
        """
        Define ordering for conflict resolution.
        Higher severity and certainty = "greater than" (higher priority)
        """
        # Primary sort: severity descending
        if self.severity_level != other.severity_level:
            return self.severity_level < other.severity_level
        
        # Secondary sort: certainty descending
        if abs(self.certainty_factor - other.certainty_factor) > 0.01:
            return self.certainty_factor < other.certainty_factor
        
        # Tertiary sort: evidence count descending
        return len(self.rules_fired) < len(other.rules_fired)
    
    def priority_score(self) -> float:
        """
        Calculate a single priority score for easier sorting.
        Range: 0.0 to 10.0
        
        Formula: (severity * 2) + (CF * 5) + (num_rules * 0.5)
        """
        severity_score = self.severity_level * 2.0  # 0-10
        cf_score = self.certainty_factor * 5.0      # 0-5
        evidence_score = min(len(self.rules_fired) * 0.5, 2.0)  # 0-2 (cap at 5 rules)
        
        return severity_score + cf_score + evidence_score


class ConflictResolver:
    """Resolve conflicts between multiple diagnoses"""
    
    def __init__(self):
        self.diagnoses: Dict[str, DiagnosisConclusion] = {}
        self.resolution_log: List[str] = []
    
    def add_diagnosis(self, diagnosis: DiagnosisConclusion):
        """
        Add a diagnosis conclusion.
        If same diagnosis already exists, merge the evidence.
        """
        if diagnosis.diagnosis_name in self.diagnoses:
            # Merge with existing diagnosis
            existing = self.diagnoses[diagnosis.diagnosis_name]
            existing.rules_fired.extend(diagnosis.rules_fired)
            existing.evidence_strength += 1
            
            # Update CF to reflect combined evidence
            # Take the higher of the two CFs (more conservative)
            if diagnosis.certainty_factor > existing.certainty_factor:
                existing.certainty_factor = diagnosis.certainty_factor
                existing.severity_level = max(existing.severity_level, diagnosis.severity_level)
        else:
            # New diagnosis
            self.diagnoses[diagnosis.diagnosis_name] = diagnosis
    
    def resolve(self) -> DiagnosisConclusion:
        """
        Resolve conflicts and return the single best diagnosis.
        
        Sorting criteria (in order):
        1. Highest severity level
        2. Highest certainty factor
        3. Most supporting rules
        
        Returns:
            The top-priority DiagnosisConclusion
        """
        if not self.diagnoses:
            # Return default "all normal" diagnosis
            return DiagnosisConclusion(
                diagnosis_name="Equipment Operating Normally",
                certainty_factor=1.0,
                severity_level=0,
                rules_fired=["default_no_fault"],
                evidence_strength=1.0,
                recommended_action="Continue routine maintenance schedule"
            )
        
        # Sort by priority (severity, then CF, then evidence)
        sorted_diagnoses = sorted(
            self.diagnoses.values(),
            key=lambda d: (d.severity_level, d.certainty_factor, len(d.rules_fired)),
            reverse=True
        )
        
        top_diagnosis = sorted_diagnoses[0]
        
        # Log resolution process if there was conflict
        if len(sorted_diagnoses) > 1:
            self._log_conflict_resolution(sorted_diagnoses)
        
        return top_diagnosis
    
    def resolve_top_n(self, n: int = 3) -> List[DiagnosisConclusion]:
        """
        Return top N diagnoses ranked by priority.
        Useful for showing alternative possibilities to user.
        
        Args:
            n: Number of diagnoses to return
        
        Returns:
            List of top N DiagnosisConclusions
        """
        sorted_diagnoses = sorted(
            self.diagnoses.values(),
            key=lambda d: (d.severity_level, d.certainty_factor, len(d.rules_fired)),
            reverse=True
        )
        return sorted_diagnoses[:n]
    
    def _log_conflict_resolution(self, sorted_diagnoses: List[DiagnosisConclusion]):
        """Log the conflict resolution process for debugging"""
        self.resolution_log.append("\n=== Conflict Resolution ===")
        self.resolution_log.append(f"Competing diagnoses: {len(sorted_diagnoses)}")
        
        for i, diagnosis in enumerate(sorted_diagnoses[:3], 1):
            score = diagnosis.priority_score()
            self.resolution_log.append(
                f"{i}. {diagnosis.diagnosis_name} "
                f"(Severity={diagnosis.severity_level}, CF={diagnosis.certainty_factor:.2f}, Score={score:.1f})"
            )
        
        self.resolution_log.append(
            f"Winner: {sorted_diagnoses[0].diagnosis_name}"
        )
    
    def get_resolution_log(self) -> str:
        """Get human-readable log of conflict resolution"""
        return "\n".join(self.resolution_log)
    
    def clear(self):
        """Clear all diagnoses and logs (for new session)"""
        self.diagnoses.clear()
        self.resolution_log.clear()


# ─────────────────────────────────────────────────────────────────────────────
# CONFLICT DETECTION UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

class ConflictDetector:
    """Identify and categorize conflicts between diagnoses"""
    
    @staticmethod
    def detect_contradictions(diagnoses: List[DiagnosisConclusion]) -> List[Tuple[str, str]]:
        """
        Detect logically contradictory diagnoses.
        
        Examples of contradictions:
        - "Equipment normal" vs "Compressor burnout"
        - "Refrigerant undercharge" vs "Refrigerant overcharge"
        
        Args:
            diagnoses: List of DiagnosisConclusions
        
        Returns:
            List of (diagnosis1, diagnosis2) pairs that contradict
        """
        contradictory_pairs = {
            ("Equipment Operating Normally", "Compressor Burnout"),
            ("Equipment Operating Normally", "Bearing Failure - Critical"),
            ("Refrigerant Undercharge", "Refrigerant Overcharge"),
            ("Condenser Fouling", "High Discharge Pressure Only"),
            ("Evaporator Freeze - Minor", "Refrigerant Leak"),
        }
        
        diagnosis_names = {d.diagnosis_name for d in diagnoses}
        conflicts = []
        
        for pair in contradictory_pairs:
            if pair[0] in diagnosis_names and pair[1] in diagnosis_names:
                conflicts.append(pair)
        
        return conflicts
    
    @staticmethod
    def severity_inversion_warning(diagnoses: List[DiagnosisConclusion]) -> List[str]:
        """
        Warn if lower severity diagnosis has higher certainty than higher severity.
        This may indicate measurement error or rule miscalibration.
        
        Args:
            diagnoses: List of DiagnosisConclusions
        
        Returns:
            List of warning messages
        """
        warnings = []
        
        sorted_by_severity = sorted(diagnoses, key=lambda d: d.severity_level, reverse=True)
        
        for i in range(len(sorted_by_severity) - 1):
            high_sev = sorted_by_severity[i]
            low_sev = sorted_by_severity[i+1]
            
            if high_sev.certainty_factor < low_sev.certainty_factor:
                warnings.append(
                    f"⚠ Severity inversion: '{low_sev.diagnosis_name}' "
                    f"(severity {low_sev.severity_level}, CF={low_sev.certainty_factor:.2f}) "
                    f"has higher confidence than '{high_sev.diagnosis_name}' "
                    f"(severity {high_sev.severity_level}, CF={high_sev.certainty_factor:.2f})"
                )
        
        return warnings


# ─────────────────────────────────────────────────────────────────────────────
# EXAMPLE USAGE
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Create test diagnoses with conflict
    diag1 = DiagnosisConclusion(
        diagnosis_name="Bearing Failure - Critical",
        certainty_factor=0.92,
        severity_level=5,
        rules_fired=["rule_bearing_grinding", "rule_bearing_vibration", "rule_bearing_temp"],
        evidence_strength=3.0,
        recommended_action="Emergency shutdown and bearing replacement"
    )
    
    diag2 = DiagnosisConclusion(
        diagnosis_name="High Discharge Temperature",
        certainty_factor=0.75,
        severity_level=3,
        rules_fired=["rule_discharge_temp", "rule_running_continuously"],
        evidence_strength=2.0,
        recommended_action="Check condenser fouling, verify charge"
    )
    
    diag3 = DiagnosisConclusion(
        diagnosis_name="Refrigerant Overcharge",
        certainty_factor=0.68,
        severity_level=3,
        rules_fired=["rule_high_pressure"],
        evidence_strength=1.0,
        recommended_action="Recover refrigerant and recharge to nameplate"
    )
    
    # Resolve conflict
    resolver = ConflictResolver()
    resolver.add_diagnosis(diag1)
    resolver.add_diagnosis(diag2)
    resolver.add_diagnosis(diag3)
    
    top_diagnosis = resolver.resolve()
    print(f"Top diagnosis: {top_diagnosis.diagnosis_name}")
    print(f"Severity: {top_diagnosis.severity_level}")
    print(f"Certainty: {top_diagnosis.certainty_factor:.2%}")
    print(f"Action: {top_diagnosis.recommended_action}")
    
    # Show all top 3
    print("\nTop 3 diagnoses:")
    for d in resolver.resolve_top_n(3):
        print(f"  - {d.diagnosis_name} (Severity {d.severity_level}, CF {d.certainty_factor:.2%})")
