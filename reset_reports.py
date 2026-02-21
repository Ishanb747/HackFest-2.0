"""
reset_reports.py — Clean up old reports and force fresh data generation

Run this to delete all cached reports and start fresh.
"""

from pathlib import Path
import shutil

ROOT = Path(__file__).parent.resolve()

# Files to delete
files_to_delete = [
    ROOT / "rules" / "violation_report.json",
    ROOT / "rules" / "violation_report_live.json",
    ROOT / "rules" / "explanations.json",
]

# Directories to clean (optional)
dirs_to_clean = [
    ROOT / "__pycache__",
]

def reset_reports():
    """Delete all generated reports to force fresh generation."""
    print("🧹 Cleaning up old reports...")
    
    deleted_count = 0
    for file_path in files_to_delete:
        if file_path.exists():
            file_path.unlink()
            print(f"  ✅ Deleted: {file_path.name}")
            deleted_count += 1
        else:
            print(f"  ⏭️  Not found: {file_path.name}")
    
    # Clean pycache (optional)
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  ✅ Cleaned: {dir_path.name}/")
    
    print(f"\n✨ Done! Deleted {deleted_count} report file(s).")
    print("\n📌 Next steps:")
    print("   1. Run: streamlit run app.py")
    print("   2. Click '🚀 Run' in the sidebar")
    print("   3. New reports will be generated with accurate counts!")

if __name__ == "__main__":
    reset_reports()
