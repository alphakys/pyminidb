from src.page import Page
from src.row import Row
from typing import TYPE_CHECKING

# Avoid circular import
if TYPE_CHECKING:
    from src.table import Table


class Cursor:
    """
    Cursor: Table 내 특정 위치(row_index)를 추적하는 포인터

    역할:
    - row_index을 (page_index, cell_index)으로 변환
    - 현재 위치의 데이터 읽기/쓰기
    - 테이블 순회 (advance)

    핵심 개념:
    - Cursor는 단일 Page에 갇히지 않음
    - 필요시 자동으로 Page를 전환하며 전체 테이블을 순회
    """

    def __init__(self, table: "Table", row_index: int):
        """
        Cursor 생성자

        Args:
            table: 이 Cursor가 속한 Table 인스턴스
            row_index: 현재 가리키는 Row 번호 (0-based)

        주의:
            - table은 Pager에 접근하기 위해 필요
            - row_index >= table.row_count 이면 end_of_table=True
        """
        self.table = table
        self.row_index: int = row_index
        self.end_of_table: bool = row_index >= table.row_count

    def _get_page_location(self) -> tuple[int, int]:
        """
        row_index을 (page_index, cell_index)으로 변환

        Returns:
            (page_index, cell_index): 페이지 번호와 페이지 내 셀 번호

        공식:
            page_index = row_index // MAX_ROWS
            cell_index = row_index % MAX_ROWS

        예시:
            row_index=0   → (0, 0)   # Page 0, Cell 0
            row_index=91  → (0, 91)  # Page 0, Cell 91
            row_index=92  → (1, 0)   # Page 1, Cell 0 (경계 넘김!)
            row_index=184 → (2, 0)   # Page 2, Cell 0
        """
        return (self.row_index // Page.MAX_ROWS, self.row_index % Page.MAX_ROWS)

    def current_cell(self) -> Row:
        """
        현재 Cursor 위치의 Row를 반환

        Returns:
            Row: 현재 위치의 Row 객체

        Raises:
            RuntimeError: end_of_table일 때 호출 시

        동작:
            1. _get_page_location()으로 (page_index, cell_index) 계산
            2. table.pager.read_page(page_index)으로 Page 로드
            3. page.read_at(cell_index)으로 Row 읽기

        중요:
            - 이 메서드가 호출될 때 Page가 로드됨 (Lazy Loading)
            - Pager가 캐싱을 지원하면 성능 향상
        """
        if self.end_of_table:
            raise RuntimeError("End of Table")

        page_idx, cell_idx = self._get_page_location()
        curr_page = self.table.pager.read_page(page_index=page_idx)
        return curr_page.read_at(row_index=cell_idx)

    def advance(self):
        """
        Cursor를 다음 Row로 이동

        동작:
            1. row_index += 1
            2. row_index >= table.row_count 이면 end_of_table = True
        """
        self.row_index += 1
        if self.row_index >= self.table.row_count:
            self.end_of_table = True

    def save(self, row: Row):
        """
        현재 Cursor 위치에 Row를 저장

        Args:
            row: 저장할 Row 객체

        Raises:
            RuntimeError: Page가 꽉 찼을 때 (이론적으로는 발생 안 해야 함)

        동작:
            1. _get_page_location()으로 (page_index, cell_index) 계산
            2. table.pager.read_page(page_index)으로 Page 로드
                - Page가 없으면(None) 새 Page() 생성
            3. page.insert(row)로 Row 삽입
            4. table.pager.write_page(page_index, page)로 디스크에 기록

        주의:
            - Table.row_count가 정확히 관리되면 Page가 꽉 차는 일 없음
            - row_index = table.row_count일 때 호출됨 (끝에 추가)
        """
        page_idx = self._get_page_location()[0]
        curr_page = self.table.pager.read_page(page_index=page_idx)
        print(row)
        if curr_page.is_full():
            raise RuntimeError(f"Page {page_idx} is full! This should not happen.")

        curr_page.write_at(row=row)
        self.table.pager.write_page(page_index=page_idx, page=curr_page)
        self.table.row_count += 1
        self.row_index += 1
