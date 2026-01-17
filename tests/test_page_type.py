"""
Step 4.1.1 검증: PageType 구분 테스트
"""

import sys

sys.path.insert(0, "/Users/alpha/.gemini/antigravity/scratch/pyminidb")

from src.page import Page, PageType
from src.row import Row


def test_page_type():
    print("=" * 60)
    print("Step 4.1.1: PageType 검증")
    print("=" * 60)

    # Test 1: Leaf Page 생성
    print("\n[Test 1] Leaf Page 생성")
    leaf_page = Page(page_type=PageType.LEAF)
    assert leaf_page.is_leaf == True
    assert leaf_page.page_type == PageType.LEAF
    print(f"✅ Leaf Page: is_leaf={leaf_page.is_leaf}, page_type={leaf_page.page_type}")

    # Test 2: Internal Page 생성
    print("\n[Test 2] Internal Page 생성")
    internal_page = Page(page_type=PageType.INTERNAL)
    assert internal_page.is_leaf == False
    assert internal_page.page_type == PageType.INTERNAL
    print(
        f"✅ Internal Page: is_leaf={internal_page.is_leaf}, page_type={internal_page.page_type}"
    )

    # Test 3: Leaf Page에 Row 저장 후 직렬화/역직렬화
    print("\n[Test 3] Leaf Page 직렬화/역직렬화")
    leaf_page.write_at(Row(1, "Alice", "alice@test.com"))
    leaf_page.write_at(Row(2, "Bob", "bob@test.com"))

    # 직렬화
    serialized = bytes(leaf_page.data)

    # 역직렬화
    restored_page = Page(raw_data=serialized)
    assert restored_page.is_leaf == True
    assert restored_page.row_count == 2
    assert restored_page.page_type == PageType.LEAF

    # Row 복원 확인
    row1 = restored_page.read_at(0)
    row2 = restored_page.read_at(1)
    assert row1.user_id == 1 and row1.username == "Alice"
    assert row2.user_id == 2 and row2.username == "Bob"
    print(
        f"✅ 직렬화 후 복원: row_count={restored_page.row_count}, is_leaf={restored_page.is_leaf}"
    )
    print(f"   Row 1: user_id={row1.user_id}, username={row1.username}")
    print(f"   Row 2: user_id={row2.user_id}, username={row2.username}")

    # Test 4: Internal Page 직렬화/역직렬화
    print("\n[Test 4] Internal Page 직렬화/역직렬화")
    internal_page._row_count = 3  # keys 3개 있다고 가정
    internal_page.update_header()

    serialized_internal = bytes(internal_page.data)
    restored_internal = Page(raw_data=serialized_internal)
    assert restored_internal.is_leaf == False
    assert restored_internal.page_type == PageType.INTERNAL
    assert restored_internal.row_count == 3
    print(
        f"✅ Internal 복원: row_count={restored_internal.row_count}, is_leaf={restored_internal.is_leaf}"
    )

    print("\n" + "=" * 60)
    print("🎉 모든 테스트 통과!")
    print("=" * 60)


if __name__ == "__main__":
    test_page_type()
