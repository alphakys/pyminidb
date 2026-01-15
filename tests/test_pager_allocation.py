"""
Step 4.1.3 검증: Pager 페이지 할당 테스트
"""

import sys
import os
import shutil
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.pager import Pager
from src.page import Page, PageType

TEST_DB = "test_allocation.db"


def setup_fresh_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    return TEST_DB


def test_pager_allocation():
    print("=" * 60)
    print("Step 4.1.3: Pager Page Allocation 검증")
    print("=" * 60)

    db_path = setup_fresh_db()

    # 1. 빈 파일에서 시작
    print("\n[Test 1] 초기 상태 확인")
    pager = Pager(db_path)
    assert pager.page_count == 0
    print(f"✅ 초기 page_count: {pager.page_count}")

    # 2. PID 할당 (Lazy Allocation)
    print("\n[Test 2] PID 할당 (get_new_page_id)")
    pid1 = pager.get_new_page_id()
    pid2 = pager.get_new_page_id()
    pid3 = pager.get_new_page_id()

    print(f"Allocated PIDs: {pid1}, {pid2}, {pid3}")
    assert pid1 == 0
    assert pid2 == 1
    assert pid3 == 2
    assert pager.page_count == 3
    print("✅ PID 순차 할당 성공")

    # 3. 파일 크기 확인 (아직 Write 안 함)
    # 주의: get_new_page_id는 메모리상 카운트만 늘림. 실제 파일은 아직 0바이트여야 함.
    file_size = os.path.getsize(db_path)
    print(f"Current File Size: {file_size} bytes")
    assert file_size == 0
    print("✅ Lazy Allocation 확인 (파일 크기 0)")

    # 4. Write Page (Persistence)
    # PID 2번(마지막)에 데이터를 씀 -> 파일이 3개 페이지 크기로 늘어나야 함
    print("\n[Test 3] Write Page & Persistence")
    page = Page(page_type=PageType.LEAF)
    # 식별을 위해 데이터 조금 씀 (Header 이후 Body 영역에)
    # Header가 손상되지 않도록 주의! Offset 20부터 작성
    page.data[20:24] = b"\xbe\xef\xca\xfe"
    page._update_header()  # [Fix] Header 정보를 data에 반영해야 함!

    pager.write_page(2, page)

    expected_size = 3 * Page.PAGE_SIZE  # 12KB
    actual_size = os.path.getsize(db_path)
    print(f"Expected Size: {expected_size}, Actual: {actual_size}")
    assert actual_size == expected_size
    print("✅ 파일 자동 확장 확인")

    pager.close()

    # 5. 재시작 후 상태 복원
    print("\n[Test 4] 재시작 후 page_count 복원")
    new_pager = Pager(db_path)
    print(f"Restored page_count: {new_pager.page_count}")
    assert new_pager.page_count == 3

    # PID 2번 데이터 확인
    loaded_page = new_pager.read_page(2)
    assert loaded_page.data[20:24] == b"\xbe\xef\xca\xfe"
    print("✅ 데이터 유지 확인")

    new_pager.close()

    # 정리
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

    print("\n" + "=" * 60)
    print("🎉 Pager Allocation 테스트 통과!")
    print("=" * 60)


if __name__ == "__main__":
    test_pager_allocation()
