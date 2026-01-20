"""
ULTRA DEBUG TEST - 상세 로깅

insert_into_parent 호출 추적
Root 변경 추적
Split 발생 추적
"""

import sys, os, unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.btree import BTreeManager
from src.table import Table
from src.page import Page, PageType
from src.row import Row
from src.node import BTreeNode


# 글로벌 카운터
insert_into_parent_calls = 0
root_modifications = []


class DebugBTreeManager(BTreeManager):
    """디버깅용 BTreeManager"""

    def insert_into_parent(self, left_pid, key, right_pid, path, parent_pid=None):
        global insert_into_parent_calls, root_modifications
        insert_into_parent_calls += 1

        is_root_insert = parent_pid is None

        print(f"\n{'=' * 60}")
        print(f"📞 insert_into_parent CALL #{insert_into_parent_calls}")
        print(f"   Left: {left_pid}, Key: {key}, Right: {right_pid}")
        print(
            f"   Parent: {parent_pid} ({'ROOT SPLIT' if is_root_insert else 'Normal'})"
        )
        print(f"   Path: {path}")

        # 부모 정보 (있으면)
        if parent_pid is not None:
            parent_page = self.pager.read_page(parent_pid)
            if not parent_page.is_leaf:
                old_keys, old_pids = parent_page.read_internal_node()
                print(f"   Parent BEFORE: keys={old_keys}, children={len(old_pids)}")

        # 원본 메서드 호출
        super().insert_into_parent(left_pid, key, right_pid, path, parent_pid)

        # 부모 정보 (수정 후)
        if parent_pid is not None:
            parent_page = self.pager.read_page(parent_pid)
            if not parent_page.is_leaf:
                new_keys, new_pids = parent_page.read_internal_node()
                print(f"   Parent AFTER:  keys={new_keys}, children={len(new_pids)}")

        # Root 변경 추적
        if parent_pid == self.table.root_page_id or is_root_insert:
            root = self.pager.read_page(self.table.root_page_id)
            if not root.is_leaf:
                r_keys, r_pids = root.read_internal_node()
                root_modifications.append(
                    {
                        "call": insert_into_parent_calls,
                        "keys": r_keys.copy(),
                        "children": len(r_pids),
                    }
                )
                print(f"   🔥 ROOT MODIFIED: keys={r_keys}, children={len(r_pids)}")

        print(f"{'=' * 60}")


class TestUltraDebug(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_max_rows = Page.MAX_ROWS
        cls.original_max_keys = BTreeNode.MAX_KEYS
        Page.MAX_ROWS = 3
        BTreeNode.MAX_KEYS = 3

        global insert_into_parent_calls, root_modifications
        insert_into_parent_calls = 0
        root_modifications = []

    @classmethod
    def tearDownClass(cls):
        Page.MAX_ROWS = cls.original_max_rows
        BTreeNode.MAX_KEYS = cls.original_max_keys

    def setUp(self):
        self.test_db = "test_ultra_debug.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.table = Table(self.test_db)
        self.btree = DebugBTreeManager(self.table)  # Debug 버전!
        root = Page(page_type=PageType.LEAF)
        root._update_header()
        self.table.pager.write_page(0, root)

    def tearDown(self):
        self.table.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_20_rows_detailed(self):
        """20 rows만 삽입하여 상세 추적"""
        print(f"\n{'=' * 70}")
        print(f"🔍 ULTRA DEBUG: 20 ROWS (MAX_ROWS=3, MAX_KEYS=3)")
        print(f"{'=' * 70}\n")

        num_rows = 20

        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"u{i}", f"u{i}@t.com")

            print(f"\n>>> Inserting Row #{i + 1} (user_id={user_id})")

            try:
                self.btree.insert(row)
            except Exception as e:
                print(f"\n❌ FAILED!")
                import traceback

                traceback.print_exc()
                raise

        # 최종 분석
        print(f"\n{'=' * 70}")
        print(f"📊 FINAL ANALYSIS")
        print(f"{'=' * 70}")
        print(f"Total insert_into_parent calls: {insert_into_parent_calls}")
        print(f"\nRoot Modification History:")
        for i, mod in enumerate(root_modifications):
            print(
                f"  [{i + 1}] Call #{mod['call']}: keys={mod['keys']}, children={mod['children']}"
            )

        root = self.table.pager.read_page(self.table.root_page_id)
        height = self._get_height(self.table.root_page_id)

        print(f"\nFinal State:")
        print(f"  Height: {height}")
        print(f"  Pages: {self.table.pager.page_count}")

        if not root.is_leaf:
            keys, pids = root.read_internal_node()
            print(f"  Root Keys: {keys}")
            print(f"  Root Children: {len(pids)}")

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
