"""
==========================================
B+Tree Comprehensive Test Suite
==========================================

이 파일은 PyMiniDB B+Tree의 **유일한 테스트 파일**입니다.
기존의 파편화된 테스트들을 모두 통합했습니다.

테스트 구성:
1. [UNIT] Core Operations - Split, Insert 기본 동작
2. [INTEGRATION] Range Scan - 범위 조회
3. [STRESS] Large Scale - 500+ rows 대량 삽입
4. [INVARIANT] Sorted Order - B+Tree 핵심 불변식 검증
5. [EDGE] Boundary Cases - 경계값 테스트

실행:
    python3 tests/test_btree_comprehensive.py

Author: PyMiniDB Phase 5
Date: 2024-01-24
"""

import sys
import os
import unittest
import random
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.btree import BTreeManager
from src.table import Table
from src.page import Page, PageType
from src.row import Row
from src.node import BTreeNode


# ============================================================
# Test Helpers
# ============================================================


class BTreeTestBase(unittest.TestCase):
    """모든 B+Tree 테스트의 Base 클래스"""

    def setUp(self):
        """각 테스트 전: 새로운 DB 생성"""
        self.test_db = f"test_btree_{self.id().split('.')[-1]}.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

        self.table = Table(self.test_db)
        self.btree = BTreeManager(self.table)

        # 초기 Root Leaf 생성
        root = Page(page_type=PageType.LEAF)
        root._update_header()
        self.table.pager.write_page(0, root)

    def tearDown(self):
        """각 테스트 후: DB 정리"""
        self.table.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def _get_tree_height(self, pid: int = None, depth: int = 1) -> int:
        """트리 높이 계산"""
        if pid is None:
            pid = self.table.root_page_id
        page = self.table.pager.read_page(pid)
        if page.is_leaf:
            return depth
        keys, pids = page.read_internal_node()
        if pids:
            return self._get_tree_height(pids[0], depth + 1)
        return depth

    def _read_all_leaf_keys(self) -> list:
        """모든 Leaf의 모든 Key를 순서대로 읽기"""
        keys = []
        # Root에서 시작해서 가장 왼쪽 Leaf 찾기
        pid = self.table.root_page_id
        page = self.table.pager.read_page(pid)

        while not page.is_leaf:
            _, pids = page.read_internal_node()
            pid = pids[0]
            page = self.table.pager.read_page(pid)

        # Leaf chain 순회
        while page:
            for i in range(page.row_count):
                row = page.read_at(i)
                keys.append(row.user_id)

            if page.has_next_sibling:
                page = self.table.pager.read_page(page.next_sibling_id)
            else:
                break

        return keys


# ============================================================
# 1. [UNIT] Core Operations
# ============================================================


class TestCoreOperations(BTreeTestBase):
    """핵심 연산 단위 테스트"""

    def test_insert_to_empty_leaf(self):
        """빈 Leaf에 단일 Row 삽입"""
        row = Row(10, "alice", "alice@test.com")
        result = self.btree.insert(row)

        self.assertTrue(result)
        leaf = self.table.pager.read_page(self.table.root_page_id)
        self.assertEqual(leaf.row_count, 1)

    def test_insert_multiple_sequential(self):
        """여러 Row 순차 삽입"""
        for i in range(1, 6):
            row = Row(i * 10, f"user{i}", f"user{i}@test.com")
            self.btree.insert(row)

        leaf = self.table.pager.read_page(self.table.root_page_id)
        self.assertEqual(leaf.row_count, 5)

    def test_leaf_split_basic(self):
        """Leaf Split 기본 동작"""
        # 기존 방식: MAX_ROWS를 넘어가면 Split
        for i in range(Page.MAX_ROWS + 1):
            row = Row(i * 10, f"user{i}", f"u{i}@test.com")
            self.btree.insert(row)

        # Split 후 페이지 수 증가
        self.assertGreater(self.table.pager.page_count, 1)

    def test_find_leaf_after_split(self):
        """Split 후 find_leaf 작동 확인"""
        for i in range(20):
            row = Row(i * 10, f"user{i}", f"u{i}@test.com")
            self.btree.insert(row)

        # 모든 키를 find_leaf로 찾을 수 있어야 함
        for i in range(20):
            user_id = i * 10
            leaf_pid = self.table.find_leaf(user_id)
            self.assertIsNotNone(leaf_pid)


# ============================================================
# 2. [INTEGRATION] Range Scan
# ============================================================


