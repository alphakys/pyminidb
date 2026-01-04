from src.pager import Pager
from src.page import Page
from src.row import Row
from src.cursor import Cursor
from typing import Optional

import os


class Table:
    """
    [Logic Layer]
    데이터베이스의 논리적 구조를 관리합니다.
    물리적 저장소(Pager)와 논리적 연산(Cursor) 사이의 조율자 역할을 합니다.
    """

    def __init__(self, filename="mydb.db"):
        # 물리 계층을 다루는 module Pager로부터 filename(path)에 해당하는 데이터 덩어리를 불러온다.
        self.pager = Pager(filename)
        self.file_size = os.path.getsize(filename)
        # Table이 물리 계층에서 읽어온 raw data가 X번 페이지에서 읽어왔다는 것을 표시해줄 메타데이터
        self.page_num = self.file_size // Page.PAGE_SIZE
        print(self.file_size, Page.PAGE_SIZE)
        self.page = self.pager.read_page(self.page_num)

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
        # 데이터베이스 스키마 해석기 현재 구현하지 않았기 때문에 Row가 가지는 column이
        # id, username, email로 현재는! 고정됨

        # [Refactoring Goal]
        # cursor = self.table_end()
        # cursor.save(Row(id, username, email))

        is_success = self.page.insert(Row(int(id), username, email))
        if is_success:
            self.pager.write_page(page_num=self.page_num, page=self.page)
            return True
        else:
            return False

    def execute_select(self):
        # [Refactoring Goal]
        # cursor = self.table_start()
        # while not cursor.end_of_table:
        #     print(cursor.current_cell())
        #     cursor.advance()

        if self.page:
            for i in range(self.page.num_rows):
                print(self.page.read_at(i))
        else:
            print("No data Found")

    def close(self):
        self.pager.close()


if __name__ == "__main__":
    print(Table())
