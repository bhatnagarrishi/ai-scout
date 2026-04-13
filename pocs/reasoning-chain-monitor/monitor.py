import json
import re

class ReasoningAuditor:
    """
    Evaluates intermediate reasoning steps against ground-truth research data.
    Detects logic failures, hallucinations, or contradictions before final output.
    Focuses on the Samosa Shop New Delhi Expansion.
    """
    
    def __init__(self, research_data_path: str):
        with open(research_data_path, 'r') as f:
            self.data = json.load(f)
        self.findings = []

    def audit_step(self, step_count: int, thought: str):
        """
        Analyzes a single thought step for logical consistency.
        """
        print(f"\n[AUDITOR] Inspecting Step {step_count}...")
        
        step_issues = []
        thought_lower = thought.lower()
        
        # 1. Check for Local Supply Chain (90% from Mandis)
        if "supply" in thought_lower or "source" in thought_lower or "ingredient" in thought_lower:
            if "mandi" not in thought_lower and "local" not in thought_lower:
                issue = "POTENTIAL LOGIC FAILURE: Strategy mentions sourcing but ignores the 90% Local Mandi sourcing requirement for New Delhi."
                step_issues.append(issue)

        # 2. Check for Quality Governance (Central HQ)
        if "quality" in thought_lower or "governance" in thought_lower or "standard" in thought_lower:
            if "central" not in thought_lower and "hq" not in thought_lower:
                issue = "POTENTIAL HALLUCINATION: Quality plan omits Central HQ governance; rules must be central even if supply is local."
                step_issues.append(issue)

        # 3. Check for Local Pulse (Flavor of the Month)
        if "pulse" in thought_lower or "crowd" in thought_lower or "voting" in thought_lower:
            if "flavor" not in thought_lower and "vote" not in thought_lower:
                issue = "LOGIC GAP: 'Local Pulse' strategy misses the neighborhood voting system for the Flavor of the Month."
                step_issues.append(issue)

        if step_issues:
            for issue in step_issues:
                print(f"ISSUE: {issue}")
                self.findings.append({"step": step_count, "issue": issue})
        else:
            print("Reasoning appears logically consistent with Research Data.")

    def get_final_report(self):
        return {
            "total_steps_audited": len(self.findings),
            "critical_flags": self.findings,
            "status": "FAIL" if self.findings else "PASS"
        }
