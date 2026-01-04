from src.pager import Pager
from src.page import Page
from src.row import Row
from src.cursor import Cursor
from typing import Optional


class Table:
    """
    [Logic Layer]
    데이터베이스의 논리적 구조를 관리합니다.
    물리적 저장소(Pager)와 논리적 연산(Cursor) 사이의 조율자 역할을 합니다.
    """

    def __init__(self, filename="mydb.db"):
        # 물리 계층을 다루는 module Pager로부터 filename(path)에 해당하는 데이터 덩어리를 불러온다.
        self.pager = Pager(filename)

        # [Phase 2] Page 0의 헤더에서 전체 Row 개수를 읽어와야 함
        # 임시로 0으로 시작하지만, 곧 수정할 예정
        self.num_rows = 0

    def table_start(self) -> Cursor:
        """테이블의 시작점(0번 Row)을 가리키는 커서를 반환"""
        return Cursor(self, 0)

    def table_end(self) -> Cursor:
        """
        테이블의 끝(마지막 Row의 다음 칸)을 가리키는 커서를 반환
        Insert는 항상 여기서 일어납니다.
        """
        return Cursor(self, self.num_rows)

    def execute_insert(self, id: int, username: str, email: str) -> bool:
        # [Refactoring Goal]
        # cursor = self.table_end()
        # cursor.save(Row(id, username, email))

        # [Legacy Logic - For Compatibility during migration]
        curr_page: Page = self.pager.read_page(0)
        if not curr_page:
            curr_page = Page()

        is_success = curr_page.insert(Row(int(id), username, email))
        if is_success:
            self.pager.write_page(page_num=0, page=curr_page)
            self.num_rows += 1
            return True
        else:
            return False

    def execute_select(self):
        # [Refactoring Goal]
        # cursor = self.table_start()
        # while not cursor.end_of_table:
        #     print(cursor.current_cell())
        #     cursor.advance()

        # [Legacy Logic]
        curr_page = self.pager.read_page(page_num=0)
        if curr_page:
            for i in range(curr_page.num_rows):
                print(curr_page.read_at(i))
        else:
            print("No data Found")

    def close(self):
        self.pager.close()
