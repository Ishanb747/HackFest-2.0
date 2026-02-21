import json
import db
from tools import RuleStoreWriterTool

def test_versioning():
    writer = RuleStoreWriterTool()
    
    # Check if there are existing rules and how many
    existing = db.get_rules()
    print(f"Existing rules: {len(existing)}")
    
    # If no rules exist, we will first insert a dummy rule
    if not existing:
        print("Inserting dummy rule to seed DB...")
        dummy_rules = [
            {
                "id": "DUMMY_1",
                "rule_type": "threshold",
                "description": "Dummy desc",
                "condition_field": "Amount_Paid",
                "operator": ">",
                "threshold_value": 50,
                "sql_hint": ""
            }
        ]
        db.save_rules(dummy_rules)
        print("Seeded DB. Now let's try versioning by adding a new rule.")
    
    # Now simulate Phase 1 finding a NEW rule that isn't in DB yet
    new_rules_payload = [
        {
            "id": "NEW_VERSION_RULE",
            "rule_type": "threshold",
            "description": "Trigger versioning snapshot",
            "condition_field": "Amount_Paid",
            "operator": ">",
            "threshold_value": 99999,
            "sql_hint": "test"
        }
    ]
    
    res = writer._run(json.dumps(new_rules_payload), pdf_source="test_version_check.pdf")
    print("\nWriter result:")
    print(res)

if __name__ == "__main__":
    test_versioning()
