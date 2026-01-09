import os
import subprocess
from src.page import Page


def run_db_command(commands):
    input_text = "\n".join(commands + [".exit"])
    process = subprocess.Popen(
        ["python3", "src/main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONPATH": os.getcwd()},
    )
    stdout, _ = process.communicate(input=input_text, timeout=10)
    return stdout


def test_strict_persistence():
    print("=== [Phase 2] Strict Persistence Stress Test ===")
    db_file = "mydb.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    # 1. 분할 삽입 (데이터를 넣고 DB를 완전히 종료)
    print("1. Inserting 100 rows and CLOSING the DB...")
    insert_cmds = [f"insert {i} user{i} user{i}@test.com" for i in range(1, 101)]
    run_db_command(insert_cmds)

    # 2. 새로운 세션에서 조회 (이때가 진짜 실력!)
    print("2. Re-opening DB in a NEW session and verifying...")
    output = run_db_command(["select"])

    all_lines = output.splitlines()
    row_count = sum(1 for line in all_lines if "Row(id=" in line)

    if row_count == 100:
        print(f"   ✅ Success: Recovered all {row_count} rows across sessions!")
    else:
        print(f"   ❌ Fail: Only recovered {row_count}/100 rows.")
        # Check for error messages
        if "struct.error" in output:
            print("   ⚠️ Found struct.error in output - Data clipping detected!")


if __name__ == "__main__":
    test_strict_persistence()
