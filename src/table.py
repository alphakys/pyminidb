from src.pager import Pager
from src.page import Page, PageType
from src.row import Row
from src.cursor import Cursor
from src.node import BTreeNode
import os
import bisect


class Table:
    """
    Table: 논리적 데이터베이스 조율자 (Coordinator)

    책임:
    1. 메타데이터 관리 (전체 Row 개수)
    2. Cursor 생성 (Factory)
    3. 고수준 연산 제공 (insert, select)

    중요:
    - Table은 Page를 직접 다루지 않음
    - 모든 물리적 작업은 Cursor에게 위임
    """

    def __init__(self, filename: str = "mydb.db"):
        """
        Table 생성자

        Args:
            filename: 데이터베이스 파일 경로

        동작:
            1. Pager 생성
            2. 파일 크기를 기반으로 row_count 복구
                - 파일이 없으면 row_count = 0
                - 파일이 있으면:
                  a. page_count = file_size // PAGE_SIZE
                  b. 마지막 페이지 로드
                  c. row_count = (page_count - 1) * MAX_ROWS + last_page.row_count

        주의:
            - 파일이 없으면 Pager가 자동으로 생성
            - row_count는 항상 정확해야 함 (Cursor가 의존)
        """
        self.pager = Pager(filename)

        # [Step 4.2] B+Tree Root Page ID (기본값: 0)
        self.root_page_id = 0

        if self.pager.page_count == 0:
            self.last_page_index = 0
            self.row_count = 0
        else:
            self.last_page_index = self.pager.page_count - 1
            # 테이블에 존재하는 모든 row의 총 개수
            self.row_count = (
                (self.pager.page_count - 1) * Page.MAX_ROWS
            ) + self.pager.read_page(self.last_page_index).row_count

    def table_start(self) -> Cursor:
        """
        테이블의 첫 번째 Row를 가리키는 Cursor 반환

        Returns:
            Cursor: row_index=0인 Cursor

        사용 예:
            cursor = table.table_start()
            while not cursor.end_of_table:
                print(cursor.current_cell())
                cursor.advance()
        """
        return Cursor(self, row_index=0)

    def table_end(self) -> Cursor:
        """
        테이블의 끝(삽입 위치)을 가리키는 Cursor 반환

        Returns:
            Cursor: row_index=self.row_count인 Cursor

        사용 예:
            cursor = table.table_end()
            cursor.save(Row(1, "alice", "alice@test.com"))

        주의:
            - 이 Cursor는 end_of_table=True 상태
            - save() 호출 후 table.row_count를 증가시켜야 함
        """
        return Cursor(self, row_index=self.row_count)

    def find_leaf(self, key: int) -> int:
        """
        [Step 4.2] 주어진 키가 존재할 Leaf Page의 PID를 반환

        Args:
            key: 검색할 키

        Returns:
            int: Leaf Page ID

        알고리즘:
            1. Root Page 로드 (self.root_page_id)
            2. while page.is_leaf == False:
                a. keys, pids = page.read_internal_node()
                b. bisect.bisect_right(keys, key)로 구간 찾기
                c. pids[index] 페이지로 이동
            3. current_page_id 반환
        """
        page = self.pager.read_page(self.root_page_id)
        pid = self.root_page_id
        while not page.is_leaf:
            keys, childs = page.read_internal_node()
            idx = bisect.bisect_right(keys, key)
            pid = childs[idx]
            page = self.pager.read_page(pid)

        return pid

    def execute_insert(self, id: int, username: str, email: str) -> bool:
        """
        Row 삽입 연산

        Args:
            id: Primary Key (정수)
            username: 사용자 이름
            email: 이메일

        Returns:
            bool: 삽입 성공 여부

        동작:
            1. Row 객체 생성
            2. table_end()로 삽입 위치 Cursor 생성
            3. cursor.save(row)로 저장
            4. self.row_count += 1 (메타데이터 갱신)

        중요:
            - Page 전환 로직은 Cursor가 처리
            - Table은 row_count만 관리

        예시:
            table.execute_insert(1, "alice", "alice@test.com")
            # → Cursor가 알아서 올바른 Page에 저장
        """
        # 🔧 Row 객체 생성
        row = Row(id, username, email)

        # 끝 위치 Cursor 생성
        end_cell = self.table_end()

        # Row 저장 (Cursor.save가 row_count 증가 처리)
        end_cell.save(row)

        return True

    def execute_select(self):
        """
        전체 Row 조회 연산

        동작:
            1. table_start()로 시작 Cursor 생성
            2. while not cursor.end_of_table:
                a. print(cursor.current_cell())
                b. cursor.advance()

        중요:
            - Page 전환은 Cursor.current_cell()이 자동 처리
            - Table은 반복문만 관리

        예시:
            table.execute_select()
            # → 모든 Row 출력 (여러 Page 자동 순회)
        """
        cur = self.table_start()
        while not cur.end_of_table:
            print(cur.current_cell())
            cur.advance()

    def close(self):
        """
        데이터베이스 연결 종료

        동작:
            - Pager.close() 호출하여 파일 핸들 닫기
        """
        self.pager.close()
