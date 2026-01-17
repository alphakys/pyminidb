"""
Step 4.2 검증: find_leaf 테스트

이 테스트는 수동으로 B+Tree 구조를 만들고,
find_leaf가 올바른 Leaf PID를 반환하는지 확인합니다.

구조:
           [Internal: PID=0]
           keys=[20, 40]
           pids=[1, 2, 3]
          /       |       \
    [Leaf:1]  [Leaf:2]  [Leaf:3]
     < 20     20~39      >= 40
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pager import Pager
from src.page import Page, PageType
from src.table import Table

TEST_DB = "test_find_leaf.db"


def setup_btree_structure():
    """수동으로 간단한 B+Tree 구조 생성"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    pager = Pager(TEST_DB)

    # Root (Internal) - PID 0
    root = Page(page_type=PageType.INTERNAL)
    root.write_internal_node(keys=[20, 40], pids=[1, 2, 3])
    pager.write_page(0, root)

    # Leaf 1 - PID 1 (keys < 20)
    leaf1 = Page(page_type=PageType.LEAF)
    leaf1.update_header()
    pager.write_page(1, leaf1)

    # Leaf 2 - PID 2 (20 <= keys < 40)
    leaf2 = Page(page_type=PageType.LEAF)
    leaf2.update_header()
    pager.write_page(2, leaf2)

    # Leaf 3 - PID 3 (keys >= 40)
    leaf3 = Page(page_type=PageType.LEAF)
    leaf3.update_header()
    pager.write_page(3, leaf3)

    pager.close()


def test_find_leaf():
    print("=" * 60)
    print("Step 4.2: find_leaf 테스트")
    print("=" * 60)

    setup_btree_structure()

    table = Table(TEST_DB)

    # Test Cases
    test_cases = [
        (5, 1),  # key=5 → Leaf 1 (< 20)
        (15, 1),  # key=15 → Leaf 1 (< 20)
        (20, 2),  # key=20 → Leaf 2 (20 <= x < 40)
        (35, 2),  # key=35 → Leaf 2 (20 <= x < 40)
        (40, 3),  # key=40 → Leaf 3 (>= 40)
        (100, 3),  # key=100 → Leaf 3 (>= 40)
    ]

    all_passed = True
    for key, expected_pid in test_cases:
        result = table.find_leaf(key)
        status = "✅" if result == expected_pid else "❌"
        print(f"find_leaf({key:3d}) → PID {result} (expected: {expected_pid}) {status}")
        if result != expected_pid:
            all_passed = False

    table.close()

    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 모든 테스트 통과!")
    else:
        print("❌ 일부 테스트 실패")
    print("=" * 60)


if __name__ == "__main__":
    test_find_leaf()
