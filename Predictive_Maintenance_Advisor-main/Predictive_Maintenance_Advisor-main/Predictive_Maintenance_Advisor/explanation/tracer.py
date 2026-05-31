"""
Execution Tracer for Expert System

Logs:
- Rule firing events
- Conclusions generated
- Evidence aggregation
- Conflict resolution decisions

Provides complete transparency and auditability for diagnoses.
"""

from typing import List, Dict
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ExecutionEvent:
    """A single event in expert system execution"""
    event_type: str  # 'rule_fired', 'conclusion', 'conflict_resolved'
    rule_name: str
    conclusion: str
    certainty_factor: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class Tracer:
    """Track and explain expert system execution"""
    
    def __init__(self):
        self.log_entries: List[ExecutionEvent] = []
        self.conclusions: Dict[str, float] = {}
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Mark start of inference"""
        self.start_time = datetime.now()
        self.log_entries.clear()
        self.conclusions.clear()
    
    def end(self):
        """Mark end of inference"""
        self.end_time = datetime.now()
    
    def log(self, rule_name: str, conclusion: str, cf: float):
        """Log a rule firing"""
        event = ExecutionEvent(
            event_type='rule_fired',
            rule_name=rule_name,
            conclusion=conclusion,
            certainty_factor=cf
        )
        self.log_entries.append(event)
        
        # Track conclusions
        if conclusion not in self.conclusions:
            self.conclusions[conclusion] = cf
        else:
            # Combine CFs using Dempster-Shafer
            old_cf = self.conclusions[conclusion]
            combined = old_cf + cf * (1 - old_cf)
            self.conclusions[conclusion] = min(1.0, combined)
    
    def get_explanation(self) -> str:
        """Get human-readable explanation of reasoning"""
        if not self.log_entries:
            return "No rules fired. Equipment appears to be operating normally."
        
        explanation = "=== EXPERT SYSTEM REASONING TRACE ===\n\n"
        
        # List all fired rules
        explanation += "Rules Fired:\n"
        for entry in self.log_entries:
            explanation += f"• {entry.rule_name}\n"
            explanation += f"  → Conclusion: {entry.conclusion}\n"
            explanation += f"  → Confidence: {entry.certainty_factor*100:.0f}%\n\n"
        
        # Show conclusion aggregation
        explanation += "\nConclusion Aggregation:\n"
        for conclusion, cf in sorted(self.conclusions.items(), key=lambda x: x[1], reverse=True):
            explanation += f"• {conclusion}: {cf*100:.0f}%\n"
        
        # Show execution time
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            explanation += f"\nExecution Time: {duration*1000:.0f}ms\n"
        
        return explanation
    
    def get_rule_graph(self):
        """Generate rule dependency graph (for future visualization)"""
        # Placeholder for NetworkX graph generation
        return f"Graph with {len(self.log_entries)} rules"
    
    def clear(self):
        """Clear all entries"""
        self.log_entries.clear()
        self.conclusions.clear()
        self.start_time = None
        self.end_time = None


# Alias for compatibility
ExecutionTracer = Tracer


if __name__ == "__main__":
    # Example usage
    tracer = Tracer()
    tracer.start()
    
    # Simulate rule firings
    tracer.log("rule_high_discharge_temp", "High Discharge Temperature - Warning", 0.76)
    tracer.log("rule_high_pressure", "High Discharge Pressure", 0.72)
    
    tracer.end()
    
    print(tracer.get_explanation())
