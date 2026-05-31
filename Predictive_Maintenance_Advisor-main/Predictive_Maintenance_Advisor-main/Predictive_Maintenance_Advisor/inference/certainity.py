"""
Certainty Factor (CF) Management Module

Implements Dempster-Shafer theory for combining multiple rules' certainty factors.
When multiple rules support the same diagnosis, their confidence values are combined
using: CF_combined = CF1 + CF2 * (1 - CF1)

This creates a more robust confidence metric that prevents overshooting to 1.0
while properly reflecting multiple sources of evidence.
"""

from typing import List, Tuple


class CertaintyFactorCalculator:
    """Calculate and combine certainty factors for multiple rules"""
    
    @staticmethod
    def combine_certainty_factors(cf_list: List[float]) -> float:
        """
        Combine multiple certainty factors using Dempster-Shafer formula.
        
        Formula: CF_combined = CF1 + CF2 * (1 - CF1)
        
        This prevents overshooting and properly weights multiple sources of evidence.
        Example:
          - CF1 = 0.7, CF2 = 0.8 → CF_combined = 0.7 + 0.8*(1-0.7) = 0.7 + 0.24 = 0.94
          - CF1 = 0.5, CF2 = 0.5 → CF_combined = 0.5 + 0.5*0.5 = 0.75
        
        Args:
            cf_list: List of certainty factors to combine (each 0.0-1.0)
        
        Returns:
            Combined certainty factor (0.0-1.0)
        """
        if not cf_list:
            return 0.0
        
        if len(cf_list) == 1:
            return cf_list[0]
        
        # Start with first CF
        combined_cf = cf_list[0]
        
        # Iteratively combine with remaining CFs
        for cf in cf_list[1:]:
            # Apply formula: CF_combined = CF1 + CF2 * (1 - CF1)
            combined_cf = combined_cf + cf * (1 - combined_cf)
        
        # Ensure result is in valid range [0.0, 1.0]
        return min(1.0, max(0.0, combined_cf))
    
    @staticmethod
    def weighted_certainty_factors(cf_weight_pairs: List[Tuple[float, float]]) -> float:
        """
        Combine certainty factors with weights (for giving priority to some rules).
        
        Each rule is weighted by importance; higher weight = higher influence.
        
        Args:
            cf_weight_pairs: List of (certainty_factor, weight) tuples
                            where weight is 0.0-1.0 (1.0 = max importance)
        
        Returns:
            Weighted combined certainty factor
        """
        if not cf_weight_pairs:
            return 0.0
        
        # Filter out zero-weight items
        valid_pairs = [(cf, w) for cf, w in cf_weight_pairs if w > 0.0]
        
        if not valid_pairs:
            return 0.0
        
        # Sort by weight descending (higher weight first)
        valid_pairs.sort(key=lambda x: x[1], reverse=True)
        
        # Apply Dempster-Shafer with weighting
        combined_cf = valid_pairs[0][0] * valid_pairs[0][1]
        
        for cf, weight in valid_pairs[1:]:
            weighted_cf = cf * weight
            combined_cf = combined_cf + weighted_cf * (1 - combined_cf)
        
        return min(1.0, max(0.0, combined_cf))
    
    @staticmethod
    def diminish_certainty(cf: float, diminish_factor: float = 0.8) -> float:
        """
        Reduce certainty factor when conditions are partially met (not all symptoms present).
        
        Used when a rule's primary condition is met but supporting conditions are weak.
        
        Args:
            cf: Original certainty factor
            diminish_factor: Multiplier (0.8 = reduce to 80% of original)
        
        Returns:
            Diminished certainty factor
        """
        return cf * diminish_factor
    
    @staticmethod
    def increase_certainty_with_age(cf: float, equipment_age_years: float) -> float:
        """
        Increase certainty factor for failure predictions based on equipment age.
        
        Older equipment is more likely to fail; use age as confidence modifier.
        
        Args:
            cf: Base certainty factor
            equipment_age_years: Age of equipment in years
        
        Returns:
            Age-adjusted certainty factor (higher for older equipment)
        """
        # Age multiplier: 0 years = 1.0x, 20 years = 2.0x (but capped at 1.0)
        age_multiplier = 1.0 + (min(equipment_age_years, 20.0) / 20.0)
        adjusted_cf = cf * age_multiplier
        return min(1.0, adjusted_cf)
    
    @staticmethod
    def consistency_check(cf: float, severity: int) -> Tuple[bool, str]:
        """
        Validate that CF and severity level are consistent.
        
        Rules:
        - Severity 5 (Critical) should have CF >= 0.85
        - Severity 3-4 (Warning) should have CF >= 0.70
        - Severity 1-2 (Monitor) should have CF >= 0.20
        - Severity 0 (OK) should have CF >= 0.95
        
        Args:
            cf: Certainty factor
            severity: Severity level (0-5)
        
        Returns:
            Tuple (is_consistent, explanation_message)
        """
        if severity == 5 and cf < 0.85:
            return False, f"Critical failure (severity 5) should have CF >= 0.85, got {cf}"
        elif severity in [3, 4] and cf < 0.70:
            return False, f"Warning (severity 3-4) should have CF >= 0.70, got {cf}"
        elif severity in [1, 2] and cf < 0.20:
            return False, f"Monitor (severity 1-2) should have CF >= 0.20, got {cf}"
        elif severity == 0 and cf < 0.95:
            return False, f"OK status (severity 0) should have CF >= 0.95, got {cf}"
        
        return True, "CF and severity are consistent"


