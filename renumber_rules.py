#!/usr/bin/env python3
"""Renumber all rules to ensure unique IDs."""

import json
from pathlib import Path

rules_file = Path("rules/policy_rules.json")
rules = json.loads(rules_file.read_text(encoding="utf-8"))

print(f"Original: {len(rules)} rules")

# Renumber all rules sequentially
for i, rule in enumerate(rules, start=1):
    old_id = rule.get("id", "")
    new_id = f"RULE_{i:03d}"
    rule["id"] = new_id
    print(f"  {old_id} -> {new_id}: {rule.get('description', '')[:60]}")

# Backup original
backup_file = rules_file.with_suffix(".json.backup")
backup_file.write_text(rules_file.read_text(encoding="utf-8"))
print(f"\nBackup saved to: {backup_file}")

# Write renumbered
rules_file.write_text(json.dumps(rules, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Renumbered rules saved to: {rules_file}")
