import os
import subprocess
from socket import timeout
import time


def test_repl_e2e():
    print("=== [Phase 4] Testing REPL (End-to-End) ===")

    db_file = "mydb.db"
    if os.path.exists(db_file):
        os.remove(db_file)

    # Input commands flow
    input_text = "\n".join(
        [
            "insert 1 user1 user1@test.com",
            "insert 2 user2 user2@test.com",
            "select",
            ".exit",
        ]
    )

    print("1. Running REPL process...")
    try:
        # Run main.py as a subprocess
        process = subprocess.Popen(
            ["python3", "src/main.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, "PYTHONPATH": os.getcwd()},
        )

        stdout, stderr = process.communicate(input=input_text, timeout=3)
        print(f"   Process finished with exit code {process.returncode}")

    except subprocess.TimeoutExpired:
        process.kill()
        print("   ❌ Timeout! REPL didn't exit correctly.")
        return

    # Validation Code
    output_lines = stdout.splitlines()
    # Filter prompt lines
    content_lines = [
        line
        for line in output_lines
        if not line.strip().startswith("db >")
        and "PyMiniDB" not in line
        and "Bye" not in line
        and ".exit" not in line
    ]

    print("2. Verifying Output...")
    # Expected output: Rows printed by select
    # Since we implemented print format in Row.__repr__, we look for that.

    found_user1 = any("user1" in line for line in content_lines)
    found_user2 = any("user2" in line for line in content_lines)
    if found_user1 and found_user2:
        print("   ✅ Insert & Select worked (Found user1 and user2 in output).")
    else:
        print("   ❌ Output mismatch.")
        print("   Full Output:")
        print(stdout)
        return

    # Verify Persistence
    if os.path.exists(db_file) and os.path.getsize(db_file) >= 4105:
        print("   ✅ DB file created and written.")
    else:
        print("   ❌ Persistence check failed.")
        return

    print("\n🎉 Congratulations! Application Logic Completed Successfully.")


if __name__ == "__main__":
    test_repl_e2e()
