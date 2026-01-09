from src.row import Row
from typing import ClassVar, Optional
import struct


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

    def __init__(self, raw_data: bytes = None):
        if raw_data:
            self.data: bytearray = bytearray(raw_data)
            self._row_count = self.header_struct.unpack(self.data[: Page.HEADER_SIZE])[
                0
            ]
        else:
            self.data: bytearray = bytearray(Page.PAGE_SIZE)
            self._row_count = 0
            self._page_type = 0
            self._free_space = 0
            self._next_page_id = 0

    @property
    def row_count(self):
        """
        Row의 개수가 몇개 인지 반환
        """
        return self._row_count

    def _update_header(self):
        """
        현재 self.row_count 값을 self.data[0:4]에 struct.pack으로 기록합니다.
        insert 할 때마다 호출해줘야 디스크에도 개수가 저장되겠죠?
        """
        self.data[: Page.HEADER_SIZE] = self.header_struct.pack(
            self._row_count, self._page_type, self._free_space, self._next_page_id
        )

    def is_full(self) -> bool:
        return True if self._row_count >= Page.MAX_ROWS else False

    def insert(self, row: Row) -> bool:
        """
        [TODO 3] Offset 계산 공식 수정
        Row가 저장될 위치는 이제 0이 아니라 4(HEADER_SIZE)부터 시작합니다.
        New Offset = HEADER_SIZE + (index * ROW_SIZE)

        그리고 성공 후에 _update_header()를 꼭 호출하세요.
        """
        offset = Page.HEADER_SIZE + (self._row_count * Page.ROW_SIZE)
        end = offset + Page.ROW_SIZE
        self.data[offset:end] = row.serialize()
        self._row_count += 1
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
