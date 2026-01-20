"""
MASSIVE SCALE TEST - 500 ROWS!
"""

import sys, os, unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.btree import BTreeManager
from src.table import Table
from src.page import Page, PageType
from src.row import Row
from src.node import BTreeNode


class TestMassiveScale(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_max_rows = Page.MAX_ROWS
        cls.original_max_keys = BTreeNode.MAX_KEYS
        Page.MAX_ROWS = 3
        BTreeNode.MAX_KEYS = 3
        print(f"\n{'=' * 70}")
        print(f"🚀 MASSIVE SCALE: 500 ROWS!")
        print(f"MAX_ROWS=3, MAX_KEYS=3")
        print(f"{'=' * 70}\n")

    @classmethod
    def tearDownClass(cls):
        Page.MAX_ROWS = cls.original_max_rows
        BTreeNode.MAX_KEYS = cls.original_max_keys

    def setUp(self):
        self.test_db = "test_massive.db"
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

    def test_500_rows(self):
        num_rows = 500

        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"u{i}", f"u{i}@t.com")
            try:
                self.btree.insert(row)
            except Exception as e:
                print(f"\n❌ FAILED at row {i + 1} (user_id={user_id})")
                print(f"Error: {e}")
                import traceback

                traceback.print_exc()
                raise

            if (i + 1) % 100 == 0:
                height = self._get_height(self.table.root_page_id)
                print(
                    f"[{i + 1:3d} rows] Height: {height}, Pages: {self.table.pager.page_count}"
                )

        height = self._get_height(self.table.root_page_id)
        root = self.table.pager.read_page(self.table.root_page_id)

        print(f"\n{'=' * 70}")
        print(f"✅ {num_rows} rows inserted!")
        print(f"Height: {height}")
        print(f"Pages: {self.table.pager.page_count}")

        if not root.is_leaf:
            keys, pids = root.read_internal_node()
            print(f"Root Keys ({len(keys)}): {keys}")

        if height >= 3:
            print(f"🎉 HEIGHT 3+ ACHIEVED! Internal Split confirmed!")
        else:
            print(f"⚠️  Still Height {height}")
        print(f"{'=' * 70}\n")

    def _get_height(self, pid, depth=1):
        page = self.table.pager.read_page(pid)
        if page.is_leaf:
            return depth
        keys, pids = page.read_internal_node()
        if pids:
            return self._get_height(pids[0], depth + 1)
        return depth


if __name__ == "__main__":
    unittest.main(verbosity=2)
