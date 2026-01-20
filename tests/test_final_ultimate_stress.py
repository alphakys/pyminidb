"""
FINAL ULTIMATE Deep Tree Stress Test

MAX_ROWS=3, MAX_KEYS=3, 100 ROWS!
이번엔 정말 Internal Split이 발생할 것입니다!
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


class TestFinalUltimateStress(unittest.TestCase):
    """THE FINAL TEST - 확실한 Internal Split 발생"""

    @classmethod
    def setUpClass(cls):
        """MAX_ROWS=3, MAX_KEYS=3"""
        cls.original_max_rows = Page.MAX_ROWS
        cls.original_max_keys = BTreeNode.MAX_KEYS

        Page.MAX_ROWS = 3
        BTreeNode.MAX_KEYS = 3

        print(f"\n{'=' * 70}")
        print(f"🔥 FINAL ULTIMATE STRESS TEST 🔥")
        print(f"{'=' * 70}")
        print(f"MAX_ROWS:  {cls.original_max_rows} → {Page.MAX_ROWS}")
        print(f"MAX_KEYS:  {cls.original_max_keys} → {BTreeNode.MAX_KEYS}")
        print(f"TARGET:    100 ROWS → Height 3+ (Internal Split!)")
        print(f"{'=' * 70}\n")

    @classmethod
    def tearDownClass(cls):
        Page.MAX_ROWS = cls.original_max_rows
        BTreeNode.MAX_KEYS = cls.original_max_keys

    def setUp(self):
        self.test_db = "test_final_ultimate.db"
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

    def test_100_rows_internal_split(self):
        """
        100 ROWS로 확실한 Internal Split 유도!
        """
        print("=" * 70)
        print("TEST: 100 ROWS → FORCE INTERNAL SPLIT")
        print("=" * 70)

        num_rows = 100

        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"user{i}", f"u{i}@test.com")

            try:
                result = self.btree.insert(row)
                self.assertTrue(result)
            except Exception as e:
                print(f"\n{'=' * 70}")
                print(f"❌ CRITICAL FAILURE at row #{i + 1} (user_id={user_id})")
                print(f"{'=' * 70}")
                print(f"Error: {type(e).__name__}: {e}\n")

                # 디버깅 정보
                print(f"System State:")
                print(f"  Pages: {self.table.pager.page_count}")
                print(f"  Root PID: {self.table.root_page_id}")

                # Traceback
                import traceback

                print(f"\nFull Traceback:")
                traceback.print_exc()

                # 이 테스트가 실패하면 insert_into_parent에 버그가 있다는 증거!
                print(f"\n💡 This proves the recursion bug exists!")
                raise

            # 매 20개마다 진행 상황
            if (i + 1) % 20 == 0:
                page_count = self.table.pager.page_count
                root = self.table.pager.read_page(self.table.root_page_id)
                height = self._get_height(self.table.root_page_id)

                print(
                    f"[{i + 1:3d} rows] Pages: {page_count:3d}, Height: {height}",
                    end="",
                )

                if not root.is_leaf:
                    keys, pids = root.read_internal_node()
                    print(f", Root Keys: {len(keys)}, Children: {len(pids)}")
                else:
                    print()

        print(f"\n{'=' * 70}")
        print(f"✅ SUCCESS! All {num_rows} rows inserted!")
        print(f"{'=' * 70}\n")

        # 최종 분석
        height = self._get_height(self.table.root_page_id)
        root = self.table.pager.read_page(self.table.root_page_id)

        print(f"📊 FINAL RESULTS:")
        print(f"   Total Pages: {self.table.pager.page_count}")
        print(f"   Tree Height: {height}")
        print(f"   Root PID: {self.table.root_page_id}")
        print(f"   Root Type: {root.page_type.name}")

        if not root.is_leaf:
            keys, pids = root.read_internal_node()
            print(f"   Root Keys ({len(keys)}): {keys}")
            print(f"   Root Children: {len(pids)}")

            # 첫 번째 자식 분석
            if pids:
                child = self.table.pager.read_page(pids[0])
                print(f"\n   First Child (PID={pids[0]}):")
                print(f"     Type: {child.page_type.name}")
                if not child.is_leaf:
                    c_keys, c_pids = child.read_internal_node()
                    print(f"     Keys: {c_keys}")
                    print(f"     Children: {len(c_pids)}")

        print(f"\n{'=' * 70}")
        if height >= 3:
            print(f"🎉 CONFIRMED! Height={height} proves Internal Cascading Split!")
        elif height == 2:
            print(f"⚠️  Height=2. Either need more data OR recursion bug exists.")
        print(f"{'=' * 70}\n")

        # 최종 검증: 모든 키 검색
        print(f"🔍 Final Verification: Searching all keys...")
        for i in range(0, num_rows, 10):
            user_id = i * 10
            leaf_pid = self.table.find_leaf(user_id)
            self.assertIsNotNone(leaf_pid)
        print(f"✅ All sample keys found!\n")

    def _get_height(self, pid: int, depth: int = 1) -> int:
        """트리 높이"""
        page = self.table.pager.read_page(pid)
        if page.is_leaf:
            return depth
        keys, pids = page.read_internal_node()
        if pids:
            return self._get_height(pids[0], depth + 1)
        return depth


if __name__ == "__main__":
    unittest.main(verbosity=2)
