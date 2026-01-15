import pathlib
import os

from src.page import Page, PageType
from io import BufferedRandom
from typing import Optional, Union


class Pager:
    """
    [Phase 3] Disk Persistence
    파일 시스템과 직접 통신하며 Page 단위로 데이터를 읽고 씁니다.
    """

    def __init__(self, filename: str):
        self.file_path: pathlib.Path = pathlib.Path(filename)
        # 1. 파일이 존재하는지 확인 (os.path.exists)
        # 2. 없으면 빈 파일 생성 ('wb' 모드로 열었다 닫기)
        # 3. 'rb+' 모드로 파일 열어서 self.file에 저장
        if not self.file_path.exists():
            with self.file_path.open("wb"):
                pass

        self.file: BufferedRandom = self.file_path.open("rb+")

        # [Step 4.1.3] 현재 파일의 페이지 개수 계산
        file_size = self.file_path.stat().st_size
        if file_size % Page.PAGE_SIZE != 0:
            # 경고: 파일 크기가 4KB 배수가 아님 (손상 가능성)
            # 여기서는 일단 내림 혹은 올림 처리가 필요하나, 단순하게 처리
            pass
        self.page_count: int = file_size // Page.PAGE_SIZE

    def get_new_page_id(self) -> int:
        """
        [Step 4.1.3] 새로운 페이지 ID를 할당합니다.

        Disk에 공간을 바로 확보하지는 않고, 논리적인 ID만 발급합니다.
        실제 파일 크기 증가는 write_page()가 호출될 때 일어납s.

        Returns:
            int: 새로 할당된 PID
        """
        pid = self.page_count
        self.page_count += 1
        return pid

    def read_page(self, page_index: int) -> Page:
        """
        파일에서 특정 페이지를 읽어옵니다.
        """
        if page_index >= self.page_count:
            # 아직 생성되지 않은 페이지 접근 시 빈 페이지 반환
            # (B+Tree 구현 시 빈 노드 필요할 때 유용)
            return Page()

        self.file.seek(page_index * Page.PAGE_SIZE)
        buffered_data: bytes = self.file.read(Page.PAGE_SIZE)

        if buffered_data:
            return Page(buffered_data)
        else:
            return Page()

    def write_page(self, page_index: int, page: Page):
        """
        데이터를 파일에 저장합니다.
        """
        self.file.seek(page_index * Page.PAGE_SIZE)
        self.file.write(page.data)
        self.file.flush()

        # [Step 4.1.3] 만약 새로 쓴 페이지가 범위를 넘어갔다면 page_count 업데이트
        if page_index >= self.page_count:
            self.page_count = page_index + 1

    def close(self):
        if self.file:
            self.file.close()