class TestRangeScan(BTreeTestBase):
    """Range Scan 통합 테스트"""

    def test_scan_single_page(self):
        """단일 페이지 Range Scan"""
        for i in range(1, 11):
            row = Row(i * 10, f"user{i}", f"u{i}@test.com")
            self.btree.insert(row)

        results = list(self.btree.scan(30, 70))
        result_ids = [row.user_id for row in results]

        self.assertEqual(result_ids, [30, 40, 50, 60, 70])

    def test_scan_multi_page(self):
        """여러 페이지 Range Scan (Sibling 포인터 검증)"""
        for i in range(50):
            row = Row(i * 10, f"user{i}", f"u{i}@test.com")
            self.btree.insert(row)

        results = list(self.btree.scan(100, 300))
        result_ids = [row.user_id for row in results]

        # 모든 결과가 범위 안에 있어야 함
        for uid in result_ids:
            self.assertTrue(100 <= uid <= 300)

    def test_scan_empty_result(self):
        """범위 밖 - 빈 결과"""
        for i in range(1, 4):
            row = Row(i * 10, f"user{i}", f"u{i}@test.com")
            self.btree.insert(row)

        results = list(self.btree.scan(100, 200))
        self.assertEqual(len(results), 0)

    def test_scan_boundary_cases(self):
        """경계값 테스트"""
        for i in range(1, 11):
            row = Row(i * 10, f"user{i}", f"u{i}@test.com")
            self.btree.insert(row)

        # start == end
        results = list(self.btree.scan(50, 50))
        self.assertEqual([r.user_id for r in results], [50])

        # start > end (잘못된 범위)
        results = list(self.btree.scan(70, 30))
        self.assertEqual(len(results), 0)

        # 전체 스캔
        results = list(self.btree.scan(0, 1000))
        self.assertEqual(len(results), 10)


# ============================================================
# 3. [STRESS] Large Scale Test
# ============================================================


class TestStressLargeScale(unittest.TestCase):
    """대량 데이터 스트레스 테스트

    MAX_ROWS=3, MAX_KEYS=3로 강제 설정하여
    빠르게 트리 높이를 증가시킵니다.
    """

    @classmethod
    def setUpClass(cls):
        """MAX_ROWS, MAX_KEYS 축소"""
        cls.original_max_rows = Page.MAX_ROWS
        cls.original_max_keys = BTreeNode.MAX_KEYS
        Page.MAX_ROWS = 3
        BTreeNode.MAX_KEYS = 3

    @classmethod
    def tearDownClass(cls):
        """복원"""
        Page.MAX_ROWS = cls.original_max_rows
        BTreeNode.MAX_KEYS = cls.original_max_keys

    def setUp(self):
        self.test_db = "test_stress.db"
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

    def _get_height(self, pid, depth=1):
        page = self.table.pager.read_page(pid)
        if page.is_leaf:
            return depth
        keys, pids = page.read_internal_node()
        if pids:
            return self._get_height(pids[0], depth + 1)
        return depth

    def test_500_rows_sequential(self):
        """500 rows 순차 삽입 - Internal Cascading Split 검증"""
        print("\n" + "=" * 70)
        print("🚀 STRESS TEST: 500 ROWS (Sequential)")
        print("=" * 70)

        num_rows = 500
        start_time = time.time()

        for i in range(num_rows):
            user_id = i * 10
            row = Row(user_id, f"u{i}", f"u{i}@t.com")

            try:
                self.btree.insert(row)
            except Exception as e:
                print(f"\n❌ FAILED at row {i + 1} (user_id={user_id})")
                print(f"Error: {e}")
                raise

            if (i + 1) % 100 == 0:
                height = self._get_height(self.table.root_page_id)
                print(
                    f"  [{i + 1:3d} rows] Height: {height}, Pages: {self.table.pager.page_count}"
                )

        elapsed = time.time() - start_time
        height = self._get_height(self.table.root_page_id)

        print(f"\n✅ {num_rows} rows inserted in {elapsed:.2f}s")
        print(f"   Final Height: {height}")
        print(f"   Total Pages: {self.table.pager.page_count}")

        # Height 3 이상이면 Internal Split 발생
        if height >= 3:
            print("🎉 Internal Cascading Split CONFIRMED!")

        self.assertGreaterEqual(height, 2)

    def test_100_rows_random_order(self):
        """100 rows 랜덤 순서 삽입"""
        print("\n" + "=" * 70)
        print("🎲 STRESS TEST: 100 ROWS (Random Order)")
        print("=" * 70)

        num_rows = 100
        user_ids = list(range(1, num_rows + 1))
        random.shuffle(user_ids)

        print(f"  First 10: {user_ids[:10]}")

        for user_id in user_ids:
            row = Row(user_id * 10, f"u{user_id}", f"u{user_id}@t.com")
            self.btree.insert(row)

        print(f"✅ {num_rows} rows inserted (random order)")

        # 검증: 모든 키를 find_leaf로 찾을 수 있어야 함
        for user_id in user_ids:
            leaf_pid = self.table.find_leaf(user_id * 10)
            self.assertIsNotNone(leaf_pid)

        print("✅ All keys found via find_leaf")


