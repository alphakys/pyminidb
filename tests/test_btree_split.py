"""
Step 4.3 검증: BTreeManager Split 테스트 (unittest)

unittest 프레임워크를 사용한 단위 테스트
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.btree import BTreeManager
from src.table import Table
from src.page import Page, PageType
from src.row import Row


class TestBTreeSplitLeaf(unittest.TestCase):
    """split_leaf 메서드 테스트"""

    def setUp(self):
        """각 테스트 전 실행: DB 초기화"""
        self.test_db = "test_split_leaf.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        self.table = Table(self.test_db)
        self.btree = BTreeManager(self.table)

    def tearDown(self):
        """각 테스트 후 실행: DB 정리"""
        self.table.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_split_leaf_basic(self):
        """Leaf Split 기본 동작 검증"""
        # Import debug helper
        from tests.debug_page import print_page_rows

        # Leaf 생성 및 데이터 채우기
        leaf_pid = 0
        leaf = Page(page_type=PageType.LEAF)

        max_rows = min(4, Page.MAX_ROWS)
        for i in range(max_rows):
            user_id = (i + 1) * 10
            row = Row(user_id, f"user{i}", f"user{i}@test.com")
            leaf.write_at(row)

        self.table.pager.write_page(leaf_pid, leaf)

        # Split 전 상태 출력
        print("\n" + "=" * 60)
        print("BEFORE SPLIT")
        print("=" * 60)
        before_leaf = self.table.pager.read_page(leaf_pid)
        print_page_rows(before_leaf, "Original Leaf")

        # Split 수행
        new_pid, promote_key = self.btree.split_leaf(leaf_pid)

        # Split 후 상태 출력
        print("\n" + "=" * 60)
        print("AFTER SPLIT")
        print("=" * 60)
        left_leaf = self.table.pager.read_page(leaf_pid)
        right_leaf = self.table.pager.read_page(new_pid)

        print_page_rows(left_leaf, "Left Leaf (Old)")
        print_page_rows(right_leaf, "Right Leaf (New)")

        # 기본 검증
        expected_left = max_rows // 2
        expected_right = max_rows - expected_left

        self.assertEqual(
            left_leaf.row_count, expected_left, "Left leaf should have half the rows"
        )
        self.assertEqual(
            right_leaf.row_count,
            expected_right,
            "Right leaf should have remaining rows",
        )

        # Promote Key 검증
        first_right_row = right_leaf.read_at(0)
        self.assertEqual(
            promote_key,
            first_right_row.user_id,
            "Promote key should be first key of right leaf",
        )

        # 🔍 추가 검증: Garbage 데이터 확인
        print("\n" + "=" * 60)
        print("GARBAGE CHECK")
        print("=" * 60)

        # Left Leaf에서 이동한 Row들이 정말 지워졌는지 확인
        for i in range(expected_left, max_rows):
            offset = Page.HEADER_SIZE + (i * Page.ROW_SIZE)
            end = offset + Page.ROW_SIZE
            data_slice = bytes(left_leaf.data[offset:end])

            is_clean = data_slice == b"\x00" * Page.ROW_SIZE

            if not is_clean:
                print(f"⚠️  WARNING: Left leaf position {i} has garbage data!")
                try:
                    garbage_row = Row.deserialize(data_slice)
                    print(f"   Contains: user_id={garbage_row.user_id}")
                except:
                    print(f"   Contains: corrupted bytes")
            else:
                print(f"✅ Position {i}: Clean (all zeros)")

        print("=" * 60)


class TestBTreeSplitInternal(unittest.TestCase):
    """split_internal 메서드 테스트"""

    def setUp(self):
        self.test_db = "test_split_internal.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        self.table = Table(self.test_db)
        self.btree = BTreeManager(self.table)

    def tearDown(self):
        self.table.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_split_internal_basic(self):
        """Internal Split 기본 동작 검증"""
        # Internal Node 생성
        internal_pid = 0
        internal = Page(page_type=PageType.INTERNAL)

        keys = [10, 20, 30, 40]
        pids = [1, 2, 3, 4, 5]

        internal.write_internal_node(keys, pids)
        self.table.pager.write_page(internal_pid, internal)

        # Split 수행
        new_pid, promote_key = self.btree.split_internal(internal_pid)

        # 검증
        left_node = self.table.pager.read_page(internal_pid)
        right_node = self.table.pager.read_page(new_pid)

        left_keys, left_pids = left_node.read_internal_node()
        right_keys, right_pids = right_node.read_internal_node()

        # mid=2이므로 promote=30, left=[10,20], right=[40]
        self.assertEqual(promote_key, 30, "Middle key should be promoted")
        self.assertEqual(left_keys, [10, 20], "Left should have first half keys")
        self.assertEqual(right_keys, [40], "Right should have second half keys")
        self.assertEqual(len(left_pids), len(left_keys) + 1, "Left PIDs should be N+1")
        self.assertEqual(
            len(right_pids), len(right_keys) + 1, "Right PIDs should be N+1"
        )


class TestBTreeInsert(unittest.TestCase):
    """insert 메서드 통합 테스트"""

    def setUp(self):
        self.test_db = "test_insert.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        self.table = Table(self.test_db)
        self.btree = BTreeManager(self.table)

        # 초기 Root Leaf 생성
        root = Page(page_type=PageType.LEAF)
        self.table.pager.write_page(0, root)

    def tearDown(self):
        self.table.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_insert_to_empty_leaf(self):
        """빈 Leaf에 Row 삽입"""
        row = Row(10, "alice", "alice@test.com")
        result = self.btree.insert(row)

        self.assertTrue(result, "Insert should succeed")

        # 검증
        root_leaf = self.table.pager.read_page(self.table.root_page_id)
        self.assertGreater(root_leaf.row_count, 0, "Leaf should have at least one row")

    def test_insert_multiple_rows(self):
        """여러 Row 삽입"""
        test_rows = [
            Row(10, "alice", "alice@test.com"),
            Row(20, "bob", "bob@test.com"),
            Row(30, "charlie", "charlie@test.com"),
        ]

        for row in test_rows:
            result = self.btree.insert(row)
            self.assertTrue(result, f"Insert of user_id={row.user_id} should succeed")

        # 검증
        root_leaf = self.table.pager.read_page(self.table.root_page_id)
        self.assertEqual(
            root_leaf.row_count, len(test_rows), "Leaf should contain all inserted rows"
        )


if __name__ == "__main__":
    # 상세 출력 모드로 실행
    unittest.main(verbosity=2)
