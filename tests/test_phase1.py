import struct
from src.row import Row

def test_row_serialization():
    print("=== [Phase 1] Grading Your Implementation... ===")

    try:
        # 1. Row 생성 테스트
        print("1. Testing Row creation...")
        row = Row(id=1, username="test_user", email="test@example.com")
        print("   ✅ Row created successfully.")

        # 2. Serialize 구현 여부 확인
        print("2. Testing serialize()...")
        packed_data = row.serialize()
        if packed_data is None:
            print("   ❌ serialize() returned None. Method not implemented?")
            return

        # 3. 데이터 사이즈 검증
        expected_size = 291
        if len(packed_data) != expected_size:
            print(f"   ❌ Size Mismatch! Expected {expected_size} bytes, got {len(packed_data)} bytes.")
            print("      Hint: Check your struct format string and column sizes.")
            return
        print(f"   ✅ Size is correct ({expected_size} bytes).")

        # 4. Deserialize 구현 여부 확인
        print("3. Testing deserialize()...")
        restored_row = Row.deserialize(packed_data)
        if restored_row is None:
            print("   ❌ deserialize() returned None. Method not implemented?")
            return

        # 5. 데이터 무결성 검증 (영어)
        if (row.id != restored_row.id or
            row.username != restored_row.username or
            row.email != restored_row.email):
            print("   ❌ Data Mismatch!")
            print(f"      Original: {row}")
            print(f"      Restored: {restored_row}")
            print("      Hint: Did you decode bytes to string and remove null padding (\\x00)?")
            return
        print("   ✅ Data Integrity (Basic) passed.")

        # 6. 한글(UTF-8) 지원 테스트
        print("4. Testing Korean (UTF-8) support...")
        kor_row = Row(id=99, username="홍길동", email="hong@chosun.kr")
        restored_kor = Row.deserialize(kor_row.serialize())

        if restored_kor.username != "홍길동":
             print(f"   ❌ Korean Text Failure. Got: '{restored_kor.username}'")
             print("      Hint: Ensure you are encoding/decoding with 'utf-8'.")
             return
        print("   ✅ Korean Support passed.")

        print("\n🎉 Congratulations! Phase 1 Completed Successfully.")

    except Exception as e:
        print(f"\n❌ Verify Error: An exception occurred during verification.")
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_row_serialization()
