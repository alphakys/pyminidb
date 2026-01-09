import pathlib
import os

from src.page import Page
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

    def read_page(self, page_index: int) -> Page:
        """
        [TODO 2] 파일에서 특정 페이지를 읽어옵니다.
        1. 페이지가 파일 범위를 벗어나는지 확인 (Optional)
        2. seek()로 위치 이동 (page_index * PAGE_SIZE)
        3. read(PAGE_SIZE)로 바이트 읽기
        4. 읽은 데이터가 없으면 빈 Page 반환
        5. 있으면 Page 객체에 데이터 채워서 반환
        """
        self.file.seek(page_index * Page.PAGE_SIZE)
        buffered_data: bytes = self.file.read(Page.PAGE_SIZE)

        if buffered_data:
            return Page(buffered_data)
        else:
            return Page()

    def write_page(self, page_index: int, page: Page):
        """
        [TODO 3] 데이터를 파일에 저장합니다.
        1. seek()로 위치 이동
        2. write()로 page.data 쓰기
        3. flush()로 동기화
        """
        self.file.seek(page_index * Page.PAGE_SIZE)
        self.file.write(page.data)
        self.file.flush()

    def close(self):
        if self.file:
            self.file.close()
