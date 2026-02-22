#!/usr/bin/env python3
"""Remove duplicate rule IDs, keeping the last occurrence of each."""

import json
from pathlib import Path

rules_file = Path("rules/policy_rules.json")
rules = json.loads(rules_file.read_text(encoding="utf-8"))

print(f"Original: {len(rules)} rules")

# Keep last occurrence of each ID
seen = {}
for rule in rules:
    rule_id = rule.get("id", "")
    seen[rule_id] = rule

deduplicated = list(seen.values())
print(f"After deduplication: {len(deduplicated)} rules")
print(f"Removed: {len(rules) - len(deduplicated)} duplicate rules")

# Backup original
backup_file = rules_file.with_suffix(".json.backup")
backup_file.write_text(rules_file.read_text(encoding="utf-8"))
print(f"Backup saved to: {backup_file}")

# Write deduplicated
rules_file.write_text(json.dumps(deduplicated, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Deduplicated rules saved to: {rules_file}")
