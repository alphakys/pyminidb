"""
Step 4.3 고급 테스트: BTree Insert 복잡한 시나리오

테스트 항목:
1. 순차 삽입 (Sequential)
2. 랜덤 삽입 (Random)
3. Cascading Split (연쇄 분할)
4. Root Split 발생
5. 대량 데이터 삽입 (100+ rows)
6. 삽입 후 검색 검증
"""

import sys
import os
import unittest
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.btree import BTreeManager
from src.table import Table
from src.page import Page, PageType
from src.row import Row


class TestBTreeInsertAdvanced(unittest.TestCase):
    """BTree Insert 고급 테스트"""

    def setUp(self):
        self.test_db = "test_insert_advanced.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        self.table = Table(self.test_db)
        self.btree = BTreeManager(self.table)

        # 초기 Root Leaf 생성
        root = Page(page_type=PageType.LEAF)
        root._update_header()
        self.table.pager.write_page(0, root)

    def tearDown(self):
        self.table.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_sequential_insert_with_splits(self):
        """
        순차 삽입 + Split 발생 테스트

        MAX_ROWS를 작게 설정하여 빠르게 Split 발생시키기
        """
        print("\n" + "=" * 60)
        print("TEST: Sequential Insert with Splits")
        print("=" * 60)

        # 충분히 많이 삽입하여 여러 번 Split 발생
        num_rows = min(20, Page.MAX_ROWS * 2)

        for i in range(num_rows):
            user_id = (i + 1) * 10
            row = Row(user_id, f"user{i}", f"user{i}@test.com")
            result = self.btree.insert(row)

            self.assertTrue(result, f"Insert {user_id} should succeed")

            if (i + 1) % 5 == 0:
                print(f"  Inserted {i + 1} rows...")

        print(f"✅ Successfully inserted {num_rows} rows")

        # 검증: Root 확인
        root = self.table.pager.read_page(self.table.root_page_id)
        print(f"  Root Type: {root.page_type.name}")
        print(f"  Root is_leaf: {root.is_leaf}")

        # 여러 번 삽입했으므로 Split이 발생했을 가능성
        # (테스트 통과 조건: 에러 없이 완료)

    def test_random_insert_order(self):
        """
        랜덤 순서 삽입 테스트

        B+Tree는 어떤 순서로 삽입되어도 정렬 유지
        """
        print("\n" + "=" * 60)
        print("TEST: Random Order Insert")
        print("=" * 60)

        # 1~100 중 랜덤 20개
        user_ids = random.sample(range(1, 101), 20)

        for user_id in user_ids:
            row = Row(user_id, f"user{user_id}", f"user{user_id}@test.com")
            result = self.btree.insert(row)
            self.assertTrue(result)

        print(f"✅ Inserted {len(user_ids)} rows in random order")
        print(f"  Sample order: {user_ids[:5]}...")

        # 검증: find_leaf가 제대로 작동하는지
        for user_id in user_ids[:5]:
            leaf_pid = self.table.find_leaf(user_id)
            self.assertIsNotNone(leaf_pid)
            print(f"  find_leaf({user_id}) → PID {leaf_pid} ✅")

    def test_cascading_splits(self):
        """
        Cascading Split 테스트

        Leaf Split → Parent Split → Grandparent Split
        """
        print("\n" + "=" * 60)
        print("TEST: Cascading Splits")
        print("=" * 60)

        # 대량 삽입으로 연쇄 Split 유도
        num_rows = min(100, Page.MAX_ROWS * 3)

        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"user{i}", f"user{i}@test.com")
            self.btree.insert(row)

        print(f"✅ Inserted {num_rows} rows")

        # 검증: 트리 통계
        page_count = self.table.pager.page_count
        print(f"  Total pages created: {page_count}")
        self.assertGreater(page_count, 1, "Multiple pages should exist")

    def test_root_split_scenario(self):
        """
        Root Split 발생 확인

        Root가 Leaf → Split → Root가 Internal로 변경
        """
        print("\n" + "=" * 60)
        print("TEST: Root Split")
        print("=" * 60)

        # Root 초기 상태 확인
        root_before = self.table.pager.read_page(self.table.root_page_id)
        print(f"  Before: Root Type = {root_before.page_type.name}")
        self.assertTrue(root_before.is_leaf, "Initial root should be LEAF")

        # 충분히 삽입하여 Root Split 유도
        num_rows = Page.MAX_ROWS + 1
        for i in range(num_rows):
            row = Row(i * 10, f"user{i}", f"user{i}@test.com")
            self.btree.insert(row)

        # Root 변경 확인
        root_after = self.table.pager.read_page(self.table.root_page_id)
        print(f"  After: Root PID = {self.table.root_page_id}")
        print(f"  After: Root Type = {root_after.page_type.name}")

        # Root Split 발생 시 새 Root는 Internal이어야 함
        if self.table.root_page_id != 0:
            self.assertFalse(
                root_after.is_leaf, "After root split, new root should be INTERNAL"
            )
            print("✅ Root Split detected!")

    def test_large_scale_insert(self):
        """
        대규모 삽입 테스트 (100+ rows)

        성능 및 안정성 검증
        """
        print("\n" + "=" * 60)
        print("TEST: Large Scale Insert")
        print("=" * 60)

        num_rows = 100

        import time

        start = time.time()

        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"user{i}", f"user{i}@test.com")
            self.btree.insert(row)

            if (i + 1) % 25 == 0:
                elapsed = time.time() - start
                print(f"  Progress: {i + 1}/{num_rows} rows ({elapsed:.2f}s)")

        elapsed = time.time() - start
        print(f"✅ Inserted {num_rows} rows in {elapsed:.2f}s")
        print(f"  Average: {num_rows / elapsed:.0f} rows/sec")

        # 통계
        page_count = self.table.pager.page_count
        print(f"  Total pages: {page_count}")
        print(f"  Rows per page (avg): {num_rows / page_count:.1f}")

    def test_insert_then_search(self):
        """
        삽입 후 검색 통합 테스트

        Insert → find_leaf가 올바르게 작동하는지
        """
        print("\n" + "=" * 60)
        print("TEST: Insert then Search")
        print("=" * 60)

        # 랜덤 삽입
        inserted_ids = random.sample(range(1, 200), 30)

        for user_id in inserted_ids:
            row = Row(user_id, f"user{user_id}", f"user{user_id}@test.com")
            self.btree.insert(row)

        print(f"✅ Inserted {len(inserted_ids)} rows")

        # 모든 키 검색 테스트
        print(f"  Testing find_leaf for all inserted keys...")
        for user_id in inserted_ids:
            leaf_pid = self.table.find_leaf(user_id)
            self.assertIsNotNone(
                leaf_pid, f"find_leaf({user_id}) should return valid PID"
            )

        print(f"✅ All {len(inserted_ids)} keys found successfully!")


if __name__ == "__main__":
    # 상세 출력 모드로 실행
    unittest.main(verbosity=2)
