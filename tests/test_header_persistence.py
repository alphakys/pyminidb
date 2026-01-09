from src.page import Page
from src.row import Row
import struct


def test_page_header():
    print("=== [Phase 4.5] Testing Page Header (Metadata Persistence) ===")

    try:
        # 1. New Page Test
        print("1. Creating New Page...")
        p1 = Page()
        if p1._row_count != 0:
            print(f"   ❌ Init fail. Expected 0 rows, got {p1._row_count}")
            return

        # Check Header bytes (Should be 0x00000000)
        # Note: Depending on user logic, header might be updated lazily or eagerly.
        # But bytearray(4096) is all zeros anyway.
        print("   ✅ New Page created.")

        # 2. Insert & Header Write Test
        print("2. Inserting Row 1...")
        p1.insert(Row(1, "hdr_test", "hdr@test.com"))

        if p1._row_count != 1:
            print(f"   ❌ row_count not updated in memory.")
            return

        # Check raw bytes for Header Update
        # The first 2 bytes (H) should be integer `1` as per Page.HEADER_FORMAT

        # 3. Serialization/Deserialization Test
        print("3. Simulating Disk Save/Load...")
        raw_bytes = p1.data  # This mocks writing to disk

        # Load back
        p2 = Page(raw_bytes)  # This mocks reading from disk

        if p2._row_count != 1:
            print(f"   ❌ Header Persistence Failed!")
            print(f"      Original Page Rows: 1")
            print(f"      Loaded Page Rows:   {p2._row_count}")
            print(
                "      Hint: Did you unpack the header in __init__? Did you update header in insert?"
            )
            return

        row_loaded = p2.read_at(0)
        if row_loaded.username != "hdr_test":
            print(
                f"   ❌ Row Data Corrupted. Offset calculation might be wrong (forgot to add HEADER_SIZE?)."
            )
            return

        print("   ✅ Header Persistence Passed (Rows restored: 1).")

        # 4. Offset Shift Check
        # If offset is wrong, Row data will overlap with Header or be shifted.
        print("4. Checking Binary Layout...")
        # Header starts with 2-byte count (<H)
        header_count = struct.unpack(Page.HEADER_FORMAT, raw_bytes[: Page.HEADER_SIZE])[
            0
        ]
        if header_count != 1:
            print(f"   ❌ Header bytes look wrong. Expected 1, got {header_count}")
            return
        print("   ✅ Binary Header is correct.")

        print("\n🎉 Congratulations! Page Metadata is now Persistent.")

    except Exception as e:
        print(f"\n❌ Verify Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_page_header()
