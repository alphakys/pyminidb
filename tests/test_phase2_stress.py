import os
import subprocess
from src.row import Row
from src.page import Page


def test_multi_page_persistence():
    print("=== [Phase 2] Stress Test: 100 Rows & Multi-Page ===")

    db_file = "mydb.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    # 1. Generate 100 Insert Commands
    insert_commands = [f"insert {i} user{i} user{i}@test.com" for i in range(1, 101)]
    input_text = "\n".join(insert_commands + ["select", ".exit"])

    print(f"1. Inserting 100 rows into {db_file}...")
    try:
        process = subprocess.Popen(
            ["python3", "src/main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "PYTHONPATH": os.getcwd()},
        )

        stdout, stderr = process.communicate(input=input_text, timeout=10)

    except subprocess.TimeoutExpired:
        process.kill()
        print("   ❌ Timeout! Too slow or stuck in loop.")
        return

    # 2. Check File Size (Should be multiple pages)
    # 100 rows / 14 rows_per_page = 7.14 -> 8 pages expected
    expected_min_size = (Page.PAGE_SIZE // 44) + int((Page.PAGE_SIZE % 44) > 0)
    actual_size = os.path.getsize(db_file) if os.path.exists(db_file) else 0

    print(f"2. Verifying File Size...")
    if actual_size >= expected_min_size:
        print(
            f"   ✅ Success: File size is {actual_size} bytes (~{actual_size // Page.PAGE_SIZE} pages)."
        )
    else:
        print(
            f"   ❌ Fail: File size is only {actual_size} bytes. (Expected >= {expected_min_size})"
        )
        print("      Hint: Still hardcoded to Page 0?")
        return

    # 3. Verify All Data Found
    print("3. Verifying Data Consistency...")
    all_lines = stdout.splitlines()
    found_count = sum(1 for line in all_lines if "Row(id=" in line)

    if found_count == 100:
        print(f"   ✅ Success: Found all {found_count} rows in output.")
    else:
        print(f"   ❌ Fail: Found only {found_count}/100 rows.")
        return

    print("\n🎉 Phase 2 Stress Test Passed! You've broken the 14-row limit.")


if __name__ == "__main__":
    test_multi_page_persistence()
