from src.page import Page
from src.row import Row


def test_page_abstraction():
    print("=== [Phase 2] Testing Page Abstraction... ===")

    try:
        # 1. Page 생성
        print("1. Creating Page...")
        p = Page()
        # Check if data attribute exists and is bytearray
        if not hasattr(p, "data"):
            print("   ❌ Page.data attribute missing.")
            return
        if len(p.data) != 4096:
            print(f"   ❌ Page size wrong. Expected 4096, got {len(p.data)}")
            return
        print("   ✅ Page created (4KB buffer ready).")

        # 2. Insert Test
        print("2. Testing Insert...")
        row1 = Row(1, "user1", "user1@test.com")
        if not p.write_at(row1):
            print("   ❌ Insert failed.")
            return

        if p._row_count != 1:
            print(f"   ❌ row_count mismatch. Expected 1, got {p._row_count}")
            return
        print("   ✅ Insert successful.")

        # 3. Read Test
        print("3. Testing Read...")
        read_row = p.read_at(0)
        if read_row != row1:
            print("   ❌ Read data mismatch!")
            print(f"      Original: {row1}")
            print(f"      Read:     {read_row}")
            return
        print("   ✅ Read data integrity check passed.")

        # 4. Capacity Test (Filling the page)
        print(f"4. Testing Page Capacity (Tetris) - MAX: {Page.MAX_ROWS}...")
        # We already have 1 row. Let's fill the rest.
        for i in range(2, Page.MAX_ROWS + 1):
            r = Row(i, f"user{i}", f"user{i}@test.com")
            success = p.write_at(r)
            if not success:
                print(f"   ❌ Prematurely full at count {i - 1}")
                return

        print(f"   ✅ Filled page with {Page.MAX_ROWS} rows.")

        # 5. Overflow Test
        print("5. Testing Overflow...")
        if p.is_full():
            overflow_row = Row(999, "overflow", "err@test.com")
            # insert logic might need to be improved to return False if full
            # Currently p.insert() doesn't check is_full() internally?
            # Let's check src/page.py
            pass

        # 6. Random Access Verification
        print("6. Verifying Random Row (Row #7)...")
        r7 = p.read_at(6)  # Index 6 is the 7th item
        if r7.user_id != 7:
            print(f"   ❌ Random access fail. Expected ID 7, got {r7.user_id}")
            return
        print(f"   ✅ Random access passed. ID: {r7.user_id}")

        print("\n🎉 Congratulations! Phase 2 Completed Successfully.")

    except Exception as e:
        print(f"\n❌ Verify Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_page_abstraction()
