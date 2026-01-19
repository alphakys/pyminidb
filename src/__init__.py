"""
PyMiniDB Core Package

이 패키지는 PyMiniDB의 핵심 데이터베이스 엔진 컴포넌트를 포함합니다.

Modules:
    row: Row 데이터 구조
    page: Page 관리 (Leaf/Internal)
    pager: Disk I/O 관리자
    node: B+Tree Node 직렬화
    cursor: 데이터 순회 커서
    table: 테이블 조율자
    btree: B+Tree 삽입/Split 관리자
"""

__version__ = "0.4.0"  # Phase 4: B+Tree Integration
__all__ = [
    "Row",
    "Page",
    "PageType",
    "Pager",
    "BTreeNode",
    "Cursor",
    "Table",
    "BTreeManager",
]

# 편의를 위한 import (선택사항)
from .row import Row
from .page import Page, PageType
from .pager import Pager
from .node import BTreeNode
from .cursor import Cursor
from .table import Table
from .btree import BTreeManager
