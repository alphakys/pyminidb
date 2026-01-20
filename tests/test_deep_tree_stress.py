"""
Deep Tree Stress Test

MAX_ROWS를 강제로 줄여서 트리 높이를 증가시키는 스트레스 테스트.
Cascading Split과 재귀 insert_into_parent를 집중 테스트.
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.btree import BTreeManager
from src.table import Table
from src.page import Page, PageType
from src.row import Row


class TestDeepTreeStress(unittest.TestCase):
    """깊은 트리 스트레스 테스트"""

    @classmethod
    def setUpClass(cls):
        """테스트 전 MAX_ROWS 축소"""
        # 원본 저장
        cls.original_max_rows = Page.MAX_ROWS

        # 강제로 작게 설정 (Split 빈번하게 발생)
        Page.MAX_ROWS = 5  # 매우 작게!
        print(f"\n⚠️  MAX_ROWS를 {cls.original_max_rows} → {Page.MAX_ROWS}로 축소")
        print(f"   (트리가 빠르게 깊어집니다!)\n")

    @classmethod
    def tearDownClass(cls):
        """테스트 후 복원"""
        Page.MAX_ROWS = cls.original_max_rows
        print(f"\n✅ MAX_ROWS 복원: {Page.MAX_ROWS}")

    def setUp(self):
        self.test_db = "test_deep_tree_stress.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        self.table = Table(self.test_db)
        self.btree = BTreeManager(self.table)

        # 초기 Root
        root = Page(page_type=PageType.LEAF)
        root._update_header()
        self.table.pager.write_page(0, root)

    def tearDown(self):
        self.table.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_very_deep_tree(self):
        """
        매우 깊은 트리 생성 테스트

        MAX_ROWS=5이므로 50개만 삽입해도 트리가 깊어짐
        """
        print("=" * 60)
        print("TEST: Very Deep Tree (MAX_ROWS=5)")
        print("=" * 60)

        num_rows = 50

        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"user{i}", f"user{i}@test.com")

            try:
                result = self.btree.insert(row)
                self.assertTrue(result, f"Insert {user_id} should succeed")
            except Exception as e:
                print(f"❌ INSERT FAILED at user_id={user_id}")
                print(f"   Error: {e}")
                raise

            # 매 10개마다 트리 상태 출력
            if (i + 1) % 10 == 0:
                page_count = self.table.pager.page_count
                root = self.table.pager.read_page(self.table.root_page_id)
                print(
                    f"  [{i + 1:2d} rows] Pages: {page_count:2d}, Root: {root.page_type.name}"
                )

        print(f"\n✅ Successfully inserted {num_rows} rows")

        # 최종 통계
        page_count = self.table.pager.page_count
        root = self.table.pager.read_page(self.table.root_page_id)

        print(f"\n📊 Final Statistics:")
        print(f"   Total Pages: {page_count}")
        print(f"   Root Type: {root.page_type.name}")
        print(f"   Root PID: {self.table.root_page_id}")

        if not root.is_leaf:
            keys, pids = root.read_internal_node()
            print(f"   Root Keys: {keys}")
            print(f"   Root Children: {len(pids)}")

        # 검증: 모든 키를 find_leaf로 찾을 수 있어야 함
        print(f"\n🔍 Verification: Testing find_leaf...")
        for i in range(0, num_rows, 5):  # 샘플링
            user_id = i * 10
            leaf_pid = self.table.find_leaf(user_id)
            self.assertIsNotNone(leaf_pid, f"find_leaf({user_id}) should work")
        print(f"✅ All sample keys found!")

    def test_cascading_split_depth(self):
        """
        Cascading Split 깊이 테스트

        의도적으로 Internal Split까지 유도
        """
        print("=" * 60)
        print("TEST: Cascading Split Depth")
        print("=" * 60)

        num_rows = 100  # MAX_ROWS=5이므로 충분히 깊어짐

        initial_root_pid = self.table.root_page_id

        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"user{i}", f"user{i}@test.com")
            self.btree.insert(row)

        final_root_pid = self.table.root_page_id

        print(f"\n📊 Root PID Changes:")
        print(f"   Initial Root: {initial_root_pid}")
        print(f"   Final Root: {final_root_pid}")

        if final_root_pid != initial_root_pid:
            print(f"✅ Root Split detected! (Height increased)")

        # 트리 높이 추정
        height = self._estimate_tree_height(self.table.root_page_id)
        print(f"\n🌳 Estimated Tree Height: {height}")
        print(f"   (Height > 2 means Internal Split occurred)")

        self.assertGreater(height, 1, "Tree should have height > 1")

    def _estimate_tree_height(self, pid: int, current_height: int = 1) -> int:
        """트리 높이 추정 (재귀)"""
        page = self.table.pager.read_page(pid)

        if page.is_leaf:
            return current_height

        # Internal이면 첫 번째 자식의 높이 + 1
        keys, pids = page.read_internal_node()
        if pids:
            return self._estimate_tree_height(pids[0], current_height + 1)

        return current_height

    def test_random_order_deep_tree(self):
        """
        랜덤 순서로 깊은 트리 생성

        순차 삽입이 아니라 랜덤 삽입으로도 작동하는지
        """
        print("=" * 60)
        print("TEST: Random Order Deep Tree")
        print("=" * 60)

        import random

        num_rows = 50
        user_ids = list(range(1, num_rows + 1))
        random.shuffle(user_ids)

        print(f"Inserting {num_rows} rows in random order...")
        print(f"First 10 order: {user_ids[:10]}")

        for user_id in user_ids:
            row = Row(user_id, f"user{user_id}", f"u{user_id}@test.com")
            result = self.btree.insert(row)
            self.assertTrue(result)

        print(f"✅ All {num_rows} rows inserted successfully")

        # 검증: 정렬된 순서로 검색 가능해야 함
        print(f"\n🔍 Verification: Sequential search...")
        for user_id in range(1, num_rows + 1, 5):
            leaf_pid = self.table.find_leaf(user_id)
            self.assertIsNotNone(leaf_pid)
        print(f"✅ All sequential keys found!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
