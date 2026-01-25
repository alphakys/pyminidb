from src.row import Row
from src.node import BTreeNode
from typing import ClassVar, Optional, Tuple, List
from enum import IntEnum
import struct

# [Sentinel Value] "다음 페이지 없음"을 의미하는 특별한 값
# 현재는 0을 사용하지만, 나중에 0xFFFFFFFF로 변경 가능
# (PostgreSQL/MySQL 스타일로 전환 시 여기만 수정하면 됨)
INVALID_PAGE_ID = 0


class PageType(IntEnum):
    """Page 타입 구분"""

    LEAF = 1  # Data Page (Row 저장)
    INTERNAL = 2  # Index Page (keys + child PIDs)


class Page:
    """
    4KB 크기의 메모리 블록을 관리하며 여러 Row를 저장합니다.
    파일 시스템과 소통하는 Pager에서 읽어온 raw bytes 데이터를 페이지라는 단위로
    분할하여 구조화하는 모듈이다.

    Page의 앞단 9byte를 header 영역으로 둔다.

    row_count: 현재 페이지에 저장된 Row 개수 (우리가 필요한 것!)
    PageType: 이게 데이터를 담는 리프 노드인지, 인덱스 노드인지 등.
    FreeSpace: 남은 공간이 얼만큼인지.
    NextPageId: (B-Tree 연결을 위한) 다음 페이지 번호.
    """

    # OS Page Size
    PAGE_SIZE: ClassVar[int] = 4096
    ROW_SIZE: ClassVar[int] = Row(0, "", "").size
    MAX_ROWS: ClassVar[int] = 10  # (PAGE_SIZE - 9) // ROW_SIZE

    # [New] Header Constants
    HEADER_FORMAT: ClassVar[str] = f"<HBHI"
    HEADER_SIZE: ClassVar[int] = 9
    header_struct: ClassVar[struct.Struct] = struct.Struct(HEADER_FORMAT)

    def __init__(self, raw_data: bytes = None, page_type: PageType = PageType.LEAF):
        """
        Args:
            raw_data: 디스크에서 읽어온 바이트 (없으면 새 페이지)
            page_type: Leaf 또는 Internal (기본값: Leaf)
        """
        if raw_data:
            self.data: bytearray = bytearray(raw_data)
            # 🔧 Header 전체 언팩 (4개 필드 모두)
            header_values = self.header_struct.unpack(self.data[: Page.HEADER_SIZE])
            self.row_count = header_values[0]
            self.page_type = PageType(header_values[1])  # Enum으로 변환
            self._free_space = header_values[2]
            self._next_page_id: int = header_values[3]
        else:
            self.data: bytearray = bytearray(Page.PAGE_SIZE)
            self.row_count = 0
            self.page_type = page_type  # 생성 시 타입 지정
            self._free_space = 0
            self._next_page_id: int = INVALID_PAGE_ID
            self._update_header()

    def row_count(self):
        """
        Row의 개수가 몇개 인지 반환
        """
        return self.row_count

    @property
    def is_leaf(self) -> bool:
        """이 페이지가 Leaf인지 확인"""
        return self.page_type == PageType.LEAF

    @property
    def has_next_sibling(self) -> bool:
        """
        다음 형제 Leaf Page가 존재하는지 확인

        Returns:
            bool: True if next sibling exists, False otherwise

        Example:
            >>> if page.has_next_sibling:
            ...     next_page = pager.read_page(page.next_sibling_id)

        Note:
            INVALID_PAGE_ID는 "다음 페이지 없음"을 의미합니다.
            Root Page ID도 0이지만, Leaf chain에서는 혼동 없음.
            (Root는 Internal이 되면 sibling chain에서 제외됨)
        """
        return self._next_page_id != INVALID_PAGE_ID

    @property
    def next_sibling_id(self) -> int:
        """
        다음 형제 페이지 ID (raw value)

        Returns:
            int: 다음 페이지 ID (INVALID_PAGE_ID일 수 있음)

        Warning:
            사용 전 has_next_sibling을 먼저 체크하세요!
            확인하지 않으면 INVALID_PAGE_ID를 반환할 수 있습니다.

        Example:
            >>> if page.has_next_sibling:
            ...     next_pid = page.next_sibling_id
            ...     next_page = pager.read_page(next_pid)
        """
        return self._next_page_id

    def page_type(self) -> PageType:
        """페이지 타입 반환"""
        return self.page_type

    def _update_header(self):
        """
        현재 self.row_count 값을 self.data[0:4]에 struct.pack으로 기록합니다.
        insert 할 때마다 호출해줘야 디스크에도 개수가 저장되겠죠?
        """
        self.data[: Page.HEADER_SIZE] = self.header_struct.pack(
            self.row_count, self.page_type, self._free_space, self._next_page_id
        )

    @property
    def is_full(self) -> bool:
        return True if self.row_count >= Page.MAX_ROWS else False

    def get_next_sibling_id(self) -> Optional[int]:
        """
        다음 형제 Leaf Page ID 반환

        Returns:
            int: 다음 페이지 ID (있을 경우)
            None: 더 이상 형제 페이지 없음

        Example:
            >>> next_pid = page.get_next_sibling_id()
            >>> if next_pid is not None:
            ...     next_page = pager.read_page(next_pid)
        """
        if self._next_page_id == INVALID_PAGE_ID:
            return None
        return self._next_page_id

    def write_at(self, index: int, row: Row) -> None:
        """
        특정 index 위치에 Row 덮어쓰기 (Low-level operation)

        ⚠️ 주의: row_count를 건드리지 않음!
        호출자가 직접 row_count와 _update_header()를 관리해야 함.

        Args:
            index: 0-based index (0 <= index < MAX_ROWS)
            row: 덮어쓸 Row 객체

        Raises:
            IndexError: index가 유효 범위를 벗어난 경우

        Use Cases:
            - BTreeManager의 sorted insert (shift 연산)
            - Update 연산 (미래)
            - 내부적으로 append()에서 사용

        Example:
            >>> # Shift 연산 예시
            >>> for i in range(page.row_count - 1, insert_pos - 1, -1):
            ...     old_row = page.read_at(i)
            ...     page.write_at(i + 1, old_row)  # row_count 건드리지 않음!
            >>> page.write_at(insert_pos, new_row)
            >>> page.row_count += 1  # 호출자가 관리!
            >>> page._update_header()
        """
        if index < 0 or index >= Page.MAX_ROWS:
            raise IndexError(f"Index {index} out of range [0, {Page.MAX_ROWS})")

        offset = Page.HEADER_SIZE + (index * Page.ROW_SIZE)
        end = offset + Page.ROW_SIZE
        self.data[offset:end] = row.serialize()

    def append(self, row: Row) -> bool:
        """
        Leaf 끝에 Row 추가 (High-level operation)

        내부적으로 write_at(row_count, row) 호출 후
        row_count 증가 및 header 업데이트를 자동으로 수행.

        Args:
            row: 추가할 Row 객체

        Returns:
            bool: 성공 여부 (항상 True, 호환성 유지)

        Raises:
            OverflowError: Page가 가득 찬 경우

        Use Cases:
            - Sequential insert (기존 write_at 대체)
            - Split 후 데이터 추가

        Example:
            >>> page.append(Row(10, 'alice', 'alice@test.com'))
            True
            >>> page.row_count
            1
        """
        if self.row_count >= Page.MAX_ROWS:
            raise OverflowError(f"Page is full (MAX_ROWS={Page.MAX_ROWS})")

        self.write_at(self.row_count, row)
        self.row_count += 1
        self._update_header()
        return True

    def read_at(self, row_index: int) -> Row:
        """
        Page내에서 target index Row를 읽는다.
        """
        offset = Page.HEADER_SIZE + (row_index * Page.ROW_SIZE)
        end = offset + Page.ROW_SIZE
        raw_data = self.data[offset:end]
        return Row.deserialize(raw_data)

    def read_internal_node(self) -> Tuple[List[int], List[int]]:
        """
        Internal Page에서 keys, pids 읽기
        """
        if not self.is_leaf:
            # Header(9 bytes) 이후부터 읽기
            return BTreeNode.deserialize_internal(self.data[Page.HEADER_SIZE :])
        raise TypeError("Not an Internal page")

    def write_internal_node(self, keys: List[int], pids: List[int]):
        """
        Internal Page에 keys, pids 쓰기
        """
        if not self.is_leaf:
            body = BTreeNode.serialize_internal(keys, pids)
            # Header(9 bytes) 이후에 덮어쓰기
            self.data[Page.HEADER_SIZE : Page.HEADER_SIZE + len(body)] = body

            # RowCount는 Key 개수로 사용
            self.row_count = len(keys)
            self._update_header()
        else:
            raise TypeError("Not an Internal page")
