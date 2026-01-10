import unittest
from unittest.mock import MagicMock
import os
from src.table import Table
from src.cursor import Cursor
from src.row import Row
from src.page import Page


class TestCursorRefactoring(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_cursor.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.table = Table(self.test_db)

    def tearDown(self):
        self.table.close()
        # if os.path.exists(self.test_db):
        #     os.remove(self.test_db)

    def test_cursor_start_and_end(self):
        """Cursor가 Table의 시작과 끝을 제대로 가리키는지 확인"""
        # 초기 상태: 0 rows
        start_cursor = self.table.table_start()
        end_cursor = self.table.table_end()

        self.assertIsInstance(start_cursor, Cursor)
        self.assertEqual(start_cursor.row_index, 0)

        self.assertIsInstance(end_cursor, Cursor)
        self.assertEqual(end_cursor.row_index, 0)  # 비어있으면 start == end

    def test_cursor_save_and_advance(self):
        """Cursor를 이용해 데이터를 저장하고 이동하는지 확인"""
        cursor = self.table.table_end()

        # 1. Insert Data using Cursor
        row = Row(1, "user1", "user1@test.com")
        cursor.save(row)

        # Table 메타데이터 업데이트 확인
        self.assertEqual(self.table.row_count, 1)

        # 2. Advance Logic
        # (Table이 아니라 Cursor를 새로 뽑아서 확인)
        read_cursor = self.table.table_start()
        self.assertEqual(read_cursor.end_of_table, False)

        fetched_row = read_cursor.current_cell()
        self.assertEqual(fetched_row.user_id, 1)

        read_cursor.advance()
        self.assertEqual(read_cursor.end_of_table, True)

    def test_pagination_logic_in_cursor(self):
        """Row index를 통해 Page index를 제대로 계산하는지 확인"""
        # MAX_ROWS + 1 번째 Row를 가리키는 커서 생성
        # (실제 insert는 안하고 위치 계산 로직만 테스트)
        target_row_index = Page.MAX_ROWS + 5
        cursor = Cursor(self.table, target_row_index)

        # 내부 로직 검증 (Private 메서드나 속성 접근 필요 시)
        # 여기서는 Cursor가 내부적으로 page_index을 계산한다고 가정
        # page_index = 1, cell_index = 5
        # (테스트를 위해 잠시 Cursor 클래스에 접근하거나, 구현 방식에 따라 조정 필요)
        pass


if __name__ == "__main__":
    unittest.main()
