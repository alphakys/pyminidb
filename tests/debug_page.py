"""
디버깅 헬퍼: Page 내용 출력
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.page import Page, PageType
from src.row import Row


def print_page_rows(page: Page, page_name: str = "Page"):
    """
    Page 내의 모든 Row를 출력 (row_count 기준 + 그 이후 garbage도 확인)
    """
    print(f"\n{'=' * 60}")
    print(f"{page_name} Analysis")
    print(f"{'=' * 60}")
    print(f"Type: {page.page_type.name}")
    print(f"Row Count: {page.row_count}")
    print(f"Max Rows: {Page.MAX_ROWS}")
    print(f"\nValid Rows (0 ~ row_count-1):")
    print("-" * 60)

    for i in range(page.row_count):
        try:
            row = page.read_at(i)
            print(
                f"  [{i}] user_id={row.user_id:3d}, name={row.username:10s}, email={row.email}"
            )
        except Exception as e:
            print(f"  [{i}] ERROR: {e}")

    # Garbage 영역 체크
    print(f"\nGarbage Check (row_count ~ MAX_ROWS-1):")
    print("-" * 60)

    has_garbage = False
    for i in range(page.row_count, min(page.row_count + 5, Page.MAX_ROWS)):
        try:
            # Header 이후 데이터 영역 직접 확인
            offset = Page.HEADER_SIZE + (i * Page.ROW_SIZE)
            end = offset + Page.ROW_SIZE
            raw = bytes(page.data[offset:end])

            # 모두 0이면 깨끗함
            if raw == b"\x00" * Page.ROW_SIZE:
                print(f"  [{i}] ✅ Clean (all zeros)")
            else:
                # Garbage 발견!
                has_garbage = True
                try:
                    row = Row.deserialize(raw)
                    print(
                        f"  [{i}] ⚠️  GARBAGE: user_id={row.user_id}, name={row.username}"
                    )
                except:
                    print(f"  [{i}] ⚠️  GARBAGE: (corrupted data)")
        except Exception as e:
            print(f"  [{i}] ERROR: {e}")

    if not has_garbage and page.row_count < Page.MAX_ROWS:
        print(f"  ✅ No garbage found (clean)")

    print("=" * 60)


if __name__ == "__main__":
    # 간단한 테스트
    page = Page(page_type=PageType.LEAF)

    # Row 추가
    for i in range(4):
        row = Row((i + 1) * 10, f"user{i}", f"user{i}@test.com")
        page.write_at(row)

    print_page_rows(page, "Test Page (Before Split)")

    # row_count만 줄이기 (garbage 남김)
    page.row_count = 2
    page._update_header()

    print_page_rows(page, "Test Page (After Simulated Split - WITH GARBAGE)")
