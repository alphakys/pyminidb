import os
from src.pager import Pager
from src.page import Page
from src.row import Row

DB_FILE = "test_db.db"


def teardown():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)


def test_pager_persistence():
    print("=== [Phase 3] Testing Disk Persistence (Pager) ===")
    teardown()

    try:
        # 1. Pager Initialization
        print("1. Initializing Pager...")
        pager = Pager(DB_FILE)
        if not os.path.exists(DB_FILE):
            print("   ❌ Database file was not created.")
            return
        print("   ✅ DB file created.")

        # 2. Write Page Test
        print("2. Writing Page 0...")
        p0 = Page()
        row = Row(1, "persist_user", "persist@db.com")
        p0.insert(row)

        pager.write_page(0, p0)
        # Check file size (should be at least 4KB)
        file_size = os.path.getsize(DB_FILE)
        if file_size < 4096:
            print(f"   ❌ File size mismatch. Expected >= 4096, got {file_size}")
            return
        print("   ✅ Write successful (File size grew).")

        # 3. Read Page Test (Memory Persistence Check)
        print("3. Reading Page 0 back...")
        p0_read = pager.read_page(0)

        # Verify Row
        read_row = p0_read.read_at(0)
        if read_row.username != "persist_user":
            print(f"   ❌ Data mismatch! Got: {read_row}")
            return
        print("   ✅ Data integrity check passed.")

        # 4. Persistence Test (Close and Re-open)
        print("4. Testing Persistence after Close...")
        pager.close()

        # Open new pager instance
        pager2 = Pager(DB_FILE)
        p0_restored = pager2.read_page(0)
        restored_row = p0_restored.read_at(0)

        if restored_row.email != "persist@db.com":
            print("   ❌ Persistence failed! Data lost after close.")
            return
        print("   ✅ Persistence verified.")
        pager2.close()

        # 5. Random Access Test (Page 1)
        print("5. Testing Random Page Access (Page 1)...")
        pager3 = Pager(DB_FILE)
        p1 = Page()
        p1.insert(Row(99, "page1_user", "p1@db.com"))

        # Write to Page 1 (Offset 4096)
        pager3.write_page(1, p1)

        # Verify file size (should be 8192)
        if os.path.getsize(DB_FILE) < 8192:
            print(f"   ❌ File too small for 2 pages. Size: {os.path.getsize(DB_FILE)}")
            return

        # Read back Page 1
        p1_read = pager3.read_page(1)
        if p1_read.read_at(0).id != 99:
            print("   ❌ Random access read failed.")
            return
        print("   ✅ Random access passed.")
        pager3.close()

        print("\n🎉 Congratulations! Phase 3 Completed Successfully.")

    except Exception as e:
        print(f"\n❌ Verify Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        teardown()


if __name__ == "__main__":
    test_pager_persistence()
