from src.page import Page
from src.row import Row

def test_page_abstraction():
    print("=== [Phase 2] Testing Page Abstraction... ===")

    try:
        # 1. Page 생성
        print("1. Creating Page...")
        p = Page()
        # Check if data attribute exists and is bytearray
        if not hasattr(p, 'data'):
            print("   ❌ Page.data attribute missing.")
            return
        if len(p.data) != 4096:
            print(f"   ❌ Page size wrong. Expected 4096, got {len(p.data)}")
            return
        print("   ✅ Page created (4KB buffer ready).")

        # 2. Insert Test
        print("2. Testing Insert...")
        row1 = Row(1, "user1", "user1@test.com")
        if not p.insert(row1):
            print("   ❌ Insert failed.")
            return

        if p.num_rows != 1:
             print(f"   ❌ num_rows mismatch. Expected 1, got {p.num_rows}")
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
        print("4. Testing Page Capacity (Tetris)...")
        # We already have 1 row. Let's fill the rest.
        # Max rows = 14. We need to insert 13 more.
        for i in range(2, 15): # 2 to 14
            r = Row(i, f"user{i}", f"user{i}@test.com")
            success = p.insert(r)
            if not success:
                print(f"   ❌ Prematurely full at count {i-1}")
                return

        print("   ✅ Filled page with 14 rows.")

        # 5. Overflow Test
        print("5. Testing Overflow...")
        overflow_row = Row(999, "overflow", "err@test.com")
        if p.insert(overflow_row):
             print("   ❌ Page allowed inserting more than MAX_ROWS!")
             return
        print("   ✅ Correctly rejected overflow (Page Full).")

        # 6. Random Access Verification
        print("6. Verifying Random Row (Row #7)...")
        # Row #7 had id=7 (since we inserted id 1..14)
        r7 = p.read_at(6) # Index 6 is the 7th item
        if r7.id != 7:
            print(f"   ❌ Random access fail. Expected ID 7, got {r7.id}")
            return
        print(f"   ✅ Random access passed. ID: {r7.id}")

        print("\n🎉 Congratulations! Phase 2 Completed Successfully.")

    except Exception as e:
        print(f"\n❌ Verify Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_page_abstraction()
