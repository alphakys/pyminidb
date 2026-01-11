"""
Level 3.2: Leaf Split (B+Tree의 핵심!)

목표:
1. Leaf가 꽉 찼을 때 2개로 분할
2. 중간 키를 Parent에 올림 (promote)
3. Sibling 포인터 재연결

핵심 개념:
- "Split" = 1개 → 2개로 나누기
- "Promote" = 중간 키를 부모에게 올리기
- "Sibling" = 분할된 Leaf 연결
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import bisect


@dataclass
class BPlusNode:
    is_leaf: bool
    keys: List[int] = field(default_factory=list)
    children: Optional[List["BPlusNode"]] = None
    values: Optional[List] = None
    next: Optional["BPlusNode"] = None


def print_tree(node: BPlusNode, level: int = 0):
    """트리 시각화"""
    indent = "  " * level
    node_type = "🍃" if node.is_leaf else "🌳"
    print(f"{indent}{node_type} {node.keys}")

    if not node.is_leaf and node.children:
        for child in node.children:
            print_tree(child, level + 1)


# ======================================================================
# Task 3.2.1: split_leaf() - Leaf 분할
# ======================================================================


def split_leaf(leaf: BPlusNode) -> Tuple[int, BPlusNode]:
    """
    꽉 찬 Leaf를 2개로 분할

    Args:
        leaf: 꽉 찬 Leaf 노드 (MAX_KEYS + 1개 키)

    Returns:
        (promote_key, new_leaf):
            - promote_key: 부모에 올릴 키
            - new_leaf: 새로 만든 오른쪽 Leaf

    동작:
        1. 중간 지점 계산 (mid = len(keys) // 2)
        2. 오른쪽 절반으로 new_leaf 생성
        3. 왼쪽 절반만 남기도록 기존 leaf 축소
        4. Sibling 포인터 재연결
        5. promote_key = new_leaf의 첫 번째 키 반환

    예시:
        Before: leaf.keys = [1, 3, 5, 7, 9]  (5개, 넘침!)

        After:
            leaf.keys = [1, 3]           ← 왼쪽
            new_leaf.keys = [5, 7, 9]    ← 오른쪽
            promote_key = 5              ← 부모에 올림

        구조:
            Before: [1,3,5,7,9]
                       ↓ Split at mid=2
            After:  [1,3] | [5,7,9]
                     ↓         ↓
                   Left     Right

    TODO: 아래 코드를 완성하세요!
    """
    # Step 1: 중간 지점 계산
    mid = len(leaf.keys) // 2

    # Step 2: 오른쪽 절반으로 new_leaf 생성
    # TODO: new_leaf를 만드세요
    # 힌트: keys와 values를 슬라이싱 [mid:]
    new_leaf = None

    # Step 3: 왼쪽 절반만 남기도록 기존 leaf 축소
    # TODO: leaf.keys = ?
    # TODO: leaf.values = ?

    # Step 4: Sibling 포인터 재연결
    # TODO: new_leaf.next = ?
    # TODO: leaf.next = ?

    # Step 5: promote_key 계산
    # TODO: promote_key = ?
    promote_key = None

    return promote_key, new_leaf


# ======================================================================
# Task 3.2.2: insert_into_parent() - Parent에 키 삽입
# ======================================================================


def insert_into_parent(
    parent: BPlusNode, promote_key: int, new_child: BPlusNode
) -> None:
    """
    Parent에 promote된 키와 새 자식 추가

    Args:
        parent: Parent (Internal) 노드
        promote_key: 올라온 키
        new_child: 새로 생성된 자식

    동작:
        1. promote_key가 들어갈 위치 찾기 (bisect)
        2. parent.keys에 promote_key 삽입
        3. parent.children에 new_child 삽입 (index+1 위치)

    예시:
        Before:
            parent.keys = [10, 20]
            parent.children = [A, B, C]

        insert_into_parent(parent, 15, D):
            - 15는 10과 20 사이
            - index = 1

        After:
            parent.keys = [10, 15, 20]
            parent.children = [A, B, D, C]
                                    ↑ index+1 위치

    TODO: 아래 코드를 완성하세요!
    """
    # Step 1: 삽입 위치 찾기
    index = None  # TODO: bisect 사용

    # Step 2: keys 삽입
    # TODO

    # Step 3: children 삽입 (index+1)
    # TODO

    pass


# ======================================================================
# Task 3.2.3: insert_with_split() - Split 포함 Insert
# ======================================================================


def insert_with_split(
    root: BPlusNode, key: int, value: str, max_keys: int
) -> BPlusNode:
    """
    Insert with Split 지원

    Args:
        root: 트리의 Root
        key: 삽입할 키
        value: 삽입할 값
        max_keys: 노드당 최대 키 개수

    Returns:
        root: 트리의 Root (변경될 수 있음!)

    동작:
        1. find_leaf()로 Leaf 찾기
        2. Leaf에 (key, value) 삽입 (일단 넘쳐도 OK)
        3. Leaf가 넘쳤으면 split_leaf()
        4. Parent 찾아서 promote_key 삽입
        5. (현재는 Parent가 Root라고 가정)

    주의:
        - 아직 Internal Split은 미구현
        - Root가 Leaf면 새 Root 생성 필요

    TODO: 아래 코드를 완성하세요!
    """
    # Step 1: Leaf 찾기
    if root.is_leaf:
        leaf = root
        parent = None
    else:
        # TODO: find_leaf 사용
        leaf = None
        parent = root  # 간단히 Root를 Parent로 가정

    # Step 2: Leaf에 삽입 (넘쳐도 OK)
    index = bisect.bisect_left(leaf.keys, key)
    leaf.keys.insert(index, key)
    leaf.values.insert(index, value)

    # Step 3: Leaf가 넘쳤나?
    if len(leaf.keys) > max_keys:
        print(f"  → Leaf 넘침! Split 발동 ({len(leaf.keys)} > {max_keys})")

        # Step 4: Split!
        promote_key, new_leaf = split_leaf(leaf)
        print(f"  → Split 완료: promote_key={promote_key}")

        # Step 5: Parent에 삽입
        if parent is None:
            # Root가 Leaf였다면 새 Root 생성
            print("  → 새 Root 생성")
            # TODO: 새 Internal Root 만들기
            # 힌트: keys=[promote_key], children=[leaf, new_leaf]
            new_root = None
            return new_root
        else:
            # Parent에 promote_key 삽입
            insert_into_parent(parent, promote_key, new_leaf)

    return root


# ======================================================================
# 이전 레벨 함수들
# ======================================================================


def find_leaf(root: BPlusNode, key: int) -> BPlusNode:
    """Leaf 찾기"""
    node = root
    while not node.is_leaf:
        index = bisect.bisect_right(node.keys, key)
        node = node.children[index]
    return node


def search(root: BPlusNode, key: int) -> Optional[str]:
    """검색"""
    leaf = find_leaf(root, key)
    if key in leaf.keys:
        index = leaf.keys.index(key)
        return leaf.values[index]
    else:
        return None


# ======================================================================
# 테스트
# ======================================================================

if __name__ == "__main__":
    print("\n🔥 B+Tree Leaf Split 실습\n")

    MAX_KEYS = 2  # Order=3 (작게 설정해서 Split 쉽게 유발)

    # 초기 트리: 단순 Root Leaf
    root = BPlusNode(is_leaf=True, keys=[5], values=["Five"])

    print("[초기 트리]")
    print_tree(root)

    # 삽입 테스트
    test_inserts = [
        (10, "Ten"),
        (15, "Fifteen"),  # 이때 Split 발생!
        (3, "Three"),
        (7, "Seven"),  # 또 Split!
    ]

    print("\n" + "=" * 60)
    print("Insert with Split 테스트")
    print("=" * 60)

    for key, value in test_inserts:
        print(f"\nInsert ({key}, {value})...")
        try:
            root = insert_with_split(root, key, value, MAX_KEYS)
            print_tree(root)
        except Exception as e:
            print(f"⚠️  에러 또는 미구현: {e}")
            import traceback

            traceback.print_exc()
            break

    # 검증
    print("\n" + "=" * 60)
    print("검색 검증")
    print("=" * 60)

    for key, expected in test_inserts:
        result = search(root, key)
        status = "✅" if result == expected else "❌"
        print(f"{status} search({key:2d}) = {result}")

    print("\n" + "=" * 60)
    print("완료 후 다음 단계: Level 3.3 - Internal Split")
    print("=" * 60)
