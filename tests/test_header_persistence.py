from src.page import Page
from src.row import Row
import struct


def test_page_header():
    print("=== [Phase 4.5] Testing Page Header (Metadata Persistence) ===")

    try:
        # 1. New Page Test
        print("1. Creating New Page...")
        p1 = Page()
        if p1.num_rows != 0:
            print(f"   ❌ Init fail. Expected 0 rows, got {p1.num_rows}")
            return

        # Check Header bytes (Should be 0x00000000)
        # Note: Depending on user logic, header might be updated lazily or eagerly.
        # But bytearray(4096) is all zeros anyway.
        print("   ✅ New Page created.")

        # 2. Insert & Header Write Test
        print("2. Inserting Row 1...")
        p1.insert(Row(1, "hdr_test", "hdr@test.com"))

        if p1.num_rows != 1:
            print(f"   ❌ num_rows not updated in memory.")
            return

        # Check raw bytes for Header Update
        # The first 4 bytes should be integer `1` (Big or Little endian)
        # We assume Little endian (<I) as per Row class standard
        # But user might implement arbitrary logic, so let's check basic persistence first.

        # 3. Serialization/Deserialization Test
        print("3. Simulating Disk Save/Load...")
        raw_bytes = p1.data  # This mocks writing to disk

        # Load back
        p2 = Page(raw_bytes)  # This mocks reading from disk

        if p2.num_rows != 1:
            print(f"   ❌ Header Persistence Failed!")
            print(f"      Original Page Rows: 1")
            print(f"      Loaded Page Rows:   {p2.num_rows}")
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
        # Header (4 bytes) should not be empty now if num_rows=1
        header_int = struct.unpack("<I", raw_bytes[0:4])[0]  # Try Little endian
        if header_int != 1:
            header_int_be = struct.unpack(">I", raw_bytes[0:4])[0]  # Try Big endian
            if header_int_be != 1:
                print(
                    f"   ❌ Header bytes look wrong. Expected 1, got raw: {raw_bytes[0:4].hex()}"
                )
                return
        print("   ✅ Binary Header is correct.")

        print("\n🎉 Congratulations! Page Metadata is now Persistent.")

    except Exception as e:
        print(f"\n❌ Verify Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_page_header()
