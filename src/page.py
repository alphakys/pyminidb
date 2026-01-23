from src.row import Row
from src.node import BTreeNode
from typing import ClassVar, Optional, Tuple, List
from enum import IntEnum
import struct


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
    MAX_ROWS: ClassVar[int] = (PAGE_SIZE - 9) // ROW_SIZE

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
            self._next_page_id: int = 0
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

    def write_at(self, row: Row) -> bool:
        """
        [TODO 3] Offset 계산 공식 수정
        Row가 저장될 위치는 이제 0이 아니라 4(HEADER_SIZE)부터 시작합니다.
        New Offset = HEADER_SIZE + (index * ROW_SIZE)

        그리고 성공 후에 update_header()를 꼭 호출하세요.
        """
        offset = Page.HEADER_SIZE + (self.row_count * Page.ROW_SIZE)
        end = offset + Page.ROW_SIZE
        self.data[offset:end] = row.serialize()
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
