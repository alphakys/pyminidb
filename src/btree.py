"""
Step 4.3: B+Tree Insert & Split Manager

BTreeManager: B+Tree 삽입 및 Split 로직을 담당하는 클래스
"""

from src.row import Row
from src.page import Page, PageType
from src.pager import Pager
from src.table import Table
from src.node import BTreeNode
from typing import Tuple, Optional, List, Iterator
from src.cursor import Cursor

import bisect


class BTreeManager:
    """
    B+Tree 삽입 및 Split 관리자

    책임:
    - Leaf/Internal Split
    - Insert into Parent (재귀)
    - Root Split 처리
    """

    def __init__(self, table: "Table"):
        """
        Args:
            table: Table 객체 (pager, root_page_id 접근용)
        """
        self.table = table
        self.pager: Pager = table.pager

    def _find_path_to_leaf(self, key: int) -> List[int]:
        """
        주어진 키가 존재할 Leaf Page의 경로를 반환 (Private 메서드)

        Args:
            key: 검색할 키

        Returns:
            List[int]: Root부터 Leaf까지 방문한 모든 PID

        알고리즘:
            1. Root Page 로드
            2. Internal Node를 따라 내려가며 경로 기록
            3. Leaf에 도달하면 경로 반환
        """
        page = self.pager.read_page(self.table.root_page_id)
        pid = self.table.root_page_id
        path = [pid]

        while not page.is_leaf:
            keys, childs = page.read_internal_node()
            idx = bisect.bisect_right(keys, key)
            pid = childs[idx]
            path.append(pid)
            page = self.pager.read_page(pid)

        return path

    def scan(self, start_key: int, end_key: int) -> Iterator[Row]:
        """
        B+Tree Range Scan - Iterator Pattern으로 범위 내 Row 반환

        Algorithm:
            1. start_key가 있을 Leaf Page 찾기 (_find_path_to_leaf)
            2. Sibling pointer를 따라 Leaf Page 순회 (Outer Loop)
            3. 각 페이지의 Row 필터링 (Inner Loop):
                - key < start_key → continue (첫 페이지에서만 발생)
                - key > end_key → return (조기 종료, 불필요한 I/O 방지)
                - start_key <= key <= end_key → yield

        Args:
            start_key: 시작 키 (inclusive)
            end_key: 종료 키 (inclusive)

        Yields:
            Row: 범위 내의 Row 객체들 (정렬된 순서로)

        Example:
            >>> btree = BTreeManager(table)
            >>> for row in btree.scan(10, 100):
            ...     print(row.user_id, row.username)

        Performance:
            - Time: O(log N + K), N=총 Row 수, K=반환되는 Row 수
            - Space: O(1) - Generator 사용으로 메모리 효율적
        """
        leaf_pid = self._find_path_to_leaf(start_key)[-1]
        leaf_page = self.pager.read_page(leaf_pid)

        while leaf_page:
            for i in range(leaf_page.row_count):
                row = leaf_page.read_at(i)
                key = row.user_id
                if key < start_key:
                    continue

                if key > end_key:
                    return
                yield row

            if not leaf_page.has_next_sibling:
                return

            leaf_page = self.pager.read_page(leaf_page.next_sibling_id)

    def insert(self, row: Row) -> bool:
        """
        B+Tree에 Row 삽입

        알고리즘:
        1. find_leaf로 삽입할 Leaf PID 찾기
        2. Leaf 로드
        3. 공간 있으면 바로 삽입
        4. 없으면 split_leaf 후 insert_into_parent

        Args:
            row: 삽입할 Row

        Returns:
            bool: 성공 여부
        """
        path = self._find_path_to_leaf(row.user_id)
        leaf_pid = path[-1]
        leaf = self.pager.read_page(leaf_pid)

        if leaf.is_full:
            new_pid, promote_key = self.split_leaf(leaf_pid)
            self.insert_into_parent(
                left_pid=leaf_pid,
                key=promote_key,
                right_pid=new_pid,
                path=path[:-1],
                parent_pid=path[:-1][-1] if len(path[:-1]) > 0 else None,
            )
        else:
            # Leaf에 정렬된 위치에 삽입 (B+Tree Invariant 유지)
            keys = [leaf.read_at(i).user_id for i in range(leaf.row_count)]
            insert_idx = bisect.bisect_left(keys, row.user_id)

            # Shift: insert_idx부터 뒤쪽 Row들을 한 칸씩 오른쪽으로
            for i in range(leaf.row_count - 1, insert_idx - 1, -1):
                old_row = leaf.read_at(i)
                leaf.write_at(i + 1, old_row)  # write_at은 row_count 건드리지 않음

            # Insert: insert_idx 위치에 새 Row 삽입
            leaf.write_at(insert_idx, row)

            # Metadata 업데이트
            leaf.row_count += 1
            leaf._update_header()

            self.pager.write_page(page_index=leaf_pid, page=leaf)

        return True

    def split_leaf(self, leaf_pid: int) -> Tuple[int, int]:
        """
        Leaf Page Split

        동작:
        1. 기존 Leaf 로드
        2. 중간 지점(MAX_ROWS // 2) 계산
        3. 새 Leaf 생성 (get_new_page_id)
        4. 우측 절반 데이터를 새 Leaf로 이동
        5. Sibling pointer 연결
        6. 양쪽 페이지 저장

        Args:
            leaf_pid: Split할 Leaf PID

        Returns:
            (new_right_pid, promote_key):
                - new_right_pid: 새로 생성된 우측 Leaf PID
                - promote_key: 우측의 첫 번째 키 (부모에 삽입용)
        """
        old_leaf = self.pager.read_page(leaf_pid)
        mid = old_leaf.row_count // 2

        # 새 Leaf 생성
        new_pid = self.pager.get_new_page_id()
        new_page = Page(page_type=PageType.LEAF)

        # 데이터 복사
        old_offset = Page.HEADER_SIZE + (mid * Page.ROW_SIZE)
        old_end = Page.HEADER_SIZE + (old_leaf.row_count * Page.ROW_SIZE)
        copy_size = old_end - old_offset

        new_offset = Page.HEADER_SIZE
        new_page.data[new_offset : new_offset + copy_size] = old_leaf.data[
            old_offset:old_end
        ]

        # Garbage 클리어 (개선!)
        old_leaf.data[old_offset:old_end] = b"\x00" * copy_size

        # 메타데이터 갱신
        new_page.row_count = old_leaf.row_count - mid
        old_leaf.row_count = mid
        old_leaf._next_page_id = new_pid

        # Header 업데이트 (메서드 이름 수정!)
        old_leaf._update_header()
        new_page._update_header()

        # 저장
        self.pager.write_page(leaf_pid, old_leaf)
        self.pager.write_page(new_pid, new_page)

        # Promote Key
        promote_key = new_page.read_at(0).user_id
        return new_pid, promote_key

    def split_internal(self, node_pid: int) -> Tuple[int, int]:
        """
        Internal Page Split

        동작:
        1. 기존 Internal 로드 (keys, pids)
        2. 중간 인덱스(mid) 계산
        3. 좌측: keys[:mid], pids[:mid+1]
        4. 우측: keys[mid+1:], pids[mid+1:]
        5. Promote: keys[mid]
        6. 새 Internal 생성 및 저장

        Args:
            node_pid: Split할 Internal PID

        Returns:
            (new_right_pid, promote_key)
        """
        # 1. 기존 Internal 로드
        old_internal_node = self.pager.read_page(node_pid)
        keys, pids = old_internal_node.read_internal_node()

        # 2. 중간 지점 및 분할
        mid = len(keys) // 2  # row_count 대신 len(keys) 사용 (더 명확)
        promote_key = keys[mid]

        left_keys = keys[:mid]
        left_pids = pids[: mid + 1]
        right_keys = keys[mid + 1 :]
        right_pids = pids[mid + 1 :]

        # 3. 새 Internal 생성 (Right)
        new_pid = self.pager.get_new_page_id()
        new_page = Page(raw_data=None, page_type=PageType.INTERNAL)
        new_page.write_internal_node(right_keys, right_pids)  # row_count 자동 설정됨

        # 4. 기존 Internal 업데이트 (Left)
        old_internal_node.write_internal_node(
            left_keys, left_pids
        )  # row_count 자동 설정됨

        # 5. 저장
        self.pager.write_page(node_pid, old_internal_node)
        self.pager.write_page(new_pid, new_page)

        return new_pid, promote_key

    def insert_into_parent(
        self,
        left_pid: int,
        key: int,
        right_pid: int,
        path: List[int],
        parent_pid: Optional[int] = None,
    ):
        """
        부모 노드에 키 삽입

        Cases:
        1. 부모 없음 (Root Split) → 새 Root 생성
        2. 부모 있고 공간 있음 → 직접 삽입
        3. 부모 있고 가득 참 → split_internal 후 재귀

        Args:
            left_pid: 좌측 Child PID
            key: 삽입할 키
            right_pid: 우측 Child PID
            parent_pid: 부모 PID (None이면 Root Split)
        """
        # TODO: 가장 복잡한 부분! 천천히 구현
        # Case 1: Root Split
        if parent_pid is None:
            # 새 Root 생성
            new_root_pid = self.pager.get_new_page_id()
            root = Page(raw_data=None, page_type=PageType.INTERNAL)
            root.write_internal_node(keys=[key], pids=[left_pid, right_pid])
            self.pager.write_page(new_root_pid, root)
            self.table.root_page_id = new_root_pid

        else:
            # Case 2 & 3: 부모에 삽입
            parent_page = self.pager.read_page(parent_pid)
            keys, pids = parent_page.read_internal_node()

            # ✅ 먼저 키를 삽입 (공간 여부와 관계없이!)
            idx = bisect.bisect_right(keys, key)
            keys.insert(idx, key)
            pids.insert(idx + 1, right_pid)

            if (
                len(keys) > BTreeNode.MAX_KEYS
            ):  # Note: MAX_KEYS는 최대 키 개수이므로, 초과하면 split
                # Case 3: 공간 없음 - 저장 후 Split
                parent_page.write_internal_node(keys, pids)
                self.pager.write_page(parent_pid, parent_page)

                new_pid, promote_key = self.split_internal(parent_pid)
                grandparent_pid = path[-1] if len(path) > 0 else None

                self.insert_into_parent(
                    left_pid=parent_pid,
                    key=promote_key,
                    right_pid=new_pid,
                    parent_pid=grandparent_pid,
                    path=path[:-1] if len(path) > 0 else [],
                )
            else:
                # Case 2: 공간 있음 - 그냥 저장
                parent_page.write_internal_node(keys, pids)
                self.pager.write_page(parent_pid, parent_page)
