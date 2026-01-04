from src.row import Row
from typing import ClassVar, Optional
import struct


class Page:
    """
    [Phase 2] Page Abstraction
    4KB 크기의 메모리 블록을 관리하며 여러 Row를 저장합니다.

    Page의 앞단 9byte를 header 영역으로 둔다.

    NumCells: 현재 페이지에 저장된 Row 개수 (우리가 필요한 것!)
    PageType: 이게 데이터를 담는 리프 노드인지, 인덱스 노드인지 등.
    FreeSpace: 남은 공간이 얼만큼인지.
    NextPageId: (B-Tree 연결을 위한) 다음 페이지 번호.
    """

    # OS Page Size
    PAGE_SIZE: ClassVar[int] = 4096
    ROW_SIZE: ClassVar[int] = Row(0, "", "").size
    MAX_ROWS: ClassVar[int] = PAGE_SIZE // ROW_SIZE

    # [New] Header Constants
    HEADER_FORMAT: ClassVar[str] = f"<HBHI"
    HEADER_SIZE: ClassVar[int] = 9
    header_struct: ClassVar[struct.Struct] = struct.Struct(HEADER_FORMAT)

    def __init__(self, raw_data: bytes = None):
        """
        [TODO 1] 생성자 수정: Header 처리
        1. raw_data가 None이면: 빈 bytearray 생성, num_rows=0
        2. raw_data가 있으면:
           - self.data에 복사
           - **Header(0~4 byte)**를 읽어서 self.num_rows 복구! <-- 핵심
        """
        self.page_type = 0  # Leaf Node default value
        self.free_space = 0
        self.next_page_id = 0
        if raw_data:
            self.data: bytearray = bytearray(raw_data)
            self.num_rows = self.header_struct.unpack(raw_data[: Page.HEADER_SIZE])[0]
            print("Number of Rows : ", self.num_rows)
        else:
            self.data: bytearray = bytearray(Page.PAGE_SIZE)
            self.num_rows = 0

    def _update_header(self):
        """
        [TODO 2] Helper Helper: Header 동기화
        현재 self.num_rows 값을 self.data[0:4]에 struct.pack으로 기록합니다.
        insert 할 때마다 호출해줘야 디스크에도 개수가 저장되겠죠?
        """
        self.data[: Page.HEADER_SIZE] = self.header_struct.pack(
            self.num_rows, self.page_type, self.free_space, self.next_page_id
        )

    def is_full(self) -> bool:
        return True if self.num_rows >= Page.MAX_ROWS else False

    def insert(self, row: Row) -> bool:
        """
        [TODO 3] Offset 계산 공식 수정
        Row가 저장될 위치는 이제 0이 아니라 4(HEADER_SIZE)부터 시작합니다.
        New Offset = HEADER_SIZE + (index * ROW_SIZE)

        그리고 성공 후에 _update_header()를 꼭 호출하세요.
        """
        offset = Page.HEADER_SIZE + (self.num_rows * Page.ROW_SIZE)
        end = offset + Page.ROW_SIZE
        self.data[offset:end] = row.serialize()
        self.num_rows += 1
        self._update_header()
        return True

    def read_at(self, index: int) -> Row:
        """
        [TODO 4] Offset 계산 공식 수정
        New Offset = HEADER_SIZE + (index * ROW_SIZE)
        """
        offset = Page.HEADER_SIZE + (index * Page.ROW_SIZE)
        end = offset + Page.ROW_SIZE
        raw_data = self.data[offset:end]
        return Row.deserialize(raw_data)
