"""
Step 4.1.2b 검증: Page와 BTreeNode 통합 테스트
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.page import Page, PageType
from src.row import Row


def test_page_node_integration():
    print("=" * 60)
    print("Step 4.1.2b: Page-Node 통합 검증")
    print("=" * 60)

    # Test 1: Internal Page 쓰기 및 읽기
    print("\n[Test 1] Internal Page Write -> Read")

    internal_page = Page(page_type=PageType.INTERNAL)
    keys = [100, 200, 300]
    pids = [10, 20, 30, 40]

    print(f"Writing keys: {keys}")
    print(f"Writing pids: {pids}")

    internal_page.write_internal_node(keys, pids)

    # row_count 헤더가 key 개수로 잘 설정되었는지 확인
    assert internal_page.row_count == 3
    print(f"✅ Header update 확인: row_count={internal_page.row_count}")

    # Disk I/O 시뮬레이션: bytes로 변환 후 새 페이지 생성
    raw_data = bytes(internal_page.data)
    loaded_page = Page(raw_data=raw_data)

    # 타입 확인
    assert loaded_page.is_leaf == False
    assert loaded_page.page_type == PageType.INTERNAL

    # 데이터 복원
    restored_keys, restored_pids = loaded_page.read_internal_node()

    assert restored_keys == keys
    assert restored_pids == pids

    print(f"Read keys: {restored_keys}")
    print(f"Read pids: {restored_pids}")
    print("✅ Internal Page 복원 성공!")

    # Test 2: Leaf Page에서의 오용 방지
    print("\n[Test 2] Leaf Page 오용 방지")
    leaf_page = Page(page_type=PageType.LEAF)

    try:
        leaf_page.write_internal_node(keys, pids)
        print("❌ 실패: Leaf Page에 Internal Write가 허용됨")
        exit(1)
    except TypeError as e:
        print(f"✅ 성공: 올바른 에러 발생 ({e})")

    try:
        leaf_page.read_internal_node()
        print("❌ 실패: Leaf Page에서 Internal Read가 허용됨")
        exit(1)
    except TypeError as e:
        print(f"✅ 성공: 올바른 에러 발생 ({e})")

    print("\n" + "=" * 60)
    print("🎉 모든 통합 테스트 통과!")
    print("=" * 60)


if __name__ == "__main__":
    test_page_node_integration()
