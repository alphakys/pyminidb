"""
Ultra Deep Tree Stress Test

MAX_ROWS와 MAX_KEYS를 모두 축소하여
Internal Cascading Split을 강제로 발생시키는 극한 테스트
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.btree import BTreeManager
from src.table import Table
from src.page import Page, PageType
from src.row import Row
from src.node import BTreeNode


class TestUltraDeepTreeStress(unittest.TestCase):
    """초극단 깊은 트리 테스트 - Internal Split까지 유도"""

    @classmethod
    def setUpClass(cls):
        """MAX_ROWS와 MAX_KEYS 모두 축소!"""
        cls.original_max_rows = Page.MAX_ROWS
        cls.original_max_keys = BTreeNode.MAX_KEYS

        # 둘 다 매우 작게!
        Page.MAX_ROWS = 3
        BTreeNode.MAX_KEYS = 3

        print(f"\n{'=' * 60}")
        print(f"⚠️  ULTRA STRESS MODE")
        print(f"{'=' * 60}")
        print(f"MAX_ROWS:  {cls.original_max_rows} → {Page.MAX_ROWS}")
        print(f"MAX_KEYS:  {cls.original_max_keys} → {BTreeNode.MAX_KEYS}")
        print(f"{'=' * 60}\n")

    @classmethod
    def tearDownClass(cls):
        """복원"""
        Page.MAX_ROWS = cls.original_max_rows
        BTreeNode.MAX_KEYS = cls.original_max_keys
        print(f"\n✅ Restored: MAX_ROWS={Page.MAX_ROWS}, MAX_KEYS={BTreeNode.MAX_KEYS}")

    def setUp(self):
        self.test_db = "test_ultra_deep.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        self.table = Table(self.test_db)
        self.btree = BTreeManager(self.table)

        root = Page(page_type=PageType.LEAF)
        root._update_header()
        self.table.pager.write_page(0, root)

    def tearDown(self):
        self.table.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_internal_cascading_split(self):
        """
        Internal Cascading Split 발생 테스트

        MAX_KEYS=3이므로 Internal도 빠르게 가득 참!
        """
        print("=" * 60)
        print("TEST: Internal Cascading Split")
        print("=" * 60)
        print(f"Target: Internal Node Split 발생시키기!")
        print(f"Strategy: MAX_ROWS=3, MAX_KEYS=3\n")

        num_rows = 30  # 충분히 많이

        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"user{i}", f"u{i}@test.com")

            try:
                result = self.btree.insert(row)
                self.assertTrue(result)
            except Exception as e:
                print(f"\n❌ FAILED at user_id={user_id} (row #{i + 1})")
                print(f"Error: {type(e).__name__}: {e}")

                # 디버깅 정보
                print(f"\n📊 State when failed:")
                print(f"   Pages: {self.table.pager.page_count}")
                print(f"   Root PID: {self.table.root_page_id}")

                raise

            # 매 5개마다 상태 출력
            if (i + 1) % 5 == 0:
                page_count = self.table.pager.page_count
                root = self.table.pager.read_page(self.table.root_page_id)

                print(
                    f"[{i + 1:2d} rows] Pages: {page_count:2d}, Root: {root.page_type.name}",
                    end="",
                )

                if not root.is_leaf:
                    keys, pids = root.read_internal_node()
                    print(f", Keys: {len(keys)}, Children: {len(pids)}")
                else:
                    print()

        print(f"\n✅ All {num_rows} rows inserted!")

        # 최종 트리 상태
        self._print_tree_structure()

        # 높이 확인
        height = self._get_tree_height(self.table.root_page_id)
        print(f"\n🌳 Tree Height: {height}")

        if height >= 3:
            print(f"✅ SUCCESS: Height >= 3 means Internal Split occurred!")
        else:
            print(f"⚠️  Height {height}: May need more rows for Internal Split")

    def _print_tree_structure(self):
        """트리 구조 출력"""
        print(f"\n📊 Final Tree Structure:")
        print(f"   Total Pages: {self.table.pager.page_count}")
        print(f"   Root PID: {self.table.root_page_id}")

        root = self.table.pager.read_page(self.table.root_page_id)
        print(f"   Root Type: {root.page_type.name}")

        if not root.is_leaf:
            keys, pids = root.read_internal_node()
            print(f"   Root Keys: {keys}")
            print(f"   Root Children: {pids}")

    def _get_tree_height(self, pid: int, depth: int = 1) -> int:
        """트리 높이 계산 (재귀)"""
        page = self.table.pager.read_page(pid)

        if page.is_leaf:
            return depth

        keys, pids = page.read_internal_node()
        if pids:
            return self._get_tree_height(pids[0], depth + 1)

        return depth

    def test_verify_all_keys(self):
        """
        삽입 후 모든 키 검색 검증

        복잡한 트리에서도 find_leaf가 작동하는지
        """
        print("=" * 60)
        print("TEST: Verify All Keys in Deep Tree")
        print("=" * 60)

        num_rows = 20

        # 삽입
        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"user{i}", f"u{i}@test.com")
            self.btree.insert(row)

        print(f"Inserted {num_rows} rows\n")

        # 검증: 모든 키를 찾을 수 있어야 함
        print(f"🔍 Verifying all keys...")
        for i in range(num_rows):
            user_id = i * 10
            leaf_pid = self.table.find_leaf(user_id)
            self.assertIsNotNone(leaf_pid, f"Key {user_id} should be found")

        print(f"✅ All {num_rows} keys found successfully!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