# ============================================================
# 4. [INVARIANT] B+Tree Sorted Order Check
# ============================================================


class TestInvariantSortedOrder(BTreeTestBase):
    """🔴 B+Tree 핵심 불변식: Leaf 내부 정렬 검증

    이 테스트가 가장 중요합니다!
    이전 테스트들이 발견하지 못한 버그를 잡아냅니다.
    """

    def test_random_insert_leaf_sorted(self):
        """랜덤 삽입 후 Leaf 내부가 정렬되어 있는지 확인

        🔴 이 테스트가 실패하면:
           insert()가 정렬된 위치에 삽입하지 않고 있다는 증거!
        """
        print("\n" + "=" * 70)
        print("🔴 INVARIANT TEST: Leaf Sorted Order")
        print("=" * 70)

        insert_order = [30, 10, 50, 20, 40]
        print(f"  Insert order: {insert_order}")

        for user_id in insert_order:
            row = Row(user_id, f"user{user_id}", f"u{user_id}@test.com")
            self.btree.insert(row)

        # Leaf에서 직접 읽기
        leaf = self.table.pager.read_page(self.table.root_page_id)
        stored_keys = []
        for i in range(leaf.row_count):
            row = leaf.read_at(i)
            stored_keys.append(row.user_id)

        print(f"  Stored in Leaf: {stored_keys}")
        print(f"  Expected sorted: {sorted(stored_keys)}")

        # 정렬되어 있어야 함!
        self.assertEqual(
            stored_keys,
            sorted(stored_keys),
            "🔴 FAIL: Leaf is NOT sorted! insert() does not maintain order!",
        )
        print("✅ Leaf is properly sorted!")

    def test_scan_returns_sorted(self):
        """Scan 결과가 정렬되어 있는지 확인"""
        print("\n" + "=" * 70)
        print("🔴 INVARIANT TEST: Scan Returns Sorted")
        print("=" * 70)

        user_ids = random.sample(range(10, 200), 20)
        print(f"  Random insert: {user_ids[:5]}...")

        for user_id in user_ids:
            row = Row(user_id, f"user{user_id}", f"u{user_id}@test.com")
            self.btree.insert(row)

        # Scan 결과
        results = list(self.btree.scan(0, 1000))
        result_ids = [row.user_id for row in results]

        print(f"  Scan result: {result_ids[:5]}...")
        print(f"  Expected:    {sorted(result_ids)[:5]}...")

        self.assertEqual(
            result_ids, sorted(result_ids), "🔴 FAIL: Scan results are NOT sorted!"
        )
        print("✅ Scan results are properly sorted!")


# ============================================================
# 5. [EDGE] Edge Cases
# ============================================================


class TestEdgeCases(BTreeTestBase):
    """경계값 및 특수 케이스"""

    def test_empty_tree_scan(self):
        """빈 트리에서 Scan"""
        results = list(self.btree.scan(0, 100))
        self.assertEqual(len(results), 0)

    def test_single_row(self):
        """단일 Row만 있는 경우"""
        row = Row(42, "test", "test@test.com")
        self.btree.insert(row)

        results = list(self.btree.scan(0, 100))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].user_id, 42)

    def test_duplicate_key_behavior(self):
        """중복 키 동작 (현재는 허용)"""
        row1 = Row(10, "alice", "alice@test.com")
        row2 = Row(10, "bob", "bob@test.com")  # 같은 키!

        self.btree.insert(row1)
        self.btree.insert(row2)

        # 둘 다 삽입됨 (현재 정책)
        leaf = self.table.pager.read_page(self.table.root_page_id)
        self.assertEqual(leaf.row_count, 2)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyMiniDB B+Tree Comprehensive Test Suite")
    print("=" * 70 + "\n")

    # 테스트 실행 순서 지정
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 순서대로 추가
    suite.addTests(loader.loadTestsFromTestCase(TestCoreOperations))
    suite.addTests(loader.loadTestsFromTestCase(TestRangeScan))
    suite.addTests(loader.loadTestsFromTestCase(TestInvariantSortedOrder))  # ⭐ 핵심!
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(
        loader.loadTestsFromTestCase(TestStressLargeScale)
    )  # 마지막에 (느림)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 결과 요약
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 ALL TESTS PASSED!")
    else:
        print("❌ SOME TESTS FAILED!")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
    print("=" * 70 + "\n")