# Singleton instance for easy access
cf_calculator = CertaintyFactorCalculator()


# ─────────────────────────────────────────────────────────────────────────────
# DIAGNOSTIC CONFIDENCE THRESHOLDS
# ─────────────────────────────────────────────────────────────────────────────

class ConfidenceThresholds:
    """Standard thresholds for interpreting certainty factors"""
    
    DEFINITE = 0.90            # >= 0.90: Definite diagnosis
    PROBABLE = 0.70            # 0.70-0.89: Probable diagnosis
    POSSIBLE = 0.50            # 0.50-0.69: Possible diagnosis
    MONITOR = 0.20             # 0.20-0.49: Monitor/watch
    UNLIKELY = 0.0             # < 0.20: Unlikely
    
    @staticmethod
    def confidence_label(cf: float) -> str:
        """Get human-readable confidence label for CF value"""
        if cf >= ConfidenceThresholds.DEFINITE:
            return "DEFINITE"
        elif cf >= ConfidenceThresholds.PROBABLE:
            return "PROBABLE"
        elif cf >= ConfidenceThresholds.POSSIBLE:
            return "POSSIBLE"
        elif cf >= ConfidenceThresholds.MONITOR:
            return "MONITOR"
        else:
            return "UNLIKELY"


# ─────────────────────────────────────────────────────────────────────────────
# EVIDENCE AGGREGATION FOR MULTI-SYMPTOM DIAGNOSIS
# ─────────────────────────────────────────────────────────────────────────────

class DiagnosticEvidence:
    """Track multiple pieces of evidence for a single diagnosis"""
    
    def __init__(self, diagnosis_name: str):
        self.diagnosis_name = diagnosis_name
        self.evidences: List[Tuple[str, float]] = []  # (rule_name, cf)
    
    def add_evidence(self, rule_name: str, cf: float):
        """Add evidence from a rule firing"""
        self.evidences.append((rule_name, cf))
    
    def get_combined_cf(self) -> float:
        """Calculate combined CF from all evidences"""
        cf_list = [cf for _, cf in self.evidences]
        return cf_calculator.combine_certainty_factors(cf_list)
    
    def get_evidence_summary(self) -> str:
        """Get human-readable summary of evidence"""
        if not self.evidences:
            return f"No evidence for {self.diagnosis_name}"
        
        summary = f"{self.diagnosis_name}:\n"
        for rule_name, cf in self.evidences:
            summary += f"  - {rule_name}: {cf*100:.0f}%\n"
        summary += f"  Combined confidence: {self.get_combined_cf()*100:.0f}%"
        return summary


if __name__ == "__main__":
    # Test CF combination
    print("Testing Certainty Factor Combination:")
    cf1, cf2, cf3 = 0.7, 0.8, 0.6
    combined = cf_calculator.combine_certainty_factors([cf1, cf2, cf3])
    print(f"CF({cf1}, {cf2}, {cf3}) = {combined:.3f}")
    
    # Test confidence labels
    print("\nConfidence Labels:")
    for cf in [0.95, 0.75, 0.55, 0.25, 0.1]:
        label = ConfidenceThresholds.confidence_label(cf)
        print(f"CF={cf:.2f} → {label}")
    
    # Test evidence tracking
    print("\nEvidence Aggregation:")
    evidence = DiagnosticEvidence("Bearing Failure")
    evidence.add_evidence("rule_bearing_vibration", 0.75)
    evidence.add_evidence("rule_bearing_temp", 0.65)
    print(evidence.get_evidence_summary())
